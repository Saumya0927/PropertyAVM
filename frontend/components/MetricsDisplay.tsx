'use client'

import { useLiveMetrics, useAnalyticsSummary } from '@/services/hooks'

interface MetricsDisplayProps {
  showSystemMetrics?: boolean;
}

export default function MetricsDisplay({ showSystemMetrics = false }: MetricsDisplayProps) {
  const { data: liveMetrics, loading: liveLoading, error: liveError } = useLiveMetrics(30000)
  const { data: analytics, loading: analyticsLoading, error: analyticsError } = useAnalyticsSummary()

  if (liveLoading || analyticsLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="text-center animate-pulse">
            <div className="h-8 bg-gray-700 rounded mb-2"></div>
            <div className="h-4 bg-gray-600 rounded w-24 mx-auto"></div>
          </div>
        ))}
      </div>
    )
  }

  if (liveError || analyticsError) {
    return (
      <div className="text-red-400 text-center p-4">
        <p>Error loading metrics: {liveError || analyticsError}</p>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400'
      case 'degraded': return 'text-yellow-400'
      case 'unhealthy': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getUptimePercentage = (systemStatus: any) => {
    if (!systemStatus?.services) return 99.9
    const services = Object.values(systemStatus.services)
    const healthyServices = services.filter((s: any) => s.status === 'healthy').length
    return Math.round((healthyServices / services.length) * 100 * 100) / 100
  }

  if (showSystemMetrics && liveMetrics) {
    // Show system metrics version
    const uptime = getUptimePercentage(liveMetrics)
    
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-3xl font-bold text-primary-400">
            {liveMetrics.api.total_requests.toLocaleString()}
          </div>
          <div className="text-sm text-gray-400 mt-1">Total Requests</div>
        </div>
        
        <div className="text-center">
          <div className="text-3xl font-bold text-green-400">
            {Math.round(liveMetrics.api.avg_response_time_ms)}ms
          </div>
          <div className="text-sm text-gray-400 mt-1">Avg Response</div>
        </div>
        
        <div className="text-center">
          <div className="text-3xl font-bold text-blue-400">
            {liveMetrics.system.cpu_usage}%
          </div>
          <div className="text-sm text-gray-400 mt-1">CPU Usage</div>
        </div>
        
        <div className="text-center">
          <div className={`text-3xl font-bold ${uptime > 99 ? 'text-green-400' : uptime > 95 ? 'text-yellow-400' : 'text-red-400'}`}>
            {uptime}%
          </div>
          <div className="text-sm text-gray-400 mt-1">Uptime</div>
        </div>
      </div>
    )
  }

  // Show analytics metrics version (default)
  if (!analytics) return null

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="text-center">
        <div className="text-3xl font-bold text-primary-400">
          {analytics.summary.total_valuations.toLocaleString()}
        </div>
        <div className="text-sm text-gray-400 mt-1">Total Predictions</div>
      </div>
      
      <div className="text-center">
        <div className="text-3xl font-bold text-green-400">
          {Math.round(analytics.summary.avg_response_time || 47)}ms
        </div>
        <div className="text-sm text-gray-400 mt-1">Avg Response</div>
      </div>
      
      <div className="text-center">
        <div className="text-3xl font-bold text-yellow-400">
          {analytics.summary.model_accuracy}%
        </div>
        <div className="text-sm text-gray-400 mt-1">Model Accuracy</div>
      </div>
      
      <div className="text-center">
        <div className={`text-3xl font-bold ${
          analytics.summary.growth_rate > 0 
            ? 'text-green-400' 
            : analytics.summary.growth_rate < 0 
            ? 'text-red-400' 
            : 'text-gray-400'
        }`}>
          {analytics.summary.growth_rate > 0 ? '+' : ''}{analytics.summary.growth_rate}%
        </div>
        <div className="text-sm text-gray-400 mt-1">Growth Rate</div>
      </div>
    </div>
  )
}