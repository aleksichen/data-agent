'use client';

import React, { useEffect, useState } from 'react';
import { DataPoint, FieldMapping } from '../types';
import { getColorByIndex } from '../utils/theme';

interface PieChartProps {
  data: DataPoint[];
  dimensions: FieldMapping[];
  measures: FieldMapping[];
  config?: any;
  width?: number;
  height?: number;
  handleDataPointClick?: (point: DataPoint, event: React.MouseEvent) => void;
  handleHover?: (point: DataPoint | null, event: React.MouseEvent) => void;
}

const PieChart: React.FC<PieChartProps> = ({
  data,
  dimensions,
  measures,
  config = {},
  width = 400,
  height = 300,
  handleDataPointClick,
  handleHover,
}) => {
  const [chartReady, setChartReady] = useState(false);
  
  // 获取维度和度量字段
  const dimensionField = dimensions[0]?.field;
  const measureField = measures[0]?.field;
  
  // 是否为环形图
  const isDonut = config.donut === true;
  const innerRadius = isDonut ? Math.min(width, height) * 0.25 : 0;
  const outerRadius = Math.min(width, height) * 0.4;
  
  // 中心点
  const centerX = width / 2;
  const centerY = height / 2;
  
  useEffect(() => {
    // 在实际项目中，这里会导入和初始化图表库
    const loadChartLibrary = async () => {
      try {
        // 实际应用中，我们会在这里导入图表库，如 recharts, chart.js 等
        // const ChartLibrary = await import('chart-library');
        
        // 模拟加载延迟
        setTimeout(() => {
          setChartReady(true);
        }, 300);
      } catch (error) {
        console.error('Failed to load chart library:', error);
      }
    };
    
    loadChartLibrary();
  }, []);
  
  if (!chartReady) {
    return (
      <div className="flex items-center justify-center w-full h-full">
        <div className="text-gray-500">加载图表中...</div>
      </div>
    );
  }
  
  // 计算总值
  const total = data.reduce((sum, item) => sum + (parseFloat(item[measureField]) || 0), 0);
  
  // 确保总值不为0
  if (total === 0) {
    return (
      <div className="flex items-center justify-center w-full h-full">
        <div className="text-gray-500">无有效数据</div>
      </div>
    );
  }
  
  // 准备饼图数据
  const pieData = data.map((item, index) => {
    const value = parseFloat(item[measureField]) || 0;
    const percentage = value / total;
    return {
      ...item,
      value,
      percentage,
      color: getColorByIndex(index, config.colors),
    };
  });
  
  // 绘制饼图扇区
  const sectors = [];
  let startAngle = 0;
  
  pieData.forEach((item, index) => {
    const angle = item.percentage * Math.PI * 2;
    const endAngle = startAngle + angle;
    
    // 计算扇区路径
    const x1 = centerX + innerRadius * Math.cos(startAngle);
    const y1 = centerY + innerRadius * Math.sin(startAngle);
    const x2 = centerX + outerRadius * Math.cos(startAngle);
    const y2 = centerY + outerRadius * Math.sin(startAngle);
    const x3 = centerX + outerRadius * Math.cos(endAngle);
    const y3 = centerY + outerRadius * Math.sin(endAngle);
    const x4 = centerX + innerRadius * Math.cos(endAngle);
    const y4 = centerY + innerRadius * Math.sin(endAngle);
    
    // 大弧标志
    const largeArcFlag = angle > Math.PI ? 1 : 0;
    
    // 构建路径
    let path;
    if (isDonut) {
      path = `M ${x2} ${y2} A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${x3} ${y3} L ${x4} ${y4} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x1} ${y1} Z`;
    } else {
      path = `M ${centerX} ${centerY} L ${x2} ${y2} A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${x3} ${y3} Z`;
    }
    
    // 计算标签位置 (在扇区中心)
    const labelAngle = startAngle + angle / 2;
    const labelRadius = outerRadius * 0.7;
    const labelX = centerX + labelRadius * Math.cos(labelAngle);
    const labelY = centerY + labelRadius * Math.sin(labelAngle);
    
    // 添加扇区
    sectors.push({
      path,
      color: item.color,
      labelX,
      labelY,
      item,
      startAngle,
      endAngle,
    });
    
    // 更新起始角度
    startAngle = endAngle;
  });
  
  return (
    <div className="pie-chart w-full h-full relative">
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        {/* 绘制饼图扇区 */}
        {sectors.map((sector, i) => (
          <g key={i}>
            <path
              d={sector.path}
              fill={sector.color}
              stroke="white"
              strokeWidth="1"
              onClick={(e) => handleDataPointClick?.(sector.item, e as React.MouseEvent)}
              onMouseEnter={(e) => handleHover?.(sector.item, e as React.MouseEvent)}
              onMouseLeave={(e) => handleHover?.(null, e as React.MouseEvent)}
              style={{ cursor: 'pointer' }}
            />
            
            {/* 如果扇区足够大，显示标签 */}
            {sector.item.percentage > 0.05 && config.showLabels && (
              <text
                x={sector.labelX}
                y={sector.labelY}
                textAnchor="middle"
                fill="white"
                fontSize="10"
                fontWeight="bold"
              >
                {(sector.item.percentage * 100).toFixed(1)}%
              </text>
            )}
          </g>
        ))}
        
        {/* 中心文本 (对于环形图) */}
        {isDonut && config.centerText && (
          <text
            x={centerX}
            y={centerY}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="16"
            fontWeight="bold"
            fill="#333"
          >
            {config.centerText}
          </text>
        )}
      </svg>
      
      {/* 图例 */}
      <div className="pie-legend absolute right-0 top-0 p-2">
        {pieData.map((item, i) => (
          <div key={i} className="flex items-center mb-1">
            <div 
              className="w-3 h-3 mr-1" 
              style={{ backgroundColor: item.color }}
            ></div>
            <span className="text-xs">
              {item[dimensionField]}: {(item.percentage * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
      
      {/* 图表注释 */}
      <div className="absolute bottom-0 left-0 right-0 text-center text-xs text-gray-500">
        注意：这是一个示例实现。在实际项目中，应集成专业图表库如 Recharts、Chart.js 或 AntV。
      </div>
    </div>
  );
};

export default PieChart;
