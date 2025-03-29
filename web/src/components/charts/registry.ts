'use client';

import { ChartType } from './types';
import dynamic from 'next/dynamic';

// 动态导入图表组件
const LineChart = dynamic(() => import('./charts/LineChart'), { ssr: false });
const BarChart = dynamic(() => import('./charts/BarChart'), { ssr: false });
const PieChart = dynamic(() => import('./charts/PieChart'), { ssr: false });
const ScatterChart = dynamic(() => import('./charts/ScatterChart'), { ssr: false });
const AreaChart = dynamic(() => import('./charts/AreaChart'), { ssr: false });

// 图表注册表
export const registry: Record<string, React.ComponentType<any>> = {
  'line': LineChart,
  'bar': BarChart,
  'pie': PieChart,
  'scatter': ScatterChart,
  'area': AreaChart,
  // 添加更多图表类型...
};

// 图表注册函数，用于动态扩展
export function registerChart(type: string, component: React.ComponentType<any>) {
  registry[type] = component;
}
