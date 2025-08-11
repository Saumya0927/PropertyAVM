'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiService, RecentValuation, AnalyticsSummary, LiveMetrics, PropertyDistribution, ValuationTrends } from './api';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

// Generic hook for API calls
function useApi<T>(
  apiCall: () => Promise<{ data: T; error?: string }>,
  deps: any[] = []
): UseApiState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiCall();
      if (response.error) {
        setError(response.error);
        setData(null);
      } else {
        setData(response.data);
        setError(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
}

// Specific hooks for different endpoints
export function useRecentValuations(limit: number = 10) {
  return useApi(
    () => apiService.getRecentValuations(limit),
    [limit]
  );
}

export function useAnalyticsSummary() {
  return useApi(() => apiService.getAnalyticsSummary());
}

export function useLiveMetrics(refreshInterval: number = 30000) {
  const [data, setData] = useState<LiveMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    if (loading) setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getLiveMetrics();
      if (response.error) {
        setError(response.error);
        setData(null);
      } else {
        setData(response.data);
        setError(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [loading]);

  useEffect(() => {
    fetchMetrics();
    
    // Set up interval for real-time updates
    const interval = setInterval(fetchMetrics, refreshInterval);
    
    return () => clearInterval(interval);
  }, [fetchMetrics, refreshInterval]);

  return {
    data,
    loading,
    error,
    refetch: fetchMetrics
  };
}

export function usePropertyDistribution() {
  return useApi(() => apiService.getPropertyDistribution());
}

export function useValuationTrends(days: number = 30) {
  return useApi(
    () => apiService.getValuationTrends(days),
    [days]
  );
}

export function useMarketOverview(city?: string, propertyType?: string) {
  return useApi(
    () => apiService.getMarketOverview(city, propertyType),
    [city, propertyType]
  );
}

// Hook for system health monitoring
export function useSystemHealth(checkInterval: number = 60000) {
  const [isHealthy, setIsHealthy] = useState(true);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const healthy = await apiService.healthCheck();
        setIsHealthy(healthy);
        setLastCheck(new Date());
      } catch {
        setIsHealthy(false);
        setLastCheck(new Date());
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, checkInterval);
    
    return () => clearInterval(interval);
  }, [checkInterval]);

  return { isHealthy, lastCheck };
}

// Hook for property valuation with loading state
export function usePropertyValuation() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const predict = useCallback(async (propertyData: any) => {
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      const response = await apiService.predictValuation(propertyData);
      if (response.error) {
        setError(response.error);
      } else {
        setResult(response.data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    predict,
    loading,
    error,
    result,
    clearResult: () => setResult(null),
    clearError: () => setError(null)
  };
}