'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon,
  BuildingOfficeIcon,
  CpuChipIcon,
  ClockIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { 
  useAnalyticsSummary, 
  useValuationTrends, 
  usePropertyDistribution, 
  useLiveMetrics, 
  useRecentValuations 
} from '../../services/hooks'
import MetricsDisplay from '../../components/MetricsDisplay'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export default function DashboardPage() {
  const [timeRange, setTimeRange] = useState('7d')
  const { data: analytics, loading: analyticsLoading, error: analyticsError } = useAnalyticsSummary()
  const { data: trends, loading: trendsLoading } = useValuationTrends(timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90)
  const { data: distribution, loading: distributionLoading } = usePropertyDistribution()
  const { data: liveMetrics, loading: liveLoading } = useLiveMetrics(30000)
  const { data: recentValuations, loading: recentLoading } = useRecentValuations(10)

  // Generate chart data from real data
  const getValuationTrendData = () => {
    if (!trends || trendsLoading) {
      return {
        labels: [...Array(7)].map(() => '...'),
        datasets: [{
          label: 'Valuations',
          data: [...Array(7)].map(() => 0),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
          fill: true
        }]
      }
    }

    const trendData = trends.trends || []
    const labels = trendData.map(t => new Date(t.date).toLocaleDateString('en-US', { weekday: 'short' }))
    const data = trendData.map(t => t.valuations_count)

    return {
      labels,
      datasets: [{
        label: 'Valuations',
        data,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    }
  }

  const valuationTrendData = getValuationTrendData()

  const getPropertyTypeData = () => {
    if (!distribution || distributionLoading) {
      return {
        labels: ['Loading...'],
        datasets: [{
          data: [1],
          backgroundColor: ['rgba(156, 163, 175, 0.5)']
        }]
      }
    }

    const typeData = distribution.by_property_type || []
    const labels = typeData.map(t => t.type)
    const data = typeData.map(t => t.count)
    const colors = [
      'rgba(59, 130, 246, 0.8)',
      'rgba(34, 197, 94, 0.8)',
      'rgba(234, 179, 8, 0.8)',
      'rgba(168, 85, 247, 0.8)',
      'rgba(239, 68, 68, 0.8)',
      'rgba(236, 72, 153, 0.8)'
    ]

    return {
      labels,
      datasets: [{
        data,
        backgroundColor: colors.slice(0, data.length)
      }]
    }
  }

  const propertyTypeData = getPropertyTypeData()

  const getResponseTimeData = () => {
    if (!liveMetrics || liveLoading) {
      return {
        labels: ['Loading...'],
        datasets: [{
          label: 'Response Time Distribution',
          data: [1],
          backgroundColor: 'rgba(156, 163, 175, 0.5)'
        }]
      }
    }

    // Generate distribution based on average response time
    const avgTime = liveMetrics.api.avg_response_time_ms
    const total = liveMetrics.api.total_requests || 1000
    
    // Simulate distribution around average response time
    const distribution = [
      Math.floor(total * (avgTime < 25 ? 0.7 : avgTime < 50 ? 0.5 : 0.3)),
      Math.floor(total * (avgTime < 50 ? 0.6 : avgTime < 100 ? 0.4 : 0.2)),
      Math.floor(total * (avgTime < 100 ? 0.2 : 0.3)),
      Math.floor(total * 0.1),
      Math.floor(total * 0.05)
    ]

    return {
      labels: ['0-25ms', '25-50ms', '50-100ms', '100-200ms', '200ms+'],
      datasets: [{
        label: 'Response Time Distribution',
        data: distribution,
        backgroundColor: 'rgba(34, 197, 94, 0.8)'
      }]
    }
  }

  const responseTimeData = getResponseTimeData()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">Real-time insights into model performance and system metrics</p>
        </div>

        {/* Time Range Selector */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex gap-2">
            {['24h', '7d', '30d', '90d'].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === range
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {range}
              </button>
            ))}
          </div>
        </div>

        {/* Key Metrics */}
        <div className="mb-8">
          <MetricsDisplay showSystemMetrics={false} />
        </div>


        {/* Charts */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Valuation Trends</h3>
            <Line 
              data={valuationTrendData} 
              options={{
                responsive: true,
                plugins: {
                  legend: { display: false }
                },
                scales: {
                  y: { beginAtZero: true }
                }
              }}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Property Type Distribution</h3>
            <div className="h-64 flex items-center justify-center">
              <Doughnut 
                data={propertyTypeData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: { position: 'right' }
                  }
                }}
              />
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="bg-white rounded-xl p-6 shadow-lg"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Response Time Distribution</h3>
          <Bar 
            data={responseTimeData}
            options={{
              responsive: true,
              plugins: {
                legend: { display: false }
              },
              scales: {
                y: { beginAtZero: true }
              }
            }}
          />
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="bg-white rounded-xl p-6 shadow-lg mt-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Valuations</h3>
          
          {recentLoading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg animate-pulse">
                  <div className="flex items-center gap-4">
                    <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                    <div>
                      <div className="h-4 bg-gray-300 rounded w-20 mb-1"></div>
                      <div className="h-3 bg-gray-200 rounded w-32"></div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="h-4 bg-gray-300 rounded w-24 mb-1"></div>
                    <div className="h-3 bg-gray-200 rounded w-16"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : recentValuations?.recent_valuations?.length > 0 ? (
            <div className="space-y-3">
              {recentValuations.recent_valuations.slice(0, 5).map((item) => {
                const timeAgo = new Date(item.created_at).toLocaleString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })
                
                return (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <div>
                        <span className="font-medium text-gray-900">{item.property_id || 'AUTO-GEN'}</span>
                        <span className="ml-2 text-sm text-gray-600">{item.property.property_type} • {item.property.city}, {item.property.state}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-gray-900">
                        ${(item.predicted_value / 1000000).toFixed(1)}M
                      </div>
                      <div className="text-xs text-gray-500">{timeAgo}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No recent valuations found. Complete some property valuations to see activity here.</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}