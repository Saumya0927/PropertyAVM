import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Tuple
import json
import os

np.random.seed(42)
random.seed(42)

class CommercialPropertyDataGenerator:
    def __init__(self, num_properties: int = 10000):
        self.num_properties = num_properties
        self.property_types = ['Office', 'Retail', 'Industrial', 'Multifamily', 'Hotel', 'Mixed-Use']
        self.property_classes = ['A', 'B', 'C']
        self.cities = self._load_cities()
        self.amenities = [
            'parking', 'gym', 'security', 'elevator', 'conference_rooms',
            'cafeteria', 'green_certified', 'ev_charging', 'bike_storage',
            'rooftop_access', 'loading_dock', 'high_speed_internet'
        ]
        
    def _load_cities(self) -> List[Dict]:
        return [
            {'name': 'New York', 'state': 'NY', 'lat': 40.7128, 'lon': -74.0060, 'price_multiplier': 2.5},
            {'name': 'Los Angeles', 'state': 'CA', 'lat': 34.0522, 'lon': -118.2437, 'price_multiplier': 2.2},
            {'name': 'Chicago', 'state': 'IL', 'lat': 41.8781, 'lon': -87.6298, 'price_multiplier': 1.8},
            {'name': 'Houston', 'state': 'TX', 'lat': 29.7604, 'lon': -95.3698, 'price_multiplier': 1.5},
            {'name': 'Phoenix', 'state': 'AZ', 'lat': 33.4484, 'lon': -112.0740, 'price_multiplier': 1.4},
            {'name': 'Philadelphia', 'state': 'PA', 'lat': 39.9526, 'lon': -75.1652, 'price_multiplier': 1.6},
            {'name': 'San Antonio', 'state': 'TX', 'lat': 29.4241, 'lon': -98.4936, 'price_multiplier': 1.3},
            {'name': 'San Diego', 'state': 'CA', 'lat': 32.7157, 'lon': -117.1611, 'price_multiplier': 2.0},
            {'name': 'Dallas', 'state': 'TX', 'lat': 32.7767, 'lon': -96.7970, 'price_multiplier': 1.6},
            {'name': 'San Jose', 'state': 'CA', 'lat': 37.3382, 'lon': -121.8863, 'price_multiplier': 2.8},
            {'name': 'Austin', 'state': 'TX', 'lat': 30.2672, 'lon': -97.7431, 'price_multiplier': 1.7},
            {'name': 'Seattle', 'state': 'WA', 'lat': 47.6062, 'lon': -122.3321, 'price_multiplier': 2.1},
            {'name': 'Denver', 'state': 'CO', 'lat': 39.7392, 'lon': -104.9903, 'price_multiplier': 1.6},
            {'name': 'Boston', 'state': 'MA', 'lat': 42.3601, 'lon': -71.0589, 'price_multiplier': 2.3},
            {'name': 'Miami', 'state': 'FL', 'lat': 25.7617, 'lon': -80.1918, 'price_multiplier': 1.9},
        ]
    
    def _generate_base_features(self) -> pd.DataFrame:
        data = []
        
        for i in range(self.num_properties):
            city = random.choice(self.cities)
            property_type = random.choice(self.property_types)
            property_class = random.choice(self.property_classes)
            
            year_built = random.randint(1950, 2023)
            current_year = 2024
            age = current_year - year_built
            
            if property_type == 'Office':
                size_range = (5000, 500000)
                floors_range = (1, 50)
                occupancy_range = (0.7, 0.98)
            elif property_type == 'Retail':
                size_range = (2000, 150000)
                floors_range = (1, 4)
                occupancy_range = (0.75, 0.95)
            elif property_type == 'Industrial':
                size_range = (10000, 1000000)
                floors_range = (1, 3)
                occupancy_range = (0.8, 0.98)
            elif property_type == 'Multifamily':
                size_range = (10000, 300000)
                floors_range = (2, 30)
                occupancy_range = (0.85, 0.98)
            elif property_type == 'Hotel':
                size_range = (20000, 400000)
                floors_range = (3, 40)
                occupancy_range = (0.6, 0.9)
            else:  # Mixed-Use
                size_range = (15000, 350000)
                floors_range = (2, 25)
                occupancy_range = (0.75, 0.95)
            
            square_feet = random.randint(*size_range)
            num_floors = random.randint(*floors_range)
            occupancy_rate = random.uniform(*occupancy_range)
            
            if property_class == 'A':
                occupancy_rate = min(occupancy_rate + 0.05, 1.0)
            elif property_class == 'C':
                occupancy_rate = max(occupancy_rate - 0.05, 0.5)
            
            lot_size = square_feet * random.uniform(1.2, 3.0)
            
            num_units = 1
            if property_type == 'Multifamily':
                num_units = int(square_feet / random.uniform(800, 1200))
            elif property_type == 'Office':
                num_units = random.randint(1, max(1, num_floors * 4))
            
            parking_spots = int(square_feet / random.uniform(300, 500))
            
            annual_revenue = self._calculate_revenue(
                property_type, square_feet, occupancy_rate, city['price_multiplier'], property_class
            )
            
            annual_expenses = annual_revenue * random.uniform(0.3, 0.5)
            net_operating_income = annual_revenue - annual_expenses
            
            cap_rate = random.uniform(0.04, 0.08)
            if property_class == 'A':
                cap_rate -= 0.01
            elif property_class == 'C':
                cap_rate += 0.01
            
            distance_to_downtown = random.uniform(0.1, 25.0)
            distance_to_highway = random.uniform(0.1, 10.0)
            distance_to_public_transit = random.uniform(0.1, 5.0)
            
            walk_score = int(np.clip(90 - distance_to_downtown * 3 + random.uniform(-10, 10), 0, 100))
            transit_score = int(np.clip(85 - distance_to_public_transit * 10 + random.uniform(-10, 10), 0, 100))
            
            crime_rate = max(0, random.gauss(50, 20))
            school_rating = min(10, max(1, random.gauss(7, 2)))
            
            property_data = {
                'property_id': f'PROP_{i+1:06d}',
                'property_type': property_type,
                'property_class': property_class,
                'city': city['name'],
                'state': city['state'],
                'latitude': city['lat'] + random.uniform(-0.1, 0.1),
                'longitude': city['lon'] + random.uniform(-0.1, 0.1),
                'year_built': year_built,
                'building_age': age,
                'square_feet': square_feet,
                'lot_size': lot_size,
                'num_floors': num_floors,
                'num_units': num_units,
                'parking_spots': parking_spots,
                'occupancy_rate': occupancy_rate,
                'annual_revenue': annual_revenue,
                'annual_expenses': annual_expenses,
                'net_operating_income': net_operating_income,
                'cap_rate': cap_rate,
                'distance_to_downtown': distance_to_downtown,
                'distance_to_highway': distance_to_highway,
                'distance_to_public_transit': distance_to_public_transit,
                'walk_score': walk_score,
                'transit_score': transit_score,
                'crime_rate': crime_rate,
                'school_rating': school_rating,
                'last_renovation_year': year_built + random.randint(0, max(0, age - 5)) if age > 10 else year_built,
                'energy_efficiency_rating': random.choice(['A', 'B', 'C', 'D', 'E']),
                'flood_zone': random.choice([True, False], p=[0.1, 0.9]),
                'earthquake_zone': random.choice([True, False], p=[0.15, 0.85]),
            }
            
            selected_amenities = random.sample(self.amenities, k=random.randint(3, len(self.amenities)))
            for amenity in self.amenities:
                property_data[f'has_{amenity}'] = amenity in selected_amenities
            
            market_trend = random.uniform(-0.05, 0.15)
            economic_indicator = random.uniform(0.8, 1.2)
            
            property_data['market_trend'] = market_trend
            property_data['economic_indicator'] = economic_indicator
            
            data.append(property_data)
        
        return pd.DataFrame(data)
    
    def _calculate_revenue(self, property_type: str, square_feet: int, 
                          occupancy_rate: float, city_multiplier: float, 
                          property_class: str) -> float:
        base_rate_per_sqft = {
            'Office': 35,
            'Retail': 40,
            'Industrial': 15,
            'Multifamily': 25,
            'Hotel': 45,
            'Mixed-Use': 30
        }
        
        class_multiplier = {'A': 1.3, 'B': 1.0, 'C': 0.8}
        
        base_rate = base_rate_per_sqft.get(property_type, 30)
        annual_revenue = (
            square_feet * 
            base_rate * 
            occupancy_rate * 
            city_multiplier * 
            class_multiplier[property_class] *
            random.uniform(0.9, 1.1)
        )
        
        return annual_revenue
    
    def _calculate_property_value(self, df: pd.DataFrame) -> pd.Series:
        values = []
        
        for _, row in df.iterrows():
            base_value = row['net_operating_income'] / row['cap_rate']
            
            age_factor = 1 - (row['building_age'] * 0.005)
            age_factor = max(0.7, age_factor)
            
            location_factor = (
                (100 - row['distance_to_downtown']) / 100 * 0.3 +
                (row['walk_score'] / 100) * 0.2 +
                (row['transit_score'] / 100) * 0.2 +
                (100 - row['crime_rate']) / 100 * 0.15 +
                (row['school_rating'] / 10) * 0.15
            )
            
            class_factor = {'A': 1.2, 'B': 1.0, 'C': 0.85}[row['property_class']]
            
            amenity_score = sum([row[f'has_{amenity}'] for amenity in self.amenities]) / len(self.amenities)
            amenity_factor = 1 + (amenity_score * 0.1)
            
            market_factor = 1 + row['market_trend']
            economic_factor = row['economic_indicator']
            
            efficiency_factors = {'A': 1.1, 'B': 1.05, 'C': 1.0, 'D': 0.95, 'E': 0.9}
            efficiency_factor = efficiency_factors[row['energy_efficiency_rating']]
            
            risk_factor = 1.0
            if row['flood_zone']:
                risk_factor *= 0.95
            if row['earthquake_zone']:
                risk_factor *= 0.97
            
            noise = random.uniform(0.95, 1.05)
            
            final_value = (
                base_value * 
                age_factor * 
                location_factor * 
                class_factor * 
                amenity_factor * 
                market_factor * 
                economic_factor * 
                efficiency_factor * 
                risk_factor * 
                noise
            )
            
            values.append(max(100000, final_value))
        
        return pd.Series(values)
    
    def generate_dataset(self) -> pd.DataFrame:
        print(f"Generating {self.num_properties} synthetic commercial properties...")
        
        df = self._generate_base_features()
        
        df['property_value'] = self._calculate_property_value(df)
        
        df['price_per_sqft'] = df['property_value'] / df['square_feet']
        df['gross_rent_multiplier'] = df['property_value'] / df['annual_revenue']
        df['debt_coverage_ratio'] = df['net_operating_income'] / (df['property_value'] * 0.7 * 0.05)
        
        last_sale_years_ago = np.random.randint(1, 10, size=len(df))
        df['last_sale_date'] = pd.Timestamp.now() - pd.to_timedelta(last_sale_years_ago * 365, unit='D')
        df['last_sale_price'] = df['property_value'] * np.random.uniform(0.8, 1.0, size=len(df))
        
        df['days_on_market'] = np.random.randint(1, 180, size=len(df))
        df['listing_date'] = pd.Timestamp.now() - pd.to_timedelta(df['days_on_market'], unit='D')
        
        print(f"Dataset generated with {len(df)} properties")
        print(f"Value range: ${df['property_value'].min():,.0f} - ${df['property_value'].max():,.0f}")
        print(f"Average value: ${df['property_value'].mean():,.0f}")
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, output_dir: str = '../data'):
        os.makedirs(output_dir, exist_ok=True)
        
        csv_path = os.path.join(output_dir, 'synthetic_properties.csv')
        df.to_csv(csv_path, index=False)
        print(f"Dataset saved to {csv_path}")
        
        json_path = os.path.join(output_dir, 'synthetic_properties.json')
        df.head(100).to_json(json_path, orient='records', indent=2, date_format='iso')
        print(f"Sample data saved to {json_path}")
        
        stats = {
            'num_properties': len(df),
            'property_types': df['property_type'].value_counts().to_dict(),
            'cities': df['city'].value_counts().to_dict(),
            'value_stats': {
                'min': float(df['property_value'].min()),
                'max': float(df['property_value'].max()),
                'mean': float(df['property_value'].mean()),
                'median': float(df['property_value'].median()),
                'std': float(df['property_value'].std())
            },
            'features': list(df.columns),
            'generated_at': datetime.now().isoformat()
        }
        
        stats_path = os.path.join(output_dir, 'dataset_stats.json')
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Statistics saved to {stats_path}")
        
        return csv_path

if __name__ == "__main__":
    generator = CommercialPropertyDataGenerator(num_properties=10000)
    df = generator.generate_dataset()
    generator.save_dataset(df)
    
    print("\nDataset Summary:")
    print(df.info())
    print("\nFirst 5 properties:")
    print(df[['property_id', 'property_type', 'city', 'square_feet', 'property_value']].head())