import { NextRequest, NextResponse } from 'next/server';
import prisma from '@/lib/prisma';

// 类型定义
interface ChartDataSource {
  table: string;
  field: string[];
}

interface ChartDimension {
  field: string;
  name: string;
}

interface ChartMeasure {
  field: string;
  name: string;
}

interface ChartSeries {
  field: string;
  name: string;
}

interface ChartConfig {
  dataSource: ChartDataSource;
  dimensions?: ChartDimension[];
  measures?: ChartMeasure[];
  series?: ChartSeries;
  config?: Record<string, any>;
}

export async function POST(request: NextRequest) {
  try {
    const chartConfig: ChartConfig = await request.json();
    
    if (!chartConfig || !chartConfig.dataSource || !chartConfig.dataSource.table) {
      return NextResponse.json(
        { error: "Invalid chart configuration" },
        { status: 400 }
      );
    }

    const { table, field } = chartConfig.dataSource;
    const dimensions = chartConfig.dimensions?.map(d => d.field) || [];
    const measures = chartConfig.measures?.map(m => m.field) || [];
    const seriesField = chartConfig.series?.field;
    
    // 检查表名是否有效（安全检查）
    if (!isValidTableName(table)) {
      return NextResponse.json(
        { error: "Invalid table name" },
        { status: 400 }
      );
    }
    
    // 检查所有字段名是否有效
    const allFields = [...dimensions, ...measures];
    if (seriesField) allFields.push(seriesField);
    
    if (!allFields.every(field => isValidFieldName(field))) {
      return NextResponse.json(
        { error: "Invalid field name" },
        { status: 400 }
      );
    }

    // 确认所有请求的字段都包含在dataSource.field中
    const requestedFields = Array.from(new Set(allFields));
    if (!requestedFields.every(f => chartConfig.dataSource.field.includes(f))) {
      return NextResponse.json(
        { error: "Requested field not available in dataSource.field" },
        { status: 400 }
      );
    }

    // 构建动态Prisma查询
    // 因为Prisma不支持完全动态表名，我们需要使用特定于表的方法
    let data;
    
    // 这里我们使用包含分组和聚合的Prisma查询
    // 注意：由于Prisma的限制，我们需要为每张表写单独的处理逻辑
    if (table === 'sale_data_id') {
      // 对于维度的分组
      const groupBy = [...dimensions];
      if (seriesField && !groupBy.includes(seriesField)) {
        groupBy.push(seriesField);
      }
      
      if (groupBy.length === 0) {
        // 如果没有分组维度，执行简单查询
        data = await prisma.sale_data_id.findMany({
          select: requestedFields.reduce((acc, field) => {
            acc[field] = true;
            return acc;
          }, {} as Record<string, boolean>)
        });
      } else {
        // 构建带有聚合的分组查询
        const aggregations: Record<string, any> = {};
        
        // 为每个度量添加聚合计算
        if (measures.length > 0) {
          const sumFields: Record<string, boolean> = {};
          measures.forEach(measure => {
            sumFields[measure] = true;
          });
          
          if (Object.keys(sumFields).length > 0) {
            aggregations._sum = sumFields;
          }
        }
        
        // 执行分组查询
        const rawResults = await prisma.sale_data_id.groupBy({
          by: groupBy,
          ...aggregations,
        });
        
        // 转换结果格式，使聚合值更容易访问
        data = rawResults.map(result => {
          const item: Record<string, any> = {...result};
          
          // 展平聚合结果
          if (result._sum) {
            for (const [key, value] of Object.entries(result._sum)) {
              item[key] = value;
            }
            delete item._sum;
          }
          
          return item;
        });
      }
    } else {
      // 为其他表添加类似的处理逻辑
      return NextResponse.json(
        { error: "Table not supported" },
        { status: 400 }
      );
    }

    return NextResponse.json({ data });
  } catch (error) {
    console.error('Error processing data query:', error);
    return NextResponse.json(
      { error: "Failed to process data query" },
      { status: 500 }
    );
  }
}

// 验证表名以防止SQL注入（简化版）
function isValidTableName(name: string): boolean {
  // 只允许字母、数字和下划线
  return /^[a-zA-Z0-9_]+$/.test(name);
}

// 验证字段名以防止SQL注入（简化版）
function isValidFieldName(name: string): boolean {
  // 只允许字母、数字和下划线
  return /^[a-zA-Z0-9_]+$/.test(name);
}
