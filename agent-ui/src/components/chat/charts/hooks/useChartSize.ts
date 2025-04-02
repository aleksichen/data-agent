'use client';

import { useState, useEffect, useRef } from 'react';
import { isClient } from '../utils';

interface ChartSize {
  width: number;
  height: number;
  ref: React.RefObject<HTMLDivElement>;
}

interface ChartSizeConfig {
  width?: number | string;
  height?: number | string;
  responsive?: boolean;
}

/**
 * 处理图表尺寸的钩子
 */
export const useChartSize = (config?: ChartSizeConfig): ChartSize => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState<{ width: number; height: number }>({
    width: typeof config?.width === 'number' ? config.width : 400,
    height: typeof config?.height === 'number' ? config.height : 300,
  });

  useEffect(() => {
    if (!isClient() || !containerRef.current) return;

    const updateSize = () => {
      if (!containerRef.current) return;

      // 获取容器尺寸
      let newWidth = size.width;
      let newHeight = size.height;
      
      // 如果指定了固定尺寸，使用固定尺寸
      if (typeof config?.width === 'number') {
        newWidth = config.width;
      } else if (config?.responsive !== false) {
        // 否则，使用容器尺寸（如果响应式）
        newWidth = containerRef.current.clientWidth;
      }
      
      if (typeof config?.height === 'number') {
        newHeight = config.height;
      } else if (config?.responsive !== false) {
        // 如果未指定高度且响应式，可以根据宽度设置一个合适的高宽比
        newHeight = containerRef.current.clientHeight || Math.round(newWidth * 0.6);
      }
      
      if (newWidth !== size.width || newHeight !== size.height) {
        setSize({ width: newWidth, height: newHeight });
      }
    };

    // 初始更新
    updateSize();

    // 添加 resize 监听器用于响应式
    if (config?.responsive !== false) {
      const resizeObserver = new ResizeObserver(updateSize);
      resizeObserver.observe(containerRef.current);
      
      // 清除
      return () => {
        resizeObserver.disconnect();
      };
    }
  }, [config?.width, config?.height, config?.responsive, containerRef.current]);

  return {
    width: size.width,
    height: size.height,
    ref: containerRef,
  };
};

export default useChartSize;
