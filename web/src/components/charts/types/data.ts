'use client';

import { DataPoint, FieldMapping } from './common';
import { ChartConfig } from './config';

/**
 * 过滤器配置
 */
export interface Filter {
  field: string;
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'nin' | 'contains' | 'startsWith' | 'endsWith';
  value: any;
}

/**
 * 查询配置
 */
export interface Query {
  filters?: Filter[];
  limit?: number;
  offset?: number;
  sort?: {
    field: string;
    order: 'asc' | 'desc';
  }[];
}

/**
 * 处理后的图表数据
 */
export interface ProcessedChartData {
  rawData: DataPoint[];
  processedData: DataPoint[];
  dimensionValues: Record<string, any[]>;
  measureValues: Record<string, any[]>;
  seriesValues: any[] | null;
  metadata: {
    dimensionFields: string[];
    measureFields: string[];
    seriesField?: string;
    minValues: Record<string, number>;
    maxValues: Record<string, number>;
  };
}

/**
 * 图表事件处理
 */
export interface ChartEvents {
  onDataPointClick?: (point: DataPoint, event: React.MouseEvent) => void;
  onHover?: (point: DataPoint | null, event: React.MouseEvent) => void;
  onBrush?: (selection: any) => void;
  onLegendClick?: (item: any, index: number) => void;
  onZoom?: (domain: any) => void;
}

/**
 * Chart组件主要Props接口
 */
export interface ChartProps {
  // 必需属性
  type: string;
  data: DataPoint[];
  
  // 字段映射
  dimensions: FieldMapping[];  // 维度字段 (x轴、分类等)
  measures: FieldMapping[];    // 度量字段 (y轴、值等)
  series?: FieldMapping;       // 系列字段 (多系列图表)
  
  // 可选配置
  config?: ChartConfig;
  
  // 容器相关
  className?: string;
  style?: React.CSSProperties;
  
  // 过滤和查询
  filters?: Filter[];
  query?: Query;
  
  // 事件处理
  onDataPointClick?: (point: DataPoint, event: React.MouseEvent) => void;
  onHover?: (point: DataPoint | null, event: React.MouseEvent) => void;
  onBrush?: (selection: any) => void;
  
  // 自定义组件
  customComponents?: {
    [key: string]: React.ComponentType<any>;
  };
}
