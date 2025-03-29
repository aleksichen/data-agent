'use client';

/**
 * 图表类型枚举
 */
export type ChartType = 
  | 'line' 
  | 'bar' 
  | 'pie'
  | 'scatter'
  | 'area'
  | 'heatmap'
  | 'radar'
  | 'column'
  | 'dual'
  | 'custom';

/**
 * 数据点类型 - 键值对形式的数据
 */
export interface DataPoint {
  [key: string]: any;
}

/**
 * 字段映射 - 定义如何使用数据字段
 */
export interface FieldMapping {
  field: string;
  name?: string;
  alias?: string;
  format?: string | ((value: any) => string);
  aggregate?: 'sum' | 'avg' | 'min' | 'max' | 'count' | 'distinct';
  filter?: any;
  sortBy?: 'asc' | 'desc';
  // 对于多轴图表
  chartType?: ChartType;
  axis?: 'primary' | 'secondary';
}
