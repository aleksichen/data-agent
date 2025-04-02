/**
 * Type definitions for chart component and API
 */

// Supported chart types
export type ChartType =
  | 'bar'
  | 'line'
  | 'pie'
  | 'scatter'
  | 'area'
  | 'heatmap'
  | 'radar'
  | 'funnel';

// Data source configuration
export interface DataSource {
  table: string;
  field: string[];
}

// Field configuration
export interface FieldConfig {
  field: string;
  name: string;
}

// Chart configuration
export interface ChartConfig {
  title?: string;
  height?: number;
  colors?: string[];
  stacked?: boolean;
  fillOpacity?: number;
  sizeField?: string;
  // Additional config properties can be added as needed
}

// Complete chart props interface
export interface ChartProps {
  type: ChartType;
  dataSource: DataSource;
  dimensions: FieldConfig[];
  measures: FieldConfig[];
  series?: FieldConfig;
  config?: ChartConfig;
  onDataPointClick?: (point: any, event: React.MouseEvent) => void;
}

// Chart data API request body
export type ChartDataRequestBody = ChartProps;

// Chart data API response
export interface ChartDataResponse {
  success: boolean;
  data: any;
  error?: string;
  details?: string;
}


// 字段映射定义
interface FieldMapping {
  field: string;        // 字段名
  name: string;         // 显示名称
  aggregation?: string; // 聚合方式 (用于度量)
  group?: string;       // 分组方式 (用于维度)
}

// 过滤条件定义
interface FilterCondition {
  field: string;                    // 字段名
  operator: string;                 // 操作符 (=, >, <, >=, <=, !=, LIKE, IN 等)
  value: string | number | any[];   // 过滤值
}

// 排序定义
interface OrderByOption {
  field: string;              // 排序字段
  direction?: 'ASC' | 'DESC'; // 排序方向，默认ASC
}

// 时间粒度类型
type TimeGranularityType = 'day' | 'week' | 'month' | 'quarter' | 'year';

// 完整的请求参数定义
export type DataFetchParams = {
  // 必填: 数据表名
  table: string;

  // 可选: 需要获取的字段，可以是字段名数组或单个字段名
  fields?: string[] | string;

  // 可选: 维度字段列表
  dimensions?: FieldMapping[];

  // 可选: 度量字段列表
  measures?: FieldMapping[];

  // 可选: 系列字段配置
  series?: FieldMapping | null;

  // 可选: 过滤条件列表
  filters?: FilterCondition[];

  // 可选: 是否进行分组聚合，默认true
  groupBy?: boolean;

  // 可选: 结果限制数量，默认1000
  limit?: number;

  // 可选: 排序设置
  orderBy?: OrderByOption | null;

  // 可选: 时间粒度设置，默认'day'
  timeGranularity?: TimeGranularityType;
}