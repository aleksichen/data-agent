/**
 * Hook for fetching chart data from the API
 */
import { useState, useEffect } from 'react';
import type { ChartProps } from '@/types/chart';
import { fetchChartData } from '@/lib/chart-utils';

interface UseChartDataOptions {
  /**
   * Whether to load data immediately when the hook is called
   */
  immediate?: boolean;
  
  /**
   * Optional callback when data loading fails
   */
  onError?: (error: Error) => void;
}

interface UseChartDataResult {
  /**
   * Chart data returned from the API
   */
  data: any;
  
  /**
   * Whether data is currently being loaded
   */
  loading: boolean;
  
  /**
   * Error object if loading fails
   */
  error: Error | null;
  
  /**
   * Function to manually trigger data loading
   */
  loadData: () => Promise<void>;
}

/**
 * Hook for fetching and managing chart data
 * 
 * @param chartProps Chart configuration properties
 * @param options Additional options for data loading
 * @returns Object containing data, loading state, error, and load function
 */
export function useChartData(
  chartProps: ChartProps,
  options?: UseChartDataOptions
): UseChartDataResult {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);
  
  // Function to load chart data
  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await fetchChartData(chartProps);
      setData(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      
      if (options?.onError) {
        options.onError(error);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Load data immediately if requested
  useEffect(() => {
    if (options?.immediate !== false) {
      loadData();
    }
  }, [
    // Re-fetch when these chart properties change
    chartProps.type,
    chartProps.dataSource.table,
    JSON.stringify(chartProps.dataSource.field),
    JSON.stringify(chartProps.dimensions),
    JSON.stringify(chartProps.measures),
    JSON.stringify(chartProps.series)
  ]);
  
  return {
    data,
    loading,
    error,
    loadData
  };
}
