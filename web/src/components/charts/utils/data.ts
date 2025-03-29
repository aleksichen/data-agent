'use client';

import { DataPoint, FieldMapping, Filter, ProcessedChartData } from '../types';

/**
 * 处理图表数据
 */
export const processChartData = (
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
  if (!data || data.length === 0) {
    return {
      rawData: [],
      processedData: [],
      dimensionValues: {},
      measureValues: {},
      seriesValues: null,
      metadata: {
        dimensionFields: [],
        measureFields: [],
        minValues: {},
        maxValues: {},
      },
    };
  }

  // 应用过滤器
  let filteredData = filters ? applyFilters(data, filters) : [...data];

  // 提取维度和度量字段
  const dimensionFields = dimensions.map(d => d.field);
  const measureFields = measures.map(m => m.field);
  
  // 收集维度值和系列值
  const dimensionValues: Record<string, any[]> = {};
  dimensionFields.forEach(field => {
    dimensionValues[field] = [...new Set(filteredData.map(item => item[field]))];
  });
  
  // 收集系列值
  let seriesValues = null;
  if (series) {
    seriesValues = [...new Set(filteredData.map(item => item[series.field]))];
  }
  
  // 计算度量的最小值和最大值
  const minValues: Record<string, number> = {};
  const maxValues: Record<string, number> = {};
  
  measureFields.forEach(field => {
    const values = filteredData.map(item => parseFloat(item[field])).filter(val => !isNaN(val));
    minValues[field] = Math.min(...values);
    maxValues[field] = Math.max(...values);
  });
  
  // 应用聚合函数 (简单实现)
  let processedData = filteredData;
  const needsAggregation = measures.some(m => m.aggregate) || dimensions.some(d => d.aggregate);
  
  if (needsAggregation) {
    processedData = aggregateData(filteredData, dimensions, measures, series);
  }
  
  // 应用排序
  processedData = applySorting(processedData, dimensions, measures);
  
  return {
    rawData: data,
    processedData,
    dimensionValues,
    measureValues: {},
    seriesValues,
    metadata: {
      dimensionFields,
      measureFields,
      seriesField: series?.field,
      minValues,
      maxValues,
    },
  };
};

/**
 * 应用过滤器
 */
const applyFilters = (data: DataPoint[], filters: Filter[]): DataPoint[] => {
  return data.filter(item => {
    return filters.every(filter => {
      const { field, operator, value } = filter;
      const itemValue = item[field];
      
      switch (operator) {
        case 'eq': return itemValue === value;
        case 'neq': return itemValue !== value;
        case 'gt': return itemValue > value;
        case 'gte': return itemValue >= value;
        case 'lt': return itemValue < value;
        case 'lte': return itemValue <= value;
        case 'in': return Array.isArray(value) && value.includes(itemValue);
        case 'nin': return Array.isArray(value) && !value.includes(itemValue);
        case 'contains': return String(itemValue).includes(String(value));
        case 'startsWith': return String(itemValue).startsWith(String(value));
        case 'endsWith': return String(itemValue).endsWith(String(value));
        default: return true;
      }
    });
  });
};

/**
 * 聚合数据 (简化实现)
 */
const aggregateData = (
  data: DataPoint[],
  dimensions: FieldMapping[],
  measures: FieldMapping[],
  series?: FieldMapping
): DataPoint[] => {
  // 创建分组键
  const getGroupKey = (item: DataPoint) => {
    let key = dimensions.map(d => item[d.field]).join('|');
    if (series) {
      key += '|' + item[series.field];
    }
    return key;
  };
  
  // 分组数据
  const groups: Record<string, DataPoint[]> = {};
  data.forEach(item => {
    const key = getGroupKey(item);
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
  });
  
  // 为每个组应用聚合
  return Object.entries(groups).map(([key, items]) => {
    const result: DataPoint = {};
    
    // 保留维度值
    dimensions.forEach(d => {
      result[d.field] = items[0][d.field];
    });
    
    // 保留系列值
    if (series) {
      result[series.field] = items[0][series.field];
    }
    
    // 应用度量聚合
    measures.forEach(m => {
      const { field, aggregate = 'sum' } = m;
      
      switch (aggregate) {
        case 'sum':
          result[field] = items.reduce((sum, item) => sum + (parseFloat(item[field]) || 0), 0);
          break;
        case 'avg':
          result[field] = items.reduce((sum, item) => sum + (parseFloat(item[field]) || 0), 0) / items.length;
          break;
        case 'min':
          result[field] = Math.min(...items.map(item => parseFloat(item[field]) || 0));
          break;
        case 'max':
          result[field] = Math.max(...items.map(item => parseFloat(item[field]) || 0));
          break;
        case 'count':
          result[field] = items.length;
          break;
        case 'distinct':
          result[field] = new Set(items.map(item => item[field])).size;
          break;
        default:
          result[field] = items[0][field];
      }
    });
    
    return result;
  });
};

/**
 * 应用排序
 */
const applySorting = (
  data: DataPoint[],
  dimensions: FieldMapping[],
  measures: FieldMapping[]
): DataPoint[] => {
  const sortFields = [
    ...dimensions.filter(d => d.sortBy),
    ...measures.filter(m => m.sortBy),
  ];
  
  if (sortFields.length === 0) {
    return data;
  }
  
  return [...data].sort((a, b) => {
    for (const field of sortFields) {
      const { field: fieldName, sortBy = 'asc' } = field;
      
      if (a[fieldName] < b[fieldName]) {
        return sortBy === 'asc' ? -1 : 1;
      }
      if (a[fieldName] > b[fieldName]) {
        return sortBy === 'asc' ? 1 : -1;
      }
    }
    return 0;
  });
};

/**
 * 格式化数据值
 */
export const formatValue = (value: any, format?: string | ((value: any) => string)): string => {
  if (value === null || value === undefined) {
    return '';
  }
  
  if (typeof format === 'function') {
    return format(value);
  }
  
  if (!format) {
    return String(value);
  }
  
  // 处理内置格式化选项
  switch (format) {
    case 'number':
      return Number(value).toLocaleString();
    case 'currency':
      return Number(value).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
    case 'percent':
      return (Number(value) * 100).toFixed(2) + '%';
    case 'date':
      return new Date(value).toLocaleDateString();
    case 'datetime':
      return new Date(value).toLocaleString();
    default:
      return String(value);
  }
};
