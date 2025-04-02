'use client'

import React from 'react'
import { registry } from './registry'
import { ChartType, DataPoint, FieldMapping } from './types'

interface ChartRendererProps {
  type: ChartType | string
  data: DataPoint[]
  dimensions: FieldMapping[]
  measures: FieldMapping[]
  series?: FieldMapping
  config?: any
  width?: number
  height?: number
  [key: string]: any
}

const ChartRenderer: React.FC<ChartRendererProps> = ({
  type,
  data,
  dimensions,
  measures,
  series,
  config,
  width,
  height,
  ...rest
}) => {
  // 从注册表中获取正确的图表组件
  const ChartComponent = registry[type as ChartType]

  if (!ChartComponent) {
    return (
      <div
        className="chart-error flex h-full w-full items-center justify-center rounded-md border border-red-200 bg-red-50 p-4 text-red-700"
        style={{ minHeight: '200px' }}
      >
        <div className="text-center">
          <p className="text-lg font-semibold">图表类型不支持</p>
          <p className="mt-1 text-sm">{`类型 "${type}" 未注册`}</p>
        </div>
      </div>
    )
  }

  // 没有数据的情况
  if (!data || data.length === 0) {
    return (
      <div
        className="chart-no-data flex h-full w-full items-center justify-center rounded-md border border-gray-200 bg-gray-50 p-4 text-gray-500"
        style={{ minHeight: '200px' }}
      >
        <div className="text-center">
          <p className="text-lg font-semibold">暂无数据</p>
        </div>
      </div>
    )
  }

  // 渲染正确类型的图表
  return (
    <ChartComponent
      data={data}
      dimensions={dimensions}
      measures={measures}
      series={series}
      config={config}
      width={width}
      height={height}
      {...rest}
    />
  )
}

export default ChartRenderer
