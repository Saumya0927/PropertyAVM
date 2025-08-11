'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import ValuationForm from '../../components/ValuationForm'
import ValuationResults from '../../components/ValuationResults'
import PropertyMap from '../../components/PropertyMap'
import { BuildingOfficeIcon } from '@heroicons/react/24/outline'

interface ValuationResult {
  predicted_value: number
  confidence_interval: {
    lower: number
    upper: number
    confidence_level: number
  }
  price_per_sqft: number
  valuation_date: string
  model_version: string
  processing_time_ms?: number
  cached?: boolean
}

interface PropertyData {
  property_type: string
  city: string
  square_feet: number
  occupancy_rate: number
  latitude?: number
  longitude?: number
  [key: string]: any
}

export default function ValuationPage() {
  const [valuationResult, setValuationResult] = useState<ValuationResult | null>(null)
  const [propertyData, setPropertyData] = useState<PropertyData | null>(null)

  // City coordinates mapping
  const getCityCoordinates = (city: string): { latitude: number, longitude: number } => {
    const cityMap: Record<string, { latitude: number, longitude: number }> = {
      'New York': { latitude: 40.7128, longitude: -74.0060 },
      'Los Angeles': { latitude: 34.0522, longitude: -118.2437 },
      'Chicago': { latitude: 41.8781, longitude: -87.6298 },
      'Houston': { latitude: 29.7604, longitude: -95.3698 },
      'Phoenix': { latitude: 33.4484, longitude: -112.0740 },
      'San Francisco': { latitude: 37.7749, longitude: -122.4194 },
      'Seattle': { latitude: 47.6062, longitude: -122.3321 },
      'Boston': { latitude: 42.3601, longitude: -71.0589 },
      'Miami': { latitude: 25.7617, longitude: -80.1918 },
      'Denver': { latitude: 39.7392, longitude: -104.9903 }
    }
    return cityMap[city] || { latitude: 40.7128, longitude: -74.0060 }
  }

  const handleValuationComplete = (result: any, data: any) => {
    // Add coordinates based on city
    const coordinates = getCityCoordinates(data.city)
    const enhancedData = {
      ...data,
      ...coordinates
    }
    
    setValuationResult(result)
    setPropertyData(enhancedData)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 bg-primary-100 text-primary-700 px-4 py-2 rounded-full text-sm font-semibold mb-4">
            <BuildingOfficeIcon className="w-4 h-4" />
            Property Valuation Tool
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-gray-900">
            Get Instant Property Valuation
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Enter property details below to receive an ML-powered valuation with confidence intervals and explainable insights
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Form */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-bold mb-6 text-gray-900">Property Details</h2>
              <ValuationForm 
                onSubmit={handleValuationComplete}
              />
            </div>
          </motion.div>

          {/* Right Column - Results/Map */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-8"
          >
            {valuationResult ? (
              <>
                <ValuationResults result={valuationResult} propertyData={propertyData} />
                <PropertyMap 
                  latitude={propertyData?.latitude || 40.7128}
                  longitude={propertyData?.longitude || -74.0060}
                  propertyValue={valuationResult.predicted_value}
                />
              </>
            ) : (
              <div className="bg-white rounded-2xl shadow-xl p-8 h-full min-h-[600px] flex flex-col items-center justify-center">
                <BuildingOfficeIcon className="w-24 h-24 text-gray-300 mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Valuation Yet</h3>
                <p className="text-gray-600 text-center max-w-sm">
                  Fill out the property details form to get an instant ML-powered valuation with confidence intervals
                </p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-16 grid md:grid-cols-3 gap-6"
        >
          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Instant Results</h3>
            <p className="text-gray-600">Get property valuations in under 100ms with our optimized ML pipeline</p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">89% Accuracy</h3>
            <p className="text-gray-600">Ensemble model combining XGBoost, LightGBM, and Neural Networks</p>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-lg">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Explainable AI</h3>
            <p className="text-gray-600">SHAP values explain which features drive the valuation</p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}