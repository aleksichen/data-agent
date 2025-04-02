'use client';

export * from './data';
export * from './theme';
export * from './scales';

/**
 * 检查是否在客户端环境
 */
export const isClient = (): boolean => {
  return typeof window !== 'undefined';
};

/**
 * 格式化数字
 */
export const formatNumber = (value: number, options: Intl.NumberFormatOptions = {}): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return '–';
  }
  
  return new Intl.NumberFormat('en-US', options).format(value);
};

/**
 * 格式化百分比
 */
export const formatPercent = (value: number, fractionDigits: number = 1): string => {
  if (value === null || value === undefined || isNaN(value)) {
    return '–';
  }
  
  return `${(value * 100).toFixed(fractionDigits)}%`;
};

/**
 * 格式化日期
 */
export const formatDate = (value: string | number | Date, options: Intl.DateTimeFormatOptions = {}): string => {
  if (!value) return '';
  
  const date = value instanceof Date ? value : new Date(value);
  if (isNaN(date.getTime())) return String(value);
  
  return date.toLocaleDateString(undefined, options);
};

/**
 * 唯一ID生成器
 */
export const generateId = (prefix: string = 'chart'): string => {
  return `${prefix}-${Math.random().toString(36).substring(2, 11)}`;
};

/**
 * 深度合并对象
 */
export const deepMerge = <T>(target: T, source: Partial<T>): T => {
  const output = { ...target };
  
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key as keyof typeof source])) {
        if (!(key in target)) {
          Object.assign(output, { [key]: source[key as keyof typeof source] });
        } else {
          (output as any)[key] = deepMerge((target as any)[key], (source as any)[key]);
        }
      } else {
        Object.assign(output, { [key]: source[key as keyof typeof source] });
      }
    });
  }
  
  return output;
};

/**
 * 检查值是否为对象
 */
const isObject = (item: any): boolean => {
  return item && typeof item === 'object' && !Array.isArray(item);
};
