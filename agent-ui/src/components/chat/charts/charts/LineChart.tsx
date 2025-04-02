'use client'

import React, { useEffect, useState } from 'react'
import { Line, LineConfig } from '@ant-design/charts'
import { DataPoint, FieldMapping } from '../types'
import { getColorByIndex } from '../utils/theme'

interface LineChartProps {
  data: DataPoint[]
  dimensions: FieldMapping[]
  measures: FieldMapping[]
  series?: FieldMapping
  config?: Partial<LineConfig>
  width?: number
  height?: number
  handleDataPointClick?: (point: DataPoint, event: React.MouseEvent) => void
  handleHover?: (point: DataPoint | null, event: React.MouseEvent) => void
}

const LineChart: React.FC<LineChartProps> = ({
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

  // 字段类型安全校验
  const dimensionField = dimensions[0]?.field || ''
  const measureField = measures[0]?.field || ''
  const seriesField = series?.field

  // 生成颜色映射（类型安全版）
  const seriesValues = seriesField
    ? ([...new Set(data.map((d) => d[seriesField]))] as string[])
    : []
  const colorMap: Record<string, string> = seriesValues.reduce(
    (acc: Record<string, string>, curr, i) => {
      acc[curr] = getColorByIndex(i)
      return acc
    },
    {}
  )

  // 图表配置（符合LineConfig类型）
  const chartConfig: LineConfig = {
    data,
    xField: dimensionField,
    yField: measureField,
    seriesField,
    width,
    height,
    theme: {
      colors: seriesValues.map((_, i) => getColorByIndex(i))
    },
    point: {
      size: 4,
      style: {
        fill: '#fff',
        stroke: seriesField
          ? (datum: Record<string, unknown>) =>
              colorMap[datum[seriesField] as string] || '#1890ff'
          : '#1890ff',
        lineWidth: 2
      }
    },
    interactions: [{ type: 'tooltip' }],
    ...config
  }

  // 事件处理（类型安全版）
  const eventConfig = {
    onEvent: (
      record: { data?: { data: DataPoint } },
      event: React.MouseEvent
    ) => {
      if (!record.data?.data) return

      switch (event.type) {
        case 'click':
          handleDataPointClick?.(record.data.data, event)
          break
        case 'mouseenter':
          handleHover?.(record.data.data, event)
          break
        case 'mouseleave':
          handleHover?.(null, event)
          break
      }
    }
  }

  useEffect(() => {
    setChartReady(true)
  }, [])

  if (!chartReady) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <div className="text-gray-500">加载图表中...</div>
      </div>
    )
  }

  return <Line {...chartConfig} {...eventConfig} />
}

export default LineChart
