interface ApiResponse<T = any> {
  data: T;
  error?: string;
}

interface RecentValuation {
  id: string;
  property_id: string;
  predicted_value: number;
  confidence_lower: number | null;
  confidence_upper: number | null;
  price_per_sqft: number | null;
  model_version: string;
  created_at: string;
  property: {
    property_type: string;
    city: string;
    state: string;
    square_feet: number;
    year_built: number | null;
  };
}

interface AnalyticsSummary {
  summary: {
    total_valuations: number;
    total_properties: number;
    avg_property_value: number;
    recent_activity: number;
    avg_response_time: number;
    model_accuracy: number;
    growth_rate: number;
  };
  trends: {
    valuations_30d: number;
    properties_growth: number;
    avg_value_trend: string;
  };
  timestamp: string;
}

interface LiveMetrics {
  timestamp: string;
  system: {
    cpu_usage: number;
    memory_usage: number;
    memory_used_gb: number;
    uptime_hours: number;
  };
  services: {
    database: {
      status: string;
      latency_ms: number | null;
    };
    redis: {
      status: string;
    };
    ml_models: {
      status: string;
      loaded_models: number;
    };
  };
  api: {
    total_requests: number;
    avg_response_time_ms: number;
    requests_per_minute: number;
  };
  alerts: {
    active: number;
    warnings: number;
    errors: number;
  };
}

interface PropertyDistribution {
  by_property_type: Array<{
    type: string;
    count: number;
    avg_value: number;
  }>;
  by_city: Array<{
    city: string;
    count: number;
    avg_value: number;
  }>;
}

interface ValuationTrends {
  period_days: number;
  trends: Array<{
    date: string;
    valuations_count: number;
    average_value: number;
  }>;
  summary: {
    total_valuations: number;
    average_daily_valuations: number;
  };
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      return { 
        data: null as T, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      };
    }
  }

  // Valuation endpoints
  async getRecentValuations(limit: number = 10): Promise<ApiResponse<{ recent_valuations: RecentValuation[]; total_count: number; timestamp: string }>> {
    return this.request(`/api/v1/valuations/recent?limit=${limit}`);
  }

  async predictValuation(propertyData: any): Promise<ApiResponse<any>> {
    return this.request('/api/v1/valuations/predict', {
      method: 'POST',
      body: JSON.stringify(propertyData),
    });
  }

  // Analytics endpoints
  async getAnalyticsSummary(): Promise<ApiResponse<AnalyticsSummary>> {
    return this.request('/api/v1/analytics/summary');
  }

  async getPropertyDistribution(): Promise<ApiResponse<PropertyDistribution>> {
    return this.request('/api/v1/analytics/property-distribution');
  }

  async getValuationTrends(days: number = 30): Promise<ApiResponse<ValuationTrends>> {
    return this.request(`/api/v1/analytics/trends?days=${days}`);
  }

  async getMarketOverview(city?: string, property_type?: string): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (city) params.append('city', city);
    if (property_type) params.append('property_type', property_type);
    
    return this.request(`/api/v1/analytics/market-overview?${params.toString()}`);
  }

  // Monitoring endpoints
  async getLiveMetrics(): Promise<ApiResponse<LiveMetrics>> {
    return this.request('/api/v1/monitoring/live-metrics');
  }

  async getSystemMetrics(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/monitoring/system');
  }

  async getServicesStatus(): Promise<ApiResponse<any>> {
    return this.request('/api/v1/monitoring/services');
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;

// Export types for use in components
export type {
  RecentValuation,
  AnalyticsSummary,
  LiveMetrics,
  PropertyDistribution,
  ValuationTrends,
  ApiResponse,
};