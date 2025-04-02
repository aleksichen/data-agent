'use client';

/**
 * 内置主题定义
 */
export interface ChartTheme {
  name: string;
  colors: string[];
  backgroundColor: string;
  textColor: string;
  fontFamily: string;
  borderColor: string;
  axisColor: string;
  gridColor: string;
  tooltipBackgroundColor: string;
  tooltipTextColor: string;
}

/**
 * 内置主题
 */
export const themes: Record<string, ChartTheme> = {
  'light': {
    name: 'Light',
    colors: ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'],
    backgroundColor: '#ffffff',
    textColor: '#333333',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    borderColor: '#e0e0e0',
    axisColor: '#666666',
    gridColor: '#f0f0f0',
    tooltipBackgroundColor: 'rgba(255, 255, 255, 0.9)',
    tooltipTextColor: '#333333',
  },
  'dark': {
    name: 'Dark',
    colors: ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'],
    backgroundColor: '#242424',
    textColor: '#e0e0e0',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    borderColor: '#4d4d4d',
    axisColor: '#e0e0e0',
    gridColor: '#383838',
    tooltipBackgroundColor: 'rgba(36, 36, 36, 0.9)',
    tooltipTextColor: '#e0e0e0',
  },
  'pastel': {
    name: 'Pastel',
    colors: ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854', '#ffd92f', '#e5c494', '#b3b3b3'],
    backgroundColor: '#f9f9f9',
    textColor: '#555555',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    borderColor: '#e0e0e0',
    axisColor: '#888888',
    gridColor: '#f0f0f0',
    tooltipBackgroundColor: 'rgba(249, 249, 249, 0.9)',
    tooltipTextColor: '#555555',
  },
  'material': {
    name: 'Material',
    colors: ['#2196f3', '#ff9800', '#4caf50', '#f44336', '#9c27b0', '#673ab7', '#3f51b5', '#00bcd4', '#009688', '#e91e63'],
    backgroundColor: '#ffffff',
    textColor: '#212121',
    fontFamily: 'Roboto, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif',
    borderColor: '#e0e0e0',
    axisColor: '#616161',
    gridColor: '#f5f5f5',
    tooltipBackgroundColor: 'rgba(255, 255, 255, 0.95)',
    tooltipTextColor: '#212121',
  }
};

/**
 * 获取当前主题
 */
export const getTheme = (themeName: string = 'light'): ChartTheme => {
  return themes[themeName] || themes.light;
};

/**
 * 获取颜色从主题或自定义颜色数组
 */
export const getChartColors = (customColors?: string[] | ((data: any, index: number) => string), themeName: string = 'light'): string[] => {
  if (Array.isArray(customColors)) {
    return customColors;
  }
  
  if (typeof customColors === 'function') {
    // 如果是函数，需在实际使用时应用，这里返回主题默认颜色
    return getTheme(themeName).colors;
  }
  
  return getTheme(themeName).colors;
};

/**
 * 获取特定索引的颜色
 */
export const getColorByIndex = (index: number, customColors?: string[] | ((data: any, index: number) => string), themeName: string = 'light'): string => {
  const colors = getChartColors(customColors, themeName);
  return colors[index % colors.length];
};
