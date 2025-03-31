/**
 * 数据查询服务
 * 用于与后端数据API进行交互
 */

export interface ChartDataSource {
  table: string;
  field: string[];
}

export interface ChartDimension {
  field: string;
  name: string;
}

export interface ChartMeasure {
  field: string;
  name: string;
}

export interface ChartSeries {
  field: string;
  name: string;
}

export interface ChartConfig {
  dataSource: ChartDataSource;
  dimensions?: ChartDimension[];
  measures?: ChartMeasure[];
  series?: ChartSeries;
  config?: Record<string, any>;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * 查询图表数据
 * 
 * @param chartConfig 图表配置参数
 * @returns 处理后的图表数据
 */
export async function fetchChartData(chartConfig: ChartConfig): Promise<any[]> {
  try {
    const response = await fetch('/api/data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(chartConfig),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch chart data');
    }

    const result = await response.json() as ApiResponse<any[]>;
    
    if (result.error) {
      throw new Error(result.error);
    }
    
    return result.data || [];
  } catch (error) {
    console.error('Error fetching chart data:', error);
    throw error;
  }
}
