/**
 * Chart utility functions
 */
import type { ChartProps, ChartDataResponse } from '@/types/chart';

/**
 * Fetch chart data from the API
 * 
 * @param chartProps Chart configuration properties
 * @returns Formatted chart data
 */
export async function fetchChartData(chartProps: ChartProps): Promise<any> {
  try {
    const response = await fetch('/api/chart-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(chartProps),
    });
    
    const result: ChartDataResponse = await response.json();
    
    if (!response.ok) {
      throw new Error(result.error || 'Failed to fetch chart data');
    }
    
    if (!result.success) {
      throw new Error(result.error || 'Failed to fetch chart data');
    }
    
    return result.data;
  } catch (error) {
    console.error('Error fetching chart data:', error);
    throw error;
  }
}

/**
 * Generate a default color palette for charts if not provided
 * 
 * @param count Number of colors needed
 * @returns Array of color hex codes
 */
export function generateColorPalette(count: number): string[] {
  const defaultColors = [
    '#4e79a7', // Blue
    '#f28e2c', // Orange
    '#e15759', // Red
    '#76b7b2', // Teal
    '#59a14f', // Green
    '#edc949', // Yellow
    '#af7aa1', // Purple
    '#ff9da7', // Pink
    '#9c755f', // Brown
    '#bab0ab'  // Gray
  ];
  
  // If we need more colors than in our default palette, cycle through them
  if (count <= defaultColors.length) {
    return defaultColors.slice(0, count);
  } else {
    const result = [...defaultColors];
    let remaining = count - defaultColors.length;
    
    while (remaining > 0) {
      const toAdd = Math.min(remaining, defaultColors.length);
      result.push(...defaultColors.slice(0, toAdd));
      remaining -= toAdd;
    }
    
    return result;
  }
}

/**
 * Format number values for display in charts
 * 
 * @param value Numeric value
 * @param decimals Number of decimal places
 * @returns Formatted string
 */
export function formatNumber(value: number, decimals: number = 2): string {
  if (value === null || value === undefined) {
    return '-';
  }
  
  // Handle large numbers with K, M, B suffixes
  if (Math.abs(value) >= 1_000_000_000) {
    return (value / 1_000_000_000).toFixed(decimals) + 'B';
  } else if (Math.abs(value) >= 1_000_000) {
    return (value / 1_000_000).toFixed(decimals) + 'M';
  } else if (Math.abs(value) >= 1_000) {
    return (value / 1_000).toFixed(decimals) + 'K';
  } else {
    return value.toFixed(decimals);
  }
}

/**
 * Format percentage values for display in charts
 * 
 * @param value Numeric value (0-100 or 0-1)
 * @returns Formatted percentage string
 */
export function formatPercentage(value: number): string {
  if (value === null || value === undefined) {
    return '-';
  }
  
  // Handle values that might be given as decimals (0-1)
  const percentValue = value > 1 ? value : value * 100;
  return percentValue.toFixed(1) + '%';
}
