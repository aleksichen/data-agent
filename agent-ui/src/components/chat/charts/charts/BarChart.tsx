'use client'

import React, { useEffect, useState } from 'react'
import { DataPoint, FieldMapping } from '../types'
import { getColorByIndex } from '../utils/theme'

interface BarChartProps {
  data: DataPoint[]
  dimensions: FieldMapping[]
  measures: FieldMapping[]
  series?: FieldMapping
  config?: any
  width?: number
  height?: number
  handleDataPointClick?: (point: DataPoint, event: React.MouseEvent) => void
  handleHover?: (point: DataPoint | null, event: React.MouseEvent) => void
}

const BarChart: React.FC<BarChartProps> = ({
  data,
  dimensions,
  measures,
  series,
  config = {},
  width = 400,
  height = 300,
  handleDataPointClick,
  handleHover
}) => {
  const [chartReady, setChartReady] = useState(false)

  // 获取维度和度量字段
  const dimensionField = dimensions[0]?.field
  const measureField = measures[0]?.field
  const seriesField = series?.field

  // 模拟从数据中提取维度类别和系列
  const categories = [...new Set(data.map((item) => item[dimensionField]))]
  const seriesValues = seriesField
    ? [...new Set(data.map((item) => item[seriesField]))]
    : [null]

  // 是否为堆叠图
  const isStacked = config.groupMode === 'stacked'

  useEffect(() => {
    // 在实际项目中，这里会导入和初始化图表库
    const loadChartLibrary = async () => {
      try {
        // 实际应用中，我们会在这里导入图表库，如 recharts, chart.js 等
        // const ChartLibrary = await import('chart-library');

        // 模拟加载延迟
        setTimeout(() => {
          setChartReady(true)
        }, 300)
      } catch (error) {
        console.error('Failed to load chart library:', error)
      }
    }

    loadChartLibrary()
  }, [])

  if (!chartReady) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <div className="text-gray-500">加载图表中...</div>
      </div>
    )
  }

  // 计算最大值以便比例尺
  let maxValue = 0
  if (isStacked) {
    // 对于堆叠图，计算每个类别的总和
    categories.forEach((category) => {
      const categoryData = data.filter(
        (item) => item[dimensionField] === category
      )
      const sum = categoryData.reduce(
        (acc, item) => acc + (parseFloat(item[measureField]) || 0),
        0
      )
      maxValue = Math.max(maxValue, sum)
    })
  } else {
    // 对于分组图，找出最大值
    maxValue = Math.max(
      ...data.map((item) => parseFloat(item[measureField]) || 0)
    )
  }

  // 确保最大值不为0
  maxValue = maxValue || 1

  // 计算柱状图布局
  const barPadding = 0.2
  const groupWidth = (width - 60) / categories.length
  const barWidth =
    seriesField && !isStacked
      ? (groupWidth * (1 - barPadding)) / seriesValues.length
      : groupWidth * (1 - barPadding)

  // 这是一个简单的图表模拟，实际项目中会使用真实的图表库
  return (
    <div className="bar-chart relative h-full w-full">
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        {/* 坐标轴 */}
        <line
          x1="40"
          y1={height - 40}
          x2={width - 20}
          y2={height - 40}
          stroke="#ccc"
          strokeWidth="1"
        />
        <line
          x1="40"
          y1="20"
          x2="40"
          y2={height - 40}
          stroke="#ccc"
          strokeWidth="1"
        />

        {/* 绘制柱状图 */}
        {categories.map((category, categoryIndex) => {
          const categoryX =
            40 + categoryIndex * groupWidth + (groupWidth * barPadding) / 2

          // 对于堆叠图的累计值
          let stackedValue = 0

          return (
            <g key={categoryIndex}>
              {seriesValues.map((seriesValue, seriesIndex) => {
                // 筛选当前类别和系列的数据
                let barData = data.filter(
                  (item) => item[dimensionField] === category
                )
                if (seriesField && seriesValue !== null) {
                  barData = barData.filter(
                    (item) => item[seriesField] === seriesValue
                  )
                }

                if (!barData.length) return null

                // 获取值
                const value = parseFloat(barData[0][measureField]) || 0

                // 计算柱子位置和高度
                let barX, barY, barHeight

                if (isStacked) {
                  // 堆叠图
                  barX = categoryX
                  barHeight = (value / maxValue) * (height - 60)
                  barY = height - 40 - barHeight - stackedValue
                  stackedValue += barHeight
                } else {
                  // 分组图
                  barX = categoryX + seriesIndex * barWidth
                  barHeight = (value / maxValue) * (height - 60)
                  barY = height - 40 - barHeight
                }

                // 获取系列颜色
                const color = getColorByIndex(seriesIndex, config.colors)

                return (
                  <g key={seriesIndex}>
                    {/* 绘制柱子 */}
                    <rect
                      x={barX}
                      y={barY}
                      width={barWidth}
                      height={barHeight}
                      fill={color}
                      onClick={(e) =>
                        handleDataPointClick?.(
                          barData[0],
                          e as React.MouseEvent
                        )
                      }
                      onMouseEnter={(e) =>
                        handleHover?.(barData[0], e as React.MouseEvent)
                      }
                      onMouseLeave={(e) =>
                        handleHover?.(null, e as React.MouseEvent)
                      }
                      style={{ cursor: 'pointer' }}
                    />

                    {/* 显示数值 */}
                    {config.showValues && (
                      <text
                        x={barX + barWidth / 2}
                        y={barY - 5}
                        textAnchor="middle"
                        fontSize="10"
                        fill="#666"
                      >
                        {value}
                      </text>
                    )}
                  </g>
                )
              })}
            </g>
          )
        })}

        {/* X轴标签 */}
        {categories.map((category, i) => {
          const x = 40 + i * groupWidth + groupWidth / 2
          return (
            <text
              key={i}
              x={x}
              y={height - 20}
              textAnchor="middle"
              fontSize="10"
              fill="#666"
            >
              {String(category)}
            </text>
          )
        })}

        {/* 图例 */}
        {seriesField && (
          <g className="legend">
            {seriesValues.map((value, i) => {
              const color = getColorByIndex(i, config.colors)
              return (
                <g
                  key={i}
                  transform={`translate(${width - 100}, ${20 + i * 20})`}
                >
                  <rect width="10" height="10" fill={color} />
                  <text x="15" y="9" fontSize="10" fill="#666">
                    {String(value)}
                  </text>
                </g>
              )
            })}
          </g>
        )}
      </svg>

      {/* 图表注释 */}
      <div className="absolute bottom-0 left-0 right-0 text-center text-xs text-gray-500"></div>
    </div>
  )
}

export default BarChart
