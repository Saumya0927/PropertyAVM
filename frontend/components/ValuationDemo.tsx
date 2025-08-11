'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { useRecentValuations } from '@/services/hooks'

export default function RecentValuations() {
  const { data, loading, error } = useRecentValuations(6)
  const [selectedProperty, setSelectedProperty] = useState(0)

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="animate-pulse">
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-4 rounded-xl border-2 border-gray-200">
                <div className="h-4 bg-gray-300 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded mb-1"></div>
                <div className="h-3 bg-gray-100 rounded w-20"></div>
              </div>
            ))}
          </div>
          <div className="bg-gradient-to-br from-primary-50 to-white rounded-xl p-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <div className="h-6 bg-gray-300 rounded mb-4 w-48"></div>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-32"></div>
                  <div className="h-4 bg-gray-200 rounded w-40"></div>
                  <div className="h-4 bg-gray-200 rounded w-36"></div>
                </div>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg">
                <div className="h-8 bg-gray-300 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded mb-4 w-24"></div>
                <div className="h-2 bg-gray-200 rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center text-red-500">
          <p>Error loading recent valuations: {error}</p>
        </div>
      </div>
    )
  }

  const valuations = data?.recent_valuations || []
  
  if (valuations.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center text-gray-500">
          <p>No recent valuations available. Complete some property valuations to see them here.</p>
        </div>
      </div>
    )
  }

  // Take first 3 for display
  const displayProperties = valuations.slice(0, 3)
  const currentProperty = displayProperties[selectedProperty] || displayProperties[0]

  const formatValue = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const getConfidenceRange = (property: any) => {
    if (property.confidence_lower && property.confidence_upper) {
      const lowerPercent = ((property.confidence_lower - property.predicted_value) / property.predicted_value * 100).toFixed(0)
      const upperPercent = ((property.confidence_upper - property.predicted_value) / property.predicted_value * 100).toFixed(0)
      return `${lowerPercent}% / +${upperPercent}%`
    }
    return '±5%' // fallback
  }

  const getConfidenceWidth = (property: any) => {
    if (property.confidence_lower && property.confidence_upper) {
      const range = Math.abs((property.confidence_upper - property.confidence_lower) / property.predicted_value)
      const confidence = Math.max(70, Math.min(95, 100 - (range * 100 * 10))) // Convert range to confidence %
      return `${confidence.toFixed(0)}%`
    }
    return '89%'
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Recent Valuations</h2>
      
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {displayProperties.map((property, index) => (
          <button
            key={property.id}
            onClick={() => setSelectedProperty(index)}
            className={`p-4 rounded-xl border-2 transition-all text-left ${
              selectedProperty === index
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <h4 className="font-semibold text-gray-900">{property.property.property_type}</h4>
            <p className="text-sm text-gray-600">{property.property.city}, {property.property.state}</p>
            <p className="text-xs text-gray-500 mt-1">{property.property.square_feet.toLocaleString()} sq ft</p>
            <p className="text-xs text-primary-600 mt-2">{formatDate(property.created_at)}</p>
          </button>
        ))}
      </div>

      <motion.div
        key={selectedProperty}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="bg-gradient-to-br from-primary-50 to-white rounded-xl p-6"
      >
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              {currentProperty.property.property_type}
            </h3>
            
            <div className="space-y-3">
              <div>
                <span className="text-sm text-gray-500">Location</span>
                <p className="font-medium">{currentProperty.property.city}, {currentProperty.property.state}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Size</span>
                <p className="font-medium">{currentProperty.property.square_feet.toLocaleString()} sq ft</p>
              </div>
              {currentProperty.property.year_built && (
                <div>
                  <span className="text-sm text-gray-500">Year Built</span>
                  <p className="font-medium">{currentProperty.property.year_built}</p>
                </div>
              )}
              {currentProperty.price_per_sqft && (
                <div>
                  <span className="text-sm text-gray-500">Price per Sq Ft</span>
                  <p className="font-medium">${currentProperty.price_per_sqft.toFixed(2)}</p>
                </div>
              )}
              <div>
                <span className="text-sm text-gray-500">Model Version</span>
                <p className="font-medium">{currentProperty.model_version}</p>
              </div>
            </div>
          </div>

          <div className="flex flex-col justify-center">
            <div className="bg-white rounded-xl p-6 shadow-lg">
              <div className="text-3xl font-bold text-primary-600 mb-2">
                {formatValue(currentProperty.predicted_value)}
              </div>
              <div className="text-sm text-gray-600 mb-4">
                Confidence: {getConfidenceRange(currentProperty)}
              </div>
              
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: getConfidenceWidth(currentProperty) }}
                  transition={{ duration: 1, delay: 0.2 }}
                  className="h-full bg-gradient-to-r from-primary-400 to-primary-600"
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">{getConfidenceWidth(currentProperty)} Model Confidence</p>
              <p className="text-xs text-gray-400 mt-1">Valued on {formatDate(currentProperty.created_at)}</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}