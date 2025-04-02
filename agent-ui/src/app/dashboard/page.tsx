'use client'

import React, { useState, useEffect } from 'react'
import { Chart } from '@/components/chat/charts'
import { DataPoint } from '@/components/chat/charts/types'

const data = [
  { month: 'Jan', sales: 100, profit: 50, category: 'A', customers: 120 },
  { month: 'Feb', sales: 120, profit: 60, category: 'A', customers: 130 },
  { month: 'Mar', sales: 140, profit: 70, category: 'A', customers: 150 },
  { month: 'Apr', sales: 160, profit: 80, category: 'A', customers: 170 },
  { month: 'May', sales: 180, profit: 90, category: 'A', customers: 165 },
  { month: 'Jun', sales: 200, profit: 100, category: 'A', customers: 180 },
  { month: 'Jan', sales: 80, profit: 40, category: 'B', customers: 100 },
  { month: 'Feb', sales: 90, profit: 45, category: 'B', customers: 110 },
  { month: 'Mar', sales: 100, profit: 50, category: 'B', customers: 120 },
  { month: 'Apr', sales: 110, profit: 55, category: 'B', customers: 125 },
  { month: 'May', sales: 120, profit: 60, category: 'B', customers: 130 },
  { month: 'Jun', sales: 130, profit: 65, category: 'B', customers: 140 }
]

export default function DashboardPage() {
  const [salesData, setSalesData] = useState<DataPoint[]>(data)

  useEffect(() => {
    // 模拟数据加载
    // 在实际应用中，这里会从API获取数据
    setSalesData([
      { month: 'Jan', sales: 100, profit: 50, category: 'A', customers: 120 },
      { month: 'Feb', sales: 120, profit: 60, category: 'A', customers: 130 },
      { month: 'Mar', sales: 140, profit: 70, category: 'A', customers: 150 },
      { month: 'Apr', sales: 160, profit: 80, category: 'A', customers: 170 },
      { month: 'May', sales: 180, profit: 90, category: 'A', customers: 165 },
      { month: 'Jun', sales: 200, profit: 100, category: 'A', customers: 180 },
      { month: 'Jan', sales: 80, profit: 40, category: 'B', customers: 100 },
      { month: 'Feb', sales: 90, profit: 45, category: 'B', customers: 110 },
      { month: 'Mar', sales: 100, profit: 50, category: 'B', customers: 120 },
      { month: 'Apr', sales: 110, profit: 55, category: 'B', customers: 125 },
      { month: 'May', sales: 120, profit: 60, category: 'B', customers: 130 },
      { month: 'Jun', sales: 130, profit: 65, category: 'B', customers: 140 }
    ])
  }, [])

  const handleDataPointClick = (point: DataPoint) => {
    console.log('Data point clicked:', point)
    alert(`${point.month}: Sales ${point.sales}, Profit ${point.profit}`)
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">
          巧克力销售数据仪表板
        </h1>
        <p className="mt-2 text-gray-600">
          使用 dimensions、measures 和 series 模型展示同一数据集的多种可视化方式
        </p>
      </header>

      <div className="mb-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* 折线图 */}
        <div className="rounded-lg bg-white shadow">
          <Chart
            type="line"
            dataSource={{
              table: 'wedata.chocolate_sales',
              fields: ['Date', 'Amount', 'Product']
            }}
            dimensions={[{ field: 'Date', name: '日' }]}
            measures={[{ field: 'Amount', name: '销售额', aggregate: 'sum' }]}
            series={{ field: 'Product', name: '产品' }}
            config={{
              title: '月度销售趋势',
              height: 350,
              colors: ['#4e79a7', '#f28e2c']
            }}
            onDataPointClick={handleDataPointClick}
          />

          <Chart
            type="line"
            data={salesData}
            dimensions={[{ field: 'month', name: '月份' }]}
            measures={[{ field: 'sales', name: '销售额' }]}
            series={{ field: 'category', name: '类别' }}
            config={{
              title: '月度销售趋势',
              height: 350,
              colors: ['#4e79a7', '#f28e2c']
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>

        {/* 柱状图 */}
        <div className="rounded-lg bg-white shadow">
          <Chart
            type="bar"
            data={salesData}
            dimensions={[{ field: 'month', name: '月份' }]}
            measures={[{ field: 'profit', name: '利润' }]}
            series={{ field: 'category', name: '类别' }}
            config={{
              title: '月度利润对比',
              height: 350,
              colors: ['#59a14f', '#e15759'],
              groupMode: 'grouped'
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* 饼图 */}
        <div className="rounded-lg bg-white shadow">
          <Chart
            type="pie"
            data={salesData.filter((d) => d.month === 'Jun')}
            dimensions={[{ field: 'category', name: '类别' }]}
            measures={[{ field: 'sales', name: '销售额' }]}
            config={{
              title: '六月销售额分布',
              height: 300,
              donut: true,
              centerText: '销售额',
              colors: ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2'],
              showLabels: true
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>

        {/* 散点图 */}
        <div className="rounded-lg bg-white shadow">
          <Chart
            type="scatter"
            data={salesData}
            dimensions={[{ field: 'sales', name: '销售额' }]}
            measures={[{ field: 'profit', name: '利润' }]}
            series={{ field: 'category', name: '类别' }}
            config={{
              title: '销售额 vs 利润',
              height: 300,
              colors: ['#af7aa1', '#ff9da7'],
              sizeField: 'customers'
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>

        {/* 面积图 */}
        <div className="rounded-lg bg-white shadow">
          <Chart
            type="area"
            data={salesData}
            dimensions={[{ field: 'month', name: '月份' }]}
            measures={[{ field: 'customers', name: '客户数' }]}
            series={{ field: 'category', name: '类别' }}
            config={{
              title: '客户数趋势',
              height: 300,
              colors: ['#76b7b2', '#edc949'],
              stacked: true,
              fillOpacity: 0.7
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>
      </div>

      <div className="mb-6 rounded-lg bg-white p-6 shadow">
        <h2 className="mb-4 text-xl font-bold">堆叠柱状图</h2>
        <Chart
          type="bar"
          data={salesData}
          dimensions={[{ field: 'month', name: '月份' }]}
          measures={[{ field: 'sales', name: '销售额' }]}
          series={{ field: 'category', name: '类别' }}
          config={{
            height: 400,
            colors: ['#4e79a7', '#f28e2c'],
            groupMode: 'stacked',
            showValues: true
          }}
          onDataPointClick={handleDataPointClick}
        />
      </div>

      <footer className="mt-8 text-center text-sm text-gray-500">
        <p>基于 dimensions、measures 和 series 的通用图表 SDK 演示</p>
        <p className="mt-1">
          这些图表都使用相同的数据集，但通过不同的映射方式展示不同的视角
        </p>
      </footer>
    </div>
  )
}
