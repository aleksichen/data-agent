'use client';

import { useCallback } from 'react';
import { DataPoint } from '../types';

interface ChartEventHandlers {
  handleDataPointClick: (point: DataPoint, event: React.MouseEvent) => void;
  handleHover: (point: DataPoint | null, event: React.MouseEvent) => void;
  handleBrush: (selection: any) => void;
  handleLegendClick: (item: any, index: number) => void;
}

/**
 * 处理图表事件的钩子
 */
export const useChartEvents = ({
  onDataPointClick,
  onHover,
  onBrush,
  onLegendClick,
}: {
  onDataPointClick?: (point: DataPoint, event: React.MouseEvent) => void;
  onHover?: (point: DataPoint | null, event: React.MouseEvent) => void;
  onBrush?: (selection: any) => void;
  onLegendClick?: (item: any, index: number) => void;
}): ChartEventHandlers => {
  
  // 点击数据点
  const handleDataPointClick = useCallback((point: DataPoint, event: React.MouseEvent) => {
    if (onDataPointClick) {
      onDataPointClick(point, event);
    }
  }, [onDataPointClick]);
  
  // 悬停处理
  const handleHover = useCallback((point: DataPoint | null, event: React.MouseEvent) => {
    if (onHover) {
      onHover(point, event);
    }
  }, [onHover]);
  
  // 刷选处理
  const handleBrush = useCallback((selection: any) => {
    if (onBrush) {
      onBrush(selection);
    }
  }, [onBrush]);
  
  // 图例点击
  const handleLegendClick = useCallback((item: any, index: number) => {
    if (onLegendClick) {
      onLegendClick(item, index);
    }
  }, [onLegendClick]);
  
  return {
    handleDataPointClick,
    handleHover,
    handleBrush,
    handleLegendClick,
  };
};

export default useChartEvents;
