"use client";

import React, { useState, useEffect } from "react";
import { Chart } from "@/components/charts";
import { DataPoint } from "@/components/charts/types";

export default function DashboardPage() {
  const [salesData, setSalesData] = useState<DataPoint[]>([]);

  useEffect(() => {
    // 模拟数据加载
    // 在实际应用中，这里会从API获取数据
    setSalesData([
      { month: "Jan", sales: 100, profit: 50, category: "A", customers: 120 },
      { month: "Feb", sales: 120, profit: 60, category: "A", customers: 130 },
      { month: "Mar", sales: 140, profit: 70, category: "A", customers: 150 },
      { month: "Apr", sales: 160, profit: 80, category: "A", customers: 170 },
      { month: "May", sales: 180, profit: 90, category: "A", customers: 165 },
      { month: "Jun", sales: 200, profit: 100, category: "A", customers: 180 },
      { month: "Jan", sales: 80, profit: 40, category: "B", customers: 100 },
      { month: "Feb", sales: 90, profit: 45, category: "B", customers: 110 },
      { month: "Mar", sales: 100, profit: 50, category: "B", customers: 120 },
      { month: "Apr", sales: 110, profit: 55, category: "B", customers: 125 },
      { month: "May", sales: 120, profit: 60, category: "B", customers: 130 },
      { month: "Jun", sales: 130, profit: 65, category: "B", customers: 140 },
    ]);
  }, []);

  const handleDataPointClick = (point: DataPoint) => {
    console.log("Data point clicked:", point);
    alert(`${point.month}: Sales ${point.sales}, Profit ${point.profit}`);
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">
          巧克力销售数据仪表板
        </h1>
        <p className="text-gray-600 mt-2">
          使用 dimensions、measures 和 series 模型展示同一数据集的多种可视化方式
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* 折线图 */}
        <div className="bg-white rounded-lg shadow">
          <Chart
            type="line"
            dataSource={{
              table: "db.sales_data",
              field: ["month", "profit", "category"],
            }}
            dimensions={[{ field: "month", name: "月份" }]}
            measures={[{ field: "sales", name: "销售额" }]}
            series={{ field: "category", name: "类别" }}
            config={{
              title: "月度销售趋势",
              height: 350,
              colors: ["#4e79a7", "#f28e2c"],
            }}
            onDataPointClick={handleDataPointClick}
          />

          <Chart
            type="line"
            data={salesData}
            dimensions={[{ field: "month", name: "月份" }]}
            measures={[{ field: "sales", name: "销售额" }]}
            series={{ field: "category", name: "类别" }}
            config={{
              title: "月度销售趋势",
              height: 350,
              colors: ["#4e79a7", "#f28e2c"],
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>

        {/* 柱状图 */}
        <div className="bg-white rounded-lg shadow">
          <Chart
            type="bar"
            data={salesData}
            dimensions={[{ field: "month", name: "月份" }]}
            measures={[{ field: "profit", name: "利润" }]}
            series={{ field: "category", name: "类别" }}
            config={{
              title: "月度利润对比",
              height: 350,
              colors: ["#59a14f", "#e15759"],
              groupMode: "grouped",
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* 饼图 */}
        <div className="bg-white rounded-lg shadow">
          <Chart
            type="pie"
            data={salesData.filter((d) => d.month === "Jun")}
            dimensions={[{ field: "category", name: "类别" }]}
            measures={[{ field: "sales", name: "销售额" }]}
            config={{
              title: "六月销售额分布",
              height: 300,
              donut: true,
              centerText: "销售额",
              colors: ["#4e79a7", "#f28e2c", "#e15759", "#76b7b2"],
              showLabels: true,
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>

        {/* 散点图 */}
        <div className="bg-white rounded-lg shadow">
          <Chart
            type="scatter"
            data={salesData}
            dimensions={[{ field: "sales", name: "销售额" }]}
            measures={[{ field: "profit", name: "利润" }]}
            series={{ field: "category", name: "类别" }}
            config={{
              title: "销售额 vs 利润",
              height: 300,
              colors: ["#af7aa1", "#ff9da7"],
              sizeField: "customers",
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>

        {/* 面积图 */}
        <div className="bg-white rounded-lg shadow">
          <Chart
            type="area"
            data={salesData}
            dimensions={[{ field: "month", name: "月份" }]}
            measures={[{ field: "customers", name: "客户数" }]}
            series={{ field: "category", name: "类别" }}
            config={{
              title: "客户数趋势",
              height: 300,
              colors: ["#76b7b2", "#edc949"],
              stacked: true,
              fillOpacity: 0.7,
            }}
            onDataPointClick={handleDataPointClick}
          />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">堆叠柱状图</h2>
        <Chart
          type="bar"
          data={salesData}
          dimensions={[{ field: "month", name: "月份" }]}
          measures={[{ field: "sales", name: "销售额" }]}
          series={{ field: "category", name: "类别" }}
          config={{
            height: 400,
            colors: ["#4e79a7", "#f28e2c"],
            groupMode: "stacked",
            showValues: true,
          }}
          onDataPointClick={handleDataPointClick}
        />
      </div>

      <footer className="text-center text-gray-500 text-sm mt-8">
        <p>基于 dimensions、measures 和 series 的通用图表 SDK 演示</p>
        <p className="mt-1">
          这些图表都使用相同的数据集，但通过不同的映射方式展示不同的视角
        </p>
      </footer>
    </div>
  );
}
