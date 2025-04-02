'use client';

/**
 * 图表配置接口
 */
export interface ChartConfig {
  // 基础配置
  width?: number | string;
  height?: number | string;
  margin?: {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
  };
  
  // 视觉配置
  theme?: string | object;
  colors?: string[] | ((data: any, index: number) => string);
  background?: string;
  padding?: number | [number, number, number, number];
  
  // 标题和描述
  title?: string;
  description?: string;
  
  // 交互配置
  interactive?: boolean;
  animationDuration?: number;
  tooltip?: TooltipConfig;
  legend?: LegendConfig;
  brush?: BrushConfig;
  
  // 轴配置
  xAxis?: AxisConfig;
  yAxis?: AxisConfig;
  
  // 布局配置
  layout?: 'horizontal' | 'vertical';
  groupMode?: 'grouped' | 'stacked';
  
  // 其他
  renderer?: 'canvas' | 'svg';
  locale?: string;
  responsive?: boolean;
  showFilters?: boolean;
  footer?: React.ReactNode;
  
  // 特定图表类型配置
  [key: string]: any;
}

export interface TooltipConfig {
  enabled?: boolean;
  format?: string | ((value: any) => string);
  custom?: (props: any) => React.ReactNode;
  includeFields?: string[];
  excludeFields?: string[];
  followMouse?: boolean;
  position?: 'top' | 'right' | 'bottom' | 'left';
}

export interface LegendConfig {
  enabled?: boolean;
  position?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
  format?: (value: any) => string;
  onClick?: (item: any, index: number) => void;
}

export interface BrushConfig {
  enabled?: boolean;
  type?: 'x' | 'y' | 'xy';
  onBrush?: (selection: any) => void;
}

export interface AxisConfig {
  enabled?: boolean;
  title?: string;
  format?: (value: any) => string;
  min?: number;
  max?: number;
  domain?: [number, number];
  tickCount?: number;
  tickValues?: any[];
  tickFormat?: (value: any) => string;
}
