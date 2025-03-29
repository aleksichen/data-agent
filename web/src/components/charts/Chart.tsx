'use client';

import React from 'react';
import ChartContainer from './ChartContainer';
import ChartRenderer from './ChartRenderer';
import { ChartProps } from './types';
import { useChartData, useChartEvents } from './hooks';

const Chart: React.FC<ChartProps> = (props) => {
  const {
    type,
    data,
    dimensions,
    measures,
    series,
    config = {},
    className,
    style,
    filters,
    customComponents,
    onDataPointClick,
    onHover,
    onBrush,
    ...restProps
  } = props;

  // 处理和转换数据
  const processedData = useChartData(data, { dimensions, measures, series, filters });

  // 设置事件处理器
  const eventHandlers = useChartEvents({
    onDataPointClick,
    onHover,
    onBrush,
  });

  return (
    <ChartContainer
      className={className}
      style={style}
      config={config}
      filters={filters}
    >
      <ChartRenderer
        type={type}
        data={processedData.processedData}
        dimensions={dimensions}
        measures={measures}
        series={series}
        config={config}
        customComponents={customComponents}
        {...eventHandlers}
        {...restProps}
      />
    </ChartContainer>
  );
};

export default Chart;
