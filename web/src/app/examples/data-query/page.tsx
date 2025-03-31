'use client';

import { useState, useEffect } from 'react';
import { fetchChartData, ChartConfig } from '@/lib/api/dataService';

export default function DataQueryExample() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        
        // 示例图表配置
        const chartConfig: ChartConfig = {
          type: "bar",
          dataSource: {
            table: "sale_data_id",
            field: ["month", "profit", "category"],
          },
          dimensions: [{ field: "month", name: "月份" }],
          measures: [{ field: "profit", name: "利润" }],
          series: { field: "category", name: "类别" },
          config: {
            title: "月度利润对比",
          },
        };
        
        const chartData = await fetchChartData(chartConfig);
        setData(chartData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error occurred');
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, []);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">数据查询示例</h1>
      
      {loading && <p className="text-gray-500">加载中...</p>}
      
      {error && (
        <div className="bg-red-50 p-4 mb-4 rounded border border-red-200">
          <p className="text-red-700">{error}</p>
        </div>
      )}
      
      {!loading && !error && (
        <>
          <h2 className="text-xl mb-4">查询结果</h2>
          
          {data.length === 0 ? (
            <p className="text-gray-500">没有查询到数据</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-200">
                <thead>
                  <tr className="bg-gray-100">
                    {Object.keys(data[0]).map((key) => (
                      <th key={key} className="px-4 py-2 text-left text-sm font-medium text-gray-600 uppercase tracking-wider">
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.map((item, index) => (
                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      {Object.values(item).map((value: any, i) => (
                        <td key={i} className="px-4 py-2 text-sm text-gray-500">
                          {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          
          <div className="mt-8">
            <h3 className="text-lg font-medium mb-2">原始数据</h3>
            <pre className="bg-gray-50 p-4 rounded overflow-auto max-h-96">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        </>
      )}
    </div>
  );
}
