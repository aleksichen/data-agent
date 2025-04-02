'use client';

import { useMemo } from 'react';
import { DataPoint, FieldMapping, Filter, ProcessedChartData } from '../types';
import { processChartData } from '../utils/data';

/**
 * 处理图表数据的钩子
 */
export const useChartData = (
  data: DataPoint[],
  {
    dimensions,
    measures,
    series,
    filters,
  }: {
    dimensions: FieldMapping[];
    measures: FieldMapping[];
    series?: FieldMapping;
    filters?: Filter[];
  }
): ProcessedChartData => {
  return useMemo(() => {
    return processChartData(data, { dimensions, measures, series, filters });
  }, [data, dimensions, measures, series, filters]);
};

export default useChartData;
