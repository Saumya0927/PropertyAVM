'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { usePropertyValuation } from '../services/hooks'

interface ValuationFormData {
  property_type: string
  city: string
  state: string
  square_feet: number
  num_floors: number
  num_units: number
  parking_spots: number
  occupancy_rate: number
  annual_revenue: number
  annual_expenses: number
  net_operating_income: number
  cap_rate: number
  walk_score: number
  transit_score: number
  building_age: number
  distance_to_downtown: number
}

interface ValuationFormProps {
  onSubmit: (result: any, data: any) => void
}

export default function ValuationForm({ onSubmit }: ValuationFormProps) {
  const { predict, loading, error, result, clearError } = usePropertyValuation()
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<ValuationFormData>()
  
  const annual_revenue = watch('annual_revenue', 0)
  const annual_expenses = watch('annual_expenses', 0)
  
  // Auto-calculate NOI
  const net_operating_income = annual_revenue - annual_expenses
  if (net_operating_income !== watch('net_operating_income')) {
    setValue('net_operating_income', net_operating_income)
  }

  // Handle result when prediction completes
  useEffect(() => {
    if (result) {
      toast.success('Valuation completed successfully!')
      onSubmit(result, {}) // Pass empty object as form data since we're using the hook
    }
  }, [result, onSubmit])

  // Handle errors
  useEffect(() => {
    if (error) {
      toast.error(error)
      clearError()
    }
  }, [error, clearError])

  const submitValuation = async (data: ValuationFormData) => {
    // Convert string inputs to numbers for proper backend processing
    const numericData = {
      ...data,
      square_feet: Number(data.square_feet),
      num_floors: Number(data.num_floors),
      num_units: Number(data.num_units),
      parking_spots: Number(data.parking_spots),
      occupancy_rate: Number(data.occupancy_rate),
      annual_revenue: Number(data.annual_revenue),
      annual_expenses: Number(data.annual_expenses),
      net_operating_income: Number(data.net_operating_income),
      cap_rate: Number(data.cap_rate),
      walk_score: Number(data.walk_score),
      transit_score: Number(data.transit_score),
      building_age: Number(data.building_age),
      distance_to_downtown: Number(data.distance_to_downtown)
    }
    
    await predict(numericData)
  }

  return (
    <form onSubmit={handleSubmit(submitValuation)} className="space-y-6">
      {/* Property Type & Location */}
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Property Type
          </label>
          <select
            {...register('property_type', { required: 'Property type is required' })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Select type</option>
            <option value="Office">Office</option>
            <option value="Retail">Retail</option>
            <option value="Industrial">Industrial</option>
            <option value="Multifamily">Multifamily</option>
            <option value="Hotel">Hotel</option>
            <option value="Mixed-Use">Mixed-Use</option>
          </select>
          {errors.property_type && (
            <p className="text-red-500 text-xs mt-1">{errors.property_type.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            City
          </label>
          <select
            {...register('city', { required: 'City is required' })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Select city</option>
            <option value="New York">New York</option>
            <option value="Los Angeles">Los Angeles</option>
            <option value="Chicago">Chicago</option>
            <option value="Houston">Houston</option>
            <option value="Phoenix">Phoenix</option>
            <option value="San Francisco">San Francisco</option>
            <option value="Seattle">Seattle</option>
            <option value="Boston">Boston</option>
            <option value="Miami">Miami</option>
            <option value="Denver">Denver</option>
          </select>
          {errors.city && (
            <p className="text-red-500 text-xs mt-1">{errors.city.message}</p>
          )}
        </div>
      </div>

      {/* Physical Characteristics */}
      <div className="grid md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Square Feet
          </label>
          <input
            type="number"
            {...register('square_feet', { 
              required: 'Square feet is required',
              min: { value: 100, message: 'Must be at least 100' }
            })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="10000"
          />
          {errors.square_feet && (
            <p className="text-red-500 text-xs mt-1">{errors.square_feet.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Number of Floors
          </label>
          <input
            type="number"
            {...register('num_floors', { 
              required: 'Number of floors is required',
              min: { value: 1, message: 'Must be at least 1' }
            })}
            defaultValue={1}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Parking Spots
          </label>
          <input
            type="number"
            {...register('parking_spots', { min: 0 })}
            defaultValue={50}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      {/* Financial Information */}
      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Annual Revenue ($)
          </label>
          <input
            type="number"
            {...register('annual_revenue', { 
              required: 'Annual revenue is required',
              min: { value: 0, message: 'Must be positive' }
            })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="500000"
          />
          {errors.annual_revenue && (
            <p className="text-red-500 text-xs mt-1">{errors.annual_revenue.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Annual Expenses ($)
          </label>
          <input
            type="number"
            {...register('annual_expenses', { 
              required: 'Annual expenses is required',
              min: { value: 0, message: 'Must be positive' }
            })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            placeholder="150000"
          />
          {errors.annual_expenses && (
            <p className="text-red-500 text-xs mt-1">{errors.annual_expenses.message}</p>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Net Operating Income ($)
          </label>
          <input
            type="number"
            {...register('net_operating_income')}
            readOnly
            className="w-full px-4 py-2 border border-gray-200 rounded-lg bg-gray-50"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Occupancy Rate (%)
          </label>
          <input
            type="number"
            step="0.01"
            {...register('occupancy_rate', { 
              required: 'Occupancy rate is required',
              min: { value: 0, message: 'Must be between 0 and 1' },
              max: { value: 1, message: 'Must be between 0 and 1' }
            })}
            defaultValue={0.92}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          {errors.occupancy_rate && (
            <p className="text-red-500 text-xs mt-1">{errors.occupancy_rate.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Cap Rate (%)
          </label>
          <input
            type="number"
            step="0.001"
            {...register('cap_rate', { 
              required: 'Cap rate is required',
              min: { value: 0.01, message: 'Must be greater than 0' },
              max: { value: 1, message: 'Must be less than 1' }
            })}
            defaultValue={0.06}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          {errors.cap_rate && (
            <p className="text-red-500 text-xs mt-1">{errors.cap_rate.message}</p>
          )}
        </div>
      </div>

      {/* Location Scores */}
      <div className="grid md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Walk Score (0-100)
          </label>
          <input
            type="number"
            {...register('walk_score', { min: 0, max: 100 })}
            defaultValue={85}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Transit Score (0-100)
          </label>
          <input
            type="number"
            {...register('transit_score', { min: 0, max: 100 })}
            defaultValue={90}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Building Age (years)
          </label>
          <input
            type="number"
            {...register('building_age', { min: 0 })}
            defaultValue={10}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      {/* Hidden fields with defaults */}
      <input type="hidden" {...register('state')} value="CA" />
      <input type="hidden" {...register('num_units')} value={1} />
      <input type="hidden" {...register('distance_to_downtown')} value={5} />

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-all ${
          loading 
            ? 'bg-gray-400 cursor-not-allowed' 
            : 'bg-primary-600 hover:bg-primary-700 hover:shadow-lg'
        }`}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Processing...
          </span>
        ) : (
          'Get Valuation'
        )}
      </button>
    </form>
  )
}