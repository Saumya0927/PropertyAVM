'use client'

import { useState, useMemo, useEffect, useRef } from 'react'
import { MapPinIcon, ExclamationTriangleIcon, GlobeAltIcon } from '@heroicons/react/24/outline'
import { Map, Marker, NavigationControl, Popup } from 'react-map-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

interface PropertyMapProps {
  latitude: number
  longitude: number
  propertyValue: number
}

// Interactive Mapbox GL JS Component
function InteractiveMap({ latitude, longitude, propertyValue }: { latitude: number, longitude: number, propertyValue: number }) {
  const [showPopup, setShowPopup] = useState(true)
  const [mapError, setMapError] = useState(false)

  console.log('=== INTERACTIVE MAP DEBUG ===')
  console.log('Map coordinates:', { latitude, longitude })
  console.log('Property value:', propertyValue)

  const formatValue = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toFixed(1)}M`
    } else if (value >= 1000) {
      return `$${(value / 1000).toFixed(0)}K`
    }
    return `$${value.toLocaleString()}`
  }

  const mapboxToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN || process.env.NEXT_PUBLIC_MAPBOX_TOKEN

  const handleMapError = (error: any) => {
    console.error('Map error:', error)
    setMapError(true)
  }

  const mapStyle = mapboxToken 
    ? 'mapbox://styles/mapbox/streets-v12' 
    : 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json' // Free alternative

  // If no Mapbox token and CartoDB fails, show fallback
  if (mapError) {
    return (
      <div className="h-full bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center">
        <div className="text-center p-4">
          <GlobeAltIcon className="w-12 h-12 text-primary-600 mx-auto mb-3" />
          <p className="text-gray-700 font-medium mb-1">Interactive Map</p>
          <p className="text-gray-600 text-sm mb-2">
            {latitude.toFixed(4)}, {longitude.toFixed(4)}
          </p>
          <div className="bg-primary-600 text-white px-3 py-1 rounded-lg text-sm font-medium">
            {formatValue(propertyValue)}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Map requires network connection
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-full rounded-xl overflow-hidden">
      <Map
        latitude={latitude}
        longitude={longitude}
        zoom={13}
        style={{ width: '100%', height: '100%' }}
        mapStyle={mapStyle}
        mapboxAccessToken={mapboxToken}
        onError={handleMapError}
        attributionControl={false}
      >
        <NavigationControl position="top-right" />
        
        <Marker
          latitude={latitude}
          longitude={longitude}
          anchor="bottom"
        >
          <div className="bg-primary-600 text-white rounded-full p-2 shadow-lg">
            <MapPinIcon className="w-6 h-6" />
          </div>
        </Marker>

        {showPopup && (
          <Popup
            latitude={latitude}
            longitude={longitude}
            anchor="top"
            onClose={() => setShowPopup(false)}
            closeButton={true}
            closeOnClick={false}
            className="property-popup"
          >
            <div className="p-3 text-center">
              <p className="text-sm font-semibold text-gray-900 mb-1">Property Value</p>
              <p className="text-lg font-bold text-primary-600">{formatValue(propertyValue)}</p>
              <p className="text-xs text-gray-500 mt-1">
                {latitude.toFixed(4)}, {longitude.toFixed(4)}
              </p>
            </div>
          </Popup>
        )}
      </Map>
    </div>
  )
}

export default function PropertyMap({ latitude, longitude, propertyValue }: PropertyMapProps) {
  // Use provided coordinates or fallback to a reasonable location
  const mapCoordinates = useMemo(() => {
    // If coordinates seem invalid, use San Francisco as fallback
    if (!latitude || !longitude || 
        Math.abs(latitude) > 90 || Math.abs(longitude) > 180) {
      return { lat: 37.7749, lng: -122.4194 } // San Francisco as a good default
    }
    return { lat: latitude, lng: longitude }
  }, [latitude, longitude])

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Property Location</h3>
      
      <div className="relative h-64 rounded-xl overflow-hidden bg-gray-100">
        <InteractiveMap
          latitude={mapCoordinates.lat}
          longitude={mapCoordinates.lng}
          propertyValue={propertyValue}
        />
      </div>
      
      <LocationDetails latitude={mapCoordinates.lat} longitude={mapCoordinates.lng} />
    </div>
  )
}

function LocationDetails({ latitude, longitude }: { latitude: number, longitude: number }) {
  return (
    <div className="mt-4 grid grid-cols-2 gap-4">
      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-xs text-gray-500">Coordinates</p>
        <p className="text-sm font-medium">{latitude.toFixed(4)}, {longitude.toFixed(4)}</p>
      </div>
      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-xs text-gray-500">Map Provider</p>
        <p className="text-sm font-medium">Mapbox GL JS</p>
      </div>
    </div>
  )
}