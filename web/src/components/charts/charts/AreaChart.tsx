"use client";

import React, { useEffect, useState } from "react";
import { DataPoint, FieldMapping } from "../types";
import { getColorByIndex } from "../utils/theme";

interface AreaChartProps {
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

const AreaChart: React.FC<AreaChartProps> = ({
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

  // 获取维度和度量字段
  const dimensionField = dimensions[0]?.field;
  const measureField = measures[0]?.field;
  const seriesField = series?.field;

  // 是否为堆叠面积图
  const isStacked = config.stacked === true;

  // 模拟从数据中提取系列组
  const seriesGroups = seriesField
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

  // 提取X轴类别
  const xCategories = [...new Set(data.map((item) => item[dimensionField]))];

  // 计算Y轴最大值
  let maxY = 0;

  if (isStacked) {
    // 对于堆叠面积图，计算每个X类别的累加值
    xCategories.forEach((category) => {
      let sum = 0;
      seriesGroups.forEach((group) => {
        const filtered = data.filter(
          (item) =>
            item[dimensionField] === category &&
            (group === null || item[seriesField] === group)
        );

        if (filtered.length) {
          sum += parseFloat(filtered[0][measureField]) || 0;
        }
      });
      maxY = Math.max(maxY, sum);
    });
  } else {
    // 对于普通面积图，找出所有度量值的最大值
    maxY = Math.max(...data.map((item) => parseFloat(item[measureField]) || 0));
  }

  // 确保最大值不为0
  maxY = maxY || 1;

  // 图表绘制区域
  const plotLeft = 40;
  const plotRight = width - 20;
  const plotTop = 20;
  const plotBottom = height - 40;
  const plotWidth = plotRight - plotLeft;
  const plotHeight = plotBottom - plotTop;

  // 透明度
  const fillOpacity = config.fillOpacity || 0.5;

  return (
    <div className="area-chart w-full h-full relative">
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

        {/* 绘制面积图 */}
        {isStacked
          ? // 堆叠面积图实现
            (() => {
              // 保存每个X类别的累积值
              const stackedValues: Record<string, number> = {};
              xCategories.forEach((cat) => {
                stackedValues[String(cat)] = 0;
              });

              return seriesGroups.map((group, groupIndex) => {
                // 获取当前系列的颜色
                const color = getColorByIndex(groupIndex, config.colors);

                // 构建区域路径
                const areaPoints: {
                  x: number;
                  y: number;
                  value: number;
                  category: any;
                  data: DataPoint;
                }[] = [];

                xCategories.forEach((category, catIndex) => {
                  // 查找数据点
                  const dataPoint = data.find(
                    (item) =>
                      item[dimensionField] === category &&
                      (group === null || item[seriesField] === group)
                  );

                  const value = dataPoint
                    ? parseFloat(dataPoint[measureField]) || 0
                    : 0;

                  // X坐标 (固定)
                  const x =
                    plotLeft +
                    (catIndex / (xCategories.length - 1 || 1)) * plotWidth;

                  // 当前值的底部位置 (基于之前的累积值)
                  const baseY =
                    plotBottom -
                    (stackedValues[String(category)] / maxY) * plotHeight;

                  // 添加当前值到累积值
                  stackedValues[String(category)] += value;

                  // 当前值的顶部位置
                  const y =
                    plotBottom -
                    (stackedValues[String(category)] / maxY) * plotHeight;

                  // 保存点位置
                  areaPoints.push({
                    x,
                    y,
                    value,
                    category,
                    data: dataPoint || ({} as DataPoint),
                  });
                });

                // 构建区域路径
                let areaPath = "";

                // 开始路径
                if (areaPoints.length > 0) {
                  // 起始点 (左下角)
                  areaPath += `M ${areaPoints[0].x} ${plotBottom} `;

                  // 添加底部线连接到第一个数据点的底部
                  const baseY =
                    plotBottom -
                    (stackedValues[String(areaPoints[0].category)] / maxY -
                      areaPoints[0].value / maxY) *
                      plotHeight;
                  areaPath += `L ${areaPoints[0].x} ${baseY} `;

                  // 添加所有上方数据点
                  areaPoints.forEach((point) => {
                    areaPath += `L ${point.x} ${point.y} `;
                  });

                  // 添加回到底部的线
                  areaPath += `L ${
                    areaPoints[areaPoints.length - 1].x
                  } ${plotBottom} `;

                  // 闭合路径
                  areaPath += "Z";
                }

                return (
                  <g key={groupIndex}>
                    {/* 区域填充 */}
                    <path
                      d={areaPath}
                      fill={color}
                      fillOpacity={fillOpacity}
                      stroke={color}
                      strokeWidth="1"
                    />

                    {/* 数据点 */}
                    {areaPoints.map((point, i) => (
                      <circle
                        key={i}
                        cx={point.x}
                        cy={point.y}
                        r="4"
                        fill="white"
                        stroke={color}
                        strokeWidth="2"
                        onClick={(e) =>
                          handleDataPointClick?.(
                            point.data,
                            e as React.MouseEvent
                          )
                        }
                        onMouseEnter={(e) =>
                          handleHover?.(point.data, e as React.MouseEvent)
                        }
                        onMouseLeave={(e) =>
                          handleHover?.(null, e as React.MouseEvent)
                        }
                        style={{ cursor: "pointer" }}
                      />
                    ))}

                    {/* 图例 */}
                    {seriesField && group && (
                      <g
                        transform={`translate(${plotRight - 100}, ${
                          plotTop + groupIndex * 20
                        })`}
                      >
                        <rect
                          width="10"
                          height="10"
                          fill={color}
                          fillOpacity={fillOpacity}
                        />
                        <text x="15" y="9" fontSize="10" fill="#666">
                          {String(group)}
                        </text>
                      </g>
                    )}
                  </g>
                );
              });
            })()
          : // 普通面积图实现
            seriesGroups.map((group, groupIndex) => {
              // 获取当前系列的数据
              let seriesData = data;
              if (seriesField && group !== null) {
                seriesData = data.filter((item) => item[seriesField] === group);
              }

              // 按X轴维度值排序
              seriesData = [...seriesData].sort((a, b) => {
                return (
                  xCategories.indexOf(a[dimensionField]) -
                  xCategories.indexOf(b[dimensionField])
                );
              });

              // 获取当前系列的颜色
              const color = getColorByIndex(groupIndex, config.colors);

              // 构建线和区域路径
              const points = seriesData.map((item, i) => {
                const xIndex = xCategories.indexOf(item[dimensionField]);
                const x =
                  plotLeft +
                  (xIndex / (xCategories.length - 1 || 1)) * plotWidth;
                const y =
                  plotBottom -
                  ((parseFloat(item[measureField]) || 0) / maxY) * plotHeight;
                return { x, y, data: item };
              });

              // 创建线路径
              const linePath = points
                .map((point, i) => {
                  return `${i === 0 ? "M" : "L"} ${point.x} ${point.y}`;
                })
                .join(" ");

              // 创建区域路径
              let areaPath = "";
              if (points.length > 0) {
                areaPath += linePath;
                areaPath += ` L ${points[points.length - 1].x} ${plotBottom}`;
                areaPath += ` L ${points[0].x} ${plotBottom}`;
                areaPath += " Z";
              }

              return (
                <g key={groupIndex}>
                  {/* 区域填充 */}
                  <path
                    d={areaPath}
                    fill={color}
                    fillOpacity={fillOpacity}
                    stroke="none"
                  />

                  {/* 线 */}
                  <path
                    d={linePath}
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                  />

                  {/* 数据点 */}
                  {points.map((point, i) => (
                    <circle
                      key={i}
                      cx={point.x}
                      cy={point.y}
                      r="4"
                      fill="white"
                      stroke={color}
                      strokeWidth="2"
                      onClick={(e) =>
                        handleDataPointClick?.(
                          point.data,
                          e as React.MouseEvent
                        )
                      }
                      onMouseEnter={(e) =>
                        handleHover?.(point.data, e as React.MouseEvent)
                      }
                      onMouseLeave={(e) =>
                        handleHover?.(null, e as React.MouseEvent)
                      }
                      style={{ cursor: "pointer" }}
                    />
                  ))}

                  {/* 图例 */}
                  {seriesField && group && (
                    <g
                      transform={`translate(${plotRight - 100}, ${
                        plotTop + groupIndex * 20
                      })`}
                    >
                      <rect
                        width="10"
                        height="10"
                        fill={color}
                        fillOpacity={fillOpacity}
                      />
                      <text x="15" y="9" fontSize="10" fill="#666">
                        {String(group)}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}

        {/* X轴标签 */}
        {xCategories.map((category, i) => {
          const x = plotLeft + (i / (xCategories.length - 1 || 1)) * plotWidth;
          return (
            <text
              key={i}
              x={x}
              y={plotBottom + 15}
              textAnchor="middle"
              fontSize="10"
              fill="#666"
            >
              {String(category)}
            </text>
          );
        })}
      </svg>

      {/* 图表注释 */}
      <div className="absolute bottom-0 left-0 right-0 text-center text-xs text-gray-500"></div>
    </div>
  );
};

export default AreaChart;
