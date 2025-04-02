'use client'

import React, { useEffect, useState } from 'react'
import ChartContainer from './ChartContainer'
import ChartRenderer from './ChartRenderer'
import { ChartProps } from './types'
import { useChartData, useChartEvents } from './hooks'

const Chart: React.FC<ChartProps> = (props) => {
  const {
    type,
    data: initialData = [],
    dataSource,
    dimensions,
    measures,
    series,
    config = {},
    className,
    style,
    filters,
    customComponents,
    onDataPointClick,
    onHover,
    onBrush,
    ...restProps
  } = props

  const [data, setData] = useState(initialData || [])
  const [loading, setLoading] = useState(!!dataSource)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (dataSource) {
      setLoading(true)
      setError(null)

      fetch('/api/chart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          table: dataSource.table,
          fields: dataSource.fields,
          dimensions,
          measures,
          series,
          filters
        })
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`)
          }
          return response.json()
        })
        .then((result) => {
          if (result.success && Array.isArray(result.data)) {
            setData(result.data)
          } else {
            throw new Error(result.error || 'Invalid data received from API')
          }
        })
        .catch((err) => {
          console.error('Error fetching chart data:', err)
          setError(err.message || 'Failed to fetch chart data')
        })
        .finally(() => {
          setLoading(false)
        })
    }
  }, [dataSource, dimensions, filters, measures, series])

  // 处理和转换数据
  const processedData = useChartData(data, {
    dimensions,
    measures,
    series,
    filters
  })

  // 设置事件处理器
  const eventHandlers = useChartEvents({
    onDataPointClick,
    onHover,
    onBrush
  })

  // 显示加载状态
  if (loading) {
    return (
      <ChartContainer
        className={className}
        style={style}
        config={config}
        filters={filters}
      >
        <div className="flex h-full min-h-[200px] w-full items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-gray-900"></div>
        </div>
      </ChartContainer>
    )
  }

  // 显示错误状态
  if (error) {
    return (
      <ChartContainer
        className={className}
        style={style}
        config={config}
        filters={filters}
      >
        <div className="flex h-full min-h-[200px] w-full items-center justify-center text-red-500">
          <div>Error loading chart data: {error}</div>
        </div>
      </ChartContainer>
    )
  }

  return (
    <ChartContainer
      className={className}
      style={style}
      config={config}
      filters={filters}
    >
      <ChartRenderer
        type={type}
        data={processedData.processedData}
        dimensions={dimensions}
        measures={measures}
        series={series}
        config={config}
        customComponents={customComponents}
        {...eventHandlers}
        {...restProps}
      />
    </ChartContainer>
  )
}

export default Chart
