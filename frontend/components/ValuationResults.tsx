'use client'

import { motion } from 'framer-motion'
import { 
  CurrencyDollarIcon, 
  ChartBarIcon, 
  ClockIcon,
  ShieldCheckIcon,
  ArrowTrendingUpIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline'

interface ValuationResultsProps {
  result: {
    predicted_value: number
    confidence_interval: {
      lower: number
      upper: number
      confidence_level: number
      uncertainty_percentage?: number
    }
    price_per_sqft: number
    valuation_date: string
    model_version: string
    processing_time_ms?: number
    cached?: boolean
    ensemble_info?: {
      models_used: number
      model_agreement: number
    }
  }
  propertyData?: any
}

export default function ValuationResults({ result, propertyData }: ValuationResultsProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  // Use backend's calculated uncertainty percentage if available, otherwise calculate from bounds
  console.log('=== VALUATION RESULTS DEBUG ===')
  console.log('Full result object:', result)
  console.log('Confidence interval:', result.confidence_interval)
  console.log('Backend uncertainty_percentage:', result.confidence_interval.uncertainty_percentage)
  console.log('Confidence interval bounds:', {
    lower: result.confidence_interval.lower,
    upper: result.confidence_interval.upper,
    predicted_value: result.predicted_value
  })
  
  // Calculate total range percentage from bounds
  const totalRangePercentage = ((result.confidence_interval.upper - result.confidence_interval.lower) / result.predicted_value) * 100
  console.log('Calculated total range from bounds:', totalRangePercentage)
  
  // Convert to plus/minus percentage (half of total range)
  const calculatedPlusMinusPercentage = totalRangePercentage / 2
  
  // Use backend's plus/minus percentage if available, otherwise use calculated plus/minus
  const confidencePercentage = result.confidence_interval.uncertainty_percentage ?? calculatedPlusMinusPercentage
  
  console.log('Backend uncertainty (plus/minus):', result.confidence_interval.uncertainty_percentage)
  console.log('Calculated plus/minus percentage:', calculatedPlusMinusPercentage)
  console.log('Final displayed percentage (plus/minus):', confidencePercentage)
  console.log('Final uncertainty percentage used:', confidencePercentage)
  console.log('=== END DEBUG ===')
  
  // Show alert with the uncertainty value for debugging
  if (typeof window !== 'undefined' && confidencePercentage > 3) {
    console.warn(`WARNING: High uncertainty detected: ${confidencePercentage.toFixed(1)}%`)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-2xl shadow-xl p-8"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Valuation Results</h2>
        <div className="flex items-center gap-2">
          {result.cached && (
            <span className="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full text-xs font-medium">
              Cached
            </span>
          )}
          <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-medium">
            {result.model_version}
          </span>
        </div>
      </div>

      {/* Main Valuation */}
      <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6 mb-6">
        <div className="flex items-center gap-3 mb-2">
          <CurrencyDollarIcon className="w-8 h-8 text-primary-600" />
          <span className="text-lg font-medium text-gray-700">Estimated Value</span>
        </div>
        <div className="text-4xl font-bold text-primary-600 mb-2">
          {formatCurrency(result.predicted_value)}
        </div>
        <div className="text-sm text-gray-600">
          {formatCurrency(result.price_per_sqft)} per sq ft
        </div>
      </div>

      {/* Confidence Interval */}
      <div className="bg-gray-50 rounded-xl p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <ShieldCheckIcon className="w-5 h-5 text-gray-600" />
          <span className="font-medium text-gray-700">
            {result.confidence_interval.confidence_level}% Confidence Interval
          </span>
        </div>
        
        <div className="relative">
          <div className="flex justify-between items-end mb-2">
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">Lower Bound</div>
              <div className="text-lg font-semibold text-gray-700">
                {formatCurrency(result.confidence_interval.lower)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-500 mb-1">Upper Bound</div>
              <div className="text-lg font-semibold text-gray-700">
                {formatCurrency(result.confidence_interval.upper)}
              </div>
            </div>
          </div>
          
          {/* Visual Range Bar */}
          <div className="relative h-3 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="absolute h-full bg-gradient-to-r from-primary-400 to-primary-600 rounded-full"
              style={{
                left: '20%',
                width: '60%'
              }}
            />
            <div 
              className="absolute h-full w-1 bg-primary-700"
              style={{ left: '50%', transform: 'translateX(-50%)' }}
            />
          </div>
          
          <div className="text-center mt-2">
            <span className="text-xs text-gray-500">
              ±{confidencePercentage.toFixed(1)}% uncertainty
            </span>
          </div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <ClockIcon className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Processing Time</span>
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {result.processing_time_ms || 0}ms
          </div>
        </div>
        
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <ArrowTrendingUpIcon className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">
              {result.ensemble_info ? 'Model Agreement' : 'Market Trend'}
            </span>
          </div>
          <div className="text-lg font-semibold text-green-600">
            {result.ensemble_info ? `${result.ensemble_info.model_agreement}%` : '+5.2%'}
          </div>
          {result.ensemble_info && (
            <div className="text-xs text-gray-500 mt-1">
              {result.ensemble_info.models_used} models used
            </div>
          )}
        </div>
      </div>

      {/* Property Summary */}
      {propertyData && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-3">Property Summary</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500">Type:</span>
              <span className="ml-2 font-medium">{propertyData.property_type}</span>
            </div>
            <div>
              <span className="text-gray-500">Location:</span>
              <span className="ml-2 font-medium">{propertyData.city}</span>
            </div>
            <div>
              <span className="text-gray-500">Size:</span>
              <span className="ml-2 font-medium">{propertyData.square_feet?.toLocaleString()} sq ft</span>
            </div>
            <div>
              <span className="text-gray-500">Occupancy:</span>
              <span className="ml-2 font-medium">{(propertyData.occupancy_rate * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* Info Note */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg flex gap-3">
        <InformationCircleIcon className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-blue-800">
          <p className="font-medium mb-1">About This Valuation</p>
          <p>
            This valuation uses an ensemble of XGBoost, LightGBM, and Neural Network models
            trained on commercial real estate data to provide accurate property valuations
            with explainable insights.
          </p>
        </div>
      </div>
    </motion.div>
  )
}