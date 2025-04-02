'use client';

/**
 * 线性比例尺函数 - 输入值映射到输出范围
 */
export const linearScale = (
  value: number, 
  domain: [number, number] = [0, 1], 
  range: [number, number] = [0, 1], 
  clamp: boolean = false
): number => {
  // 确保域有效
  if (domain[0] === domain[1]) {
    return range[0];
  }
  
  // 计算比例
  let normalized = (value - domain[0]) / (domain[1] - domain[0]);
  
  // 可选的钳制到范围
  if (clamp) {
    normalized = Math.max(0, Math.min(1, normalized));
  }
  
  // 映射到输出范围
  return range[0] + normalized * (range[1] - range[0]);
};

/**
 * 计算合适的数字轴刻度
 */
export const calculateTicks = (min: number, max: number, targetCount: number = 5): number[] => {
  if (min === max) {
    return [min];
  }
  
  const range = max - min;
  const roughStep = range / (targetCount - 1);
  
  // 找到"漂亮"的步长 (1, 2, 5, 10, 20, 50, etc.)
  const magnitudeExponent = Math.floor(Math.log10(roughStep));
  const magnitude = Math.pow(10, magnitudeExponent);
  
  let nicestStep;
  const normalized = roughStep / magnitude;
  
  if (normalized < 1.5) {
    nicestStep = 1;
  } else if (normalized < 3) {
    nicestStep = 2;
  } else if (normalized < 7) {
    nicestStep = 5;
  } else {
    nicestStep = 10;
  }
  
  nicestStep *= magnitude;
  
  // 计算起始点 (向下取整到最近的nicestStep的倍数)
  const start = Math.floor(min / nicestStep) * nicestStep;
  
  // 生成刻度
  const ticks = [];
  let currentTick = start;
  
  while (currentTick <= max + 0.5 * nicestStep) {
    ticks.push(currentTick);
    currentTick += nicestStep;
  }
  
  return ticks;
};

/**
 * 确保值在范围内
 */
export const clamp = (value: number, min: number, max: number): number => {
  return Math.max(min, Math.min(max, value));
};

/**
 * 构建离散映射比例尺 (用于分类数据)
 */
export const createCategoryScale = <T>(
  categories: T[],
  range: [number, number] = [0, 1]
): (value: T) => number => {
  const step = categories.length > 1 ? (range[1] - range[0]) / (categories.length - 1) : 0;
  
  return (value: T) => {
    const index = categories.indexOf(value);
    if (index === -1) return range[0];
    return range[0] + index * step;
  };
};
