'use client'

import React from 'react'
import { useChartSize } from './hooks'
import { ChartConfig } from './types'

interface ChartContainerProps {
  children: React.ReactNode
  className?: string
  style?: React.CSSProperties
  config?: ChartConfig
  filters?: any[]
  onFilterChange?: (filters: any[]) => void
}

const ChartContainer: React.FC<ChartContainerProps> = ({
  children,
  className,
  style,
  config = {},
  filters,
  onFilterChange
}) => {
  const { width, height, ref } = useChartSize({
    width: config?.width,
    height: config?.height,
    responsive: config?.responsive
  })

  // 计算容器内部内容的边距
  const margin = config?.margin || { top: 10, right: 10, bottom: 10, left: 10 }

  return (
    <div
      ref={ref}
      className={`chart-container ${className || ''}`}
      style={{
        position: 'relative',
        width: config?.width || '100%',
        height: config?.height || '400px',
        background: config?.background || '#ffffff',
        borderRadius: '6px',
        overflow: 'hidden',
        ...style
      }}
    >
      {/* 图表标题 */}
      {config?.title && (
        <div className="chart-title p-3 pb-0">
          <h3 className="text-lg font-semibold text-gray-700">
            {config.title}
          </h3>
          {config?.description && (
            <p className="mt-1 text-sm text-gray-500">{config.description}</p>
          )}
        </div>
      )}

      {/* 可选的筛选器界面 */}
      {config?.showFilters && (
        <div className="chart-filters p-3">
          {/* 筛选器组件 */}
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="font-medium">筛选:</span>
            {filters && filters.length > 0 ? (
              filters.map((filter, index) => (
                <div
                  key={index}
                  className="flex items-center rounded bg-blue-100 px-2 py-1 text-blue-800"
                >
                  <span>
                    {filter.field} {filter.operator} {filter.value}
                  </span>
                  <button
                    className="ml-2 text-blue-500 hover:text-blue-700"
                    onClick={() => {
                      if (onFilterChange) {
                        const newFilters = [...filters]
                        newFilters.splice(index, 1)
                        onFilterChange(newFilters)
                      }
                    }}
                  >
                    ✕
                  </button>
                </div>
              ))
            ) : (
              <span className="text-gray-500">无</span>
            )}
          </div>
        </div>
      )}

      {/* 图表主体内容 */}
      <div
        className="chart-body relative"
        style={{
          padding: `${margin.top}px ${margin.right}px ${margin.bottom}px ${margin.left}px`
        }}
      >
        {React.Children.map(children, (child) => {
          // 将尺寸传递给子组件
          if (React.isValidElement(child)) {
            return React.cloneElement(child, {
              width: width - margin.left - margin.right,
              height:
                height -
                (config?.title ? 60 : 0) -
                (config?.showFilters ? 40 : 0) -
                margin.top -
                margin.bottom
            })
          }
          return child
        })}
      </div>

      {/* 可选的图表附加信息 */}
      {config?.footer && (
        <div className="chart-footer p-3 pt-0 text-sm text-gray-500">
          {config.footer}
        </div>
      )}
    </div>
  )
}

export default ChartContainer
