'use client';

import React from 'react';
import { registry } from './registry';
import { ChartType, DataPoint, FieldMapping } from './types';

interface ChartRendererProps {
  type: ChartType | string;
  data: DataPoint[];
  dimensions: FieldMapping[];
  measures: FieldMapping[];
  series?: FieldMapping;
  config?: any;
  width?: number;
  height?: number;
  [key: string]: any;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({
  type,
  data,
  dimensions,
  measures,
  series,
  config,
  width,
  height,
  ...rest
}) => {
  // 从注册表中获取正确的图表组件
  const ChartComponent = registry[type as ChartType];
  
  if (!ChartComponent) {
    return (
      <div className="chart-error p-4 flex items-center justify-center bg-red-50 border border-red-200 rounded-md text-red-700 h-full w-full" style={{ minHeight: '200px' }}>
        <div className="text-center">
          <p className="text-lg font-semibold">图表类型不支持</p>
          <p className="text-sm mt-1">{`类型 "${type}" 未注册`}</p>
        </div>
      </div>
    );
  }
  
  // 没有数据的情况
  if (!data || data.length === 0) {
    return (
      <div className="chart-no-data p-4 flex items-center justify-center bg-gray-50 border border-gray-200 rounded-md text-gray-500 h-full w-full" style={{ minHeight: '200px' }}>
        <div className="text-center">
          <p className="text-lg font-semibold">暂无数据</p>
          <p className="text-sm mt-1">请检查数据源或筛选条件</p>
        </div>
      </div>
    );
  }
  
  // 渲染正确类型的图表
  return (
    <ChartComponent
      data={data}
      dimensions={dimensions}
      measures={measures}
      series={series}
      config={config}
      width={width}
      height={height}
      {...rest}
    />
  );
};

export default ChartRenderer;
