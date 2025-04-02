"use client";

import React, { useEffect, useState } from "react";
import { DataPoint, FieldMapping } from "../types";
import { getColorByIndex } from "../utils/theme";

interface ScatterChartProps {
  data: DataPoint[];
  dimensions: FieldMapping[];
  measures: FieldMapping[];
  series?: FieldMapping;
  config?: any;
  width?: number;
  height?: number;
  handleDataPointClick?: (point: DataPoint, event: React.MouseEvent) => void;
  handleHover?: (point: DataPoint | null, event: React.MouseEvent) => void;
}

const ScatterChart: React.FC<ScatterChartProps> = ({
  data,
  dimensions,
  measures,
  series,
  config = {},
  width = 400,
  height = 300,
  handleDataPointClick,
  handleHover,
}) => {
  const [chartReady, setChartReady] = useState(false);

  // 对于散点图，我们使用第一个维度作为X轴，第一个度量作为Y轴
  const xField = dimensions[0]?.field;
  const yField = measures[0]?.field;
  const seriesField = series?.field;

  // 点大小字段 (可选)
  const sizeField = config.sizeField || measures[1]?.field;

  // 模拟从数据中提取系列
  const seriesValues = seriesField
    ? [...new Set(data.map((item) => item[seriesField]))]
    : [null];

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
        console.error("Failed to load chart library:", error);
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

  // 计算x和y的范围
  const xValues = data.map((item) => parseFloat(item[xField]) || 0);
  const yValues = data.map((item) => parseFloat(item[yField]) || 0);

  const xMin = config.xAxis?.min ?? Math.min(...xValues);
  const xMax = config.xAxis?.max ?? Math.max(...xValues);
  const yMin = config.yAxis?.min ?? Math.min(...yValues);
  const yMax = config.yAxis?.max ?? Math.max(...yValues);

  // 计算点大小范围 (如果指定了大小字段)
  let sizeMin = 4;
  let sizeMax = 20;
  let sizeValues: number[] = [];

  if (sizeField) {
    sizeValues = data.map((item) => parseFloat(item[sizeField]) || 0);
    const minSize = Math.min(...sizeValues);
    const maxSize = Math.max(...sizeValues);

    if (minSize !== maxSize) {
      // 计算点大小比例
      sizeValues = sizeValues.map((val) => {
        const sizeRatio = (val - minSize) / (maxSize - minSize);
        return sizeMin + sizeRatio * (sizeMax - sizeMin);
      });
    }
  }

  // 图表绘制区域
  const plotLeft = 50;
  const plotRight = width - 20;
  const plotTop = 20;
  const plotBottom = height - 50;
  const plotWidth = plotRight - plotLeft;
  const plotHeight = plotBottom - plotTop;

  return (
    <div className="scatter-chart w-full h-full relative">
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        {/* 坐标轴 */}
        <line
          x1={plotLeft}
          y1={plotBottom}
          x2={plotRight}
          y2={plotBottom}
          stroke="#ccc"
          strokeWidth="1"
        />
        <line
          x1={plotLeft}
          y1={plotTop}
          x2={plotLeft}
          y2={plotBottom}
          stroke="#ccc"
          strokeWidth="1"
        />

        {/* X轴标签 */}
        <text
          x={width / 2}
          y={height - 10}
          textAnchor="middle"
          fontSize="12"
          fill="#666"
        >
          {dimensions[0]?.name || dimensions[0]?.field}
        </text>

        {/* Y轴标签 */}
        <text
          x={10}
          y={height / 2}
          textAnchor="middle"
          fontSize="12"
          fill="#666"
          transform={`rotate(-90, 10, ${height / 2})`}
        >
          {measures[0]?.name || measures[0]?.field}
        </text>

        {/* 绘制点 */}
        {seriesValues.map((seriesValue, seriesIndex) => {
          // 筛选当前系列的数据
          let seriesData = data;
          if (seriesField && seriesValue !== null) {
            seriesData = data.filter(
              (item) => item[seriesField] === seriesValue
            );
          }

          // 获取系列颜色
          const color = getColorByIndex(seriesIndex, config.colors);

          return (
            <g key={seriesIndex}>
              {seriesData.map((item, i) => {
                // 获取x和y值
                const xVal = parseFloat(item[xField]) || 0;
                const yVal = parseFloat(item[yField]) || 0;

                // 计算点的位置
                const x =
                  plotLeft + ((xVal - xMin) / (xMax - xMin)) * plotWidth;
                const y =
                  plotBottom - ((yVal - yMin) / (yMax - yMin)) * plotHeight;

                // 计算点的大小
                const size = sizeField ? sizeValues[data.indexOf(item)] : 5;

                return (
                  <circle
                    key={i}
                    cx={x}
                    cy={y}
                    r={size}
                    fill={color}
                    opacity={0.7}
                    stroke="white"
                    strokeWidth="1"
                    onClick={(e) =>
                      handleDataPointClick?.(item, e as React.MouseEvent)
                    }
                    onMouseEnter={(e) =>
                      handleHover?.(item, e as React.MouseEvent)
                    }
                    onMouseLeave={(e) =>
                      handleHover?.(null, e as React.MouseEvent)
                    }
                    style={{ cursor: "pointer" }}
                  />
                );
              })}

              {/* 系列图例 */}
              {seriesField && seriesValue && (
                <g
                  transform={`translate(${plotRight - 100}, ${
                    plotTop + seriesIndex * 20
                  })`}
                >
                  <circle cx={5} cy={5} r={5} fill={color} />
                  <text x={15} y={9} fontSize="10" fill="#666">
                    {String(seriesValue)}
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>

      {/* 图表注释 */}
      <div className="absolute bottom-0 left-0 right-0 text-center text-xs text-gray-500">
        注意：这是一个示例实现。在实际项目中，应集成专业图表库如
        Recharts、Chart.js 或 AntV。
      </div>
    </div>
  );
};

export default ScatterChart;
// const params = {
//   type: "bar",
//   dataSource: {
//     table: "sale_data_id",
//     field: ["month", "profit", "category"],
//   },
//   dimensions: [{ field: "month", name: "月份" }],
//   measures: [{ field: "profit", name: "利润" }],
//   series: { field: "category", name: "类别" },
//   config: {
//     title: "月度利润对比",

//   },
// };
