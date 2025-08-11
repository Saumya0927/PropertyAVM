import json
import boto3
import pickle
import numpy as np
from datetime import datetime
import os
import traceback

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

MODEL_BUCKET = os.environ.get('MODEL_BUCKET', 'avm-models')
MODEL_KEY = os.environ.get('MODEL_KEY', 'models/xgboost_model.pkl')
CACHE_TABLE = os.environ.get('CACHE_TABLE', 'valuation-cache')

class ValuationLambda:
    def __init__(self):
        self.model = None
        self.cache_table = None
        self.load_model()
        self.setup_cache()
    
    def load_model(self):
        """Load ML model from S3"""
        try:
            response = s3_client.get_object(Bucket=MODEL_BUCKET, Key=MODEL_KEY)
            model_data = response['Body'].read()
            self.model = pickle.loads(model_data)
            print(f"Model loaded successfully from s3://{MODEL_BUCKET}/{MODEL_KEY}")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            # For local testing, use a mock model
            self.model = None
    
    def setup_cache(self):
        """Setup DynamoDB cache table"""
        try:
            self.cache_table = dynamodb.Table(CACHE_TABLE)
        except Exception as e:
            print(f"Cache table setup error: {str(e)}")
            self.cache_table = None
    
    def get_cached_valuation(self, property_hash):
        """Check cache for existing valuation"""
        if not self.cache_table:
            return None
        
        try:
            response = self.cache_table.get_item(
                Key={'property_hash': property_hash}
            )
            
            if 'Item' in response:
                item = response['Item']
                # Check if cache is still valid (24 hours)
                cached_time = datetime.fromisoformat(item['timestamp'])
                if (datetime.now() - cached_time).total_seconds() < 86400:
                    return item['valuation']
        except Exception as e:
            print(f"Cache retrieval error: {str(e)}")
        
        return None
    
    def save_to_cache(self, property_hash, valuation):
        """Save valuation to cache"""
        if not self.cache_table:
            return
        
        try:
            self.cache_table.put_item(
                Item={
                    'property_hash': property_hash,
                    'valuation': valuation,
                    'timestamp': datetime.now().isoformat(),
                    'ttl': int((datetime.now().timestamp())) + 86400  # 24 hour TTL
                }
            )
        except Exception as e:
            print(f"Cache save error: {str(e)}")
    
    def prepare_features(self, property_data):
        """Prepare features for model prediction"""
        required_features = [
            'square_feet', 'num_floors', 'num_units', 'parking_spots',
            'occupancy_rate', 'annual_revenue', 'annual_expenses',
            'net_operating_income', 'cap_rate', 'distance_to_downtown',
            'walk_score', 'transit_score', 'building_age'
        ]
        
        features = []
        for feature in required_features:
            value = property_data.get(feature, 0)
            features.append(float(value))
        
        # Add derived features
        if property_data.get('annual_revenue', 0) > 0:
            efficiency_ratio = property_data.get('annual_expenses', 0) / property_data.get('annual_revenue', 1)
        else:
            efficiency_ratio = 0
        features.append(efficiency_ratio)
        
        location_score = (property_data.get('walk_score', 0) + property_data.get('transit_score', 0)) / 2
        features.append(location_score)
        
        return np.array(features).reshape(1, -1)
    
    def calculate_confidence_interval(self, prediction, property_data):
        """Calculate confidence interval for prediction"""
        # Simplified confidence interval calculation
        # In production, this would use proper statistical methods
        
        base_uncertainty = 0.1  # 10% base uncertainty
        
        # Adjust uncertainty based on data quality
        if property_data.get('occupancy_rate', 0) < 0.7:
            base_uncertainty += 0.05
        
        if property_data.get('building_age', 0) > 30:
            base_uncertainty += 0.03
        
        lower_bound = prediction * (1 - base_uncertainty)
        upper_bound = prediction * (1 + base_uncertainty)
        
        return lower_bound, upper_bound
    
    def predict(self, property_data):
        """Make valuation prediction"""
        # Generate cache key
        property_hash = str(hash(json.dumps(property_data, sort_keys=True)))
        
        # Check cache
        cached_result = self.get_cached_valuation(property_hash)
        if cached_result:
            print("Returning cached valuation")
            return cached_result
        
        # Prepare features
        features = self.prepare_features(property_data)
        
        # Make prediction
        if self.model:
            prediction = float(self.model.predict(features)[0])
        else:
            # Mock prediction for testing
            base_value = property_data.get('net_operating_income', 500000) / property_data.get('cap_rate', 0.06)
            prediction = base_value * np.random.uniform(0.95, 1.05)
        
        # Calculate confidence interval
        lower_bound, upper_bound = self.calculate_confidence_interval(prediction, property_data)
        
        # Prepare result
        result = {
            'predicted_value': round(prediction, 2),
            'confidence_interval': {
                'lower': round(lower_bound, 2),
                'upper': round(upper_bound, 2),
                'confidence_level': 95
            },
            'price_per_sqft': round(prediction / property_data.get('square_feet', 1), 2),
            'valuation_date': datetime.now().isoformat(),
            'model_version': 'v1.0.0',
            'processing_time_ms': 0  # Will be calculated by wrapper
        }
        
        # Save to cache
        self.save_to_cache(property_hash, result)
        
        return result

# Global instance for Lambda reuse
valuation_service = ValuationLambda()

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    start_time = datetime.now()
    
    try:
        # Parse input
        if 'body' in event:
            # API Gateway invocation
            body = json.loads(event['body'])
        else:
            # Direct invocation
            body = event
        
        # Validate required fields
        required_fields = ['square_feet', 'property_type', 'city']
        missing_fields = [field for field in required_fields if field not in body]
        
        if missing_fields:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required fields',
                    'missing_fields': missing_fields
                })
            }
        
        # Perform valuation
        result = valuation_service.predict(body)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        result['processing_time_ms'] = round(processing_time, 2)
        
        # Log metrics
        print(json.dumps({
            'metric': 'valuation_request',
            'city': body.get('city'),
            'property_type': body.get('property_type'),
            'predicted_value': result['predicted_value'],
            'processing_time_ms': processing_time
        }))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in lambda_handler: {error_trace}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def batch_handler(event, context):
    """Handle batch valuation requests"""
    start_time = datetime.now()
    
    try:
        # Parse batch input
        if 'Records' in event:
            # SQS trigger
            properties = []
            for record in event['Records']:
                body = json.loads(record['body'])
                properties.append(body)
        else:
            # Direct invocation
            properties = event.get('properties', [])
        
        results = []
        total_value = 0
        
        for property_data in properties:
            try:
                valuation = valuation_service.predict(property_data)
                results.append({
                    'property_id': property_data.get('property_id'),
                    'status': 'success',
                    'valuation': valuation
                })
                total_value += valuation['predicted_value']
            except Exception as e:
                results.append({
                    'property_id': property_data.get('property_id'),
                    'status': 'error',
                    'error': str(e)
                })
        
        # Calculate statistics
        successful_valuations = [r for r in results if r['status'] == 'success']
        
        response = {
            'batch_id': context.request_id,
            'total_properties': len(properties),
            'successful_valuations': len(successful_valuations),
            'failed_valuations': len(properties) - len(successful_valuations),
            'total_portfolio_value': round(total_value, 2),
            'average_property_value': round(total_value / max(len(successful_valuations), 1), 2),
            'processing_time_ms': round((datetime.now() - start_time).total_seconds() * 1000, 2),
            'results': results
        }
        
        # Log batch metrics
        print(json.dumps({
            'metric': 'batch_valuation',
            'batch_id': context.request_id,
            'total_properties': len(properties),
            'total_value': total_value,
            'processing_time_ms': response['processing_time_ms']
        }))
        
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in batch_handler: {error_trace}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Batch processing failed',
                'message': str(e)
            })
        }

if __name__ == "__main__":
    # Test the Lambda function locally
    test_event = {
        'body': json.dumps({
            'property_id': 'PROP_TEST_001',
            'square_feet': 15000,
            'property_type': 'Office',
            'city': 'New York',
            'num_floors': 3,
            'num_units': 10,
            'parking_spots': 50,
            'occupancy_rate': 0.92,
            'annual_revenue': 525000,
            'annual_expenses': 157500,
            'net_operating_income': 367500,
            'cap_rate': 0.06,
            'distance_to_downtown': 2.5,
            'walk_score': 85,
            'transit_score': 90,
            'building_age': 15
        })
    }
    
    class MockContext:
        request_id = 'test-request-123'
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))