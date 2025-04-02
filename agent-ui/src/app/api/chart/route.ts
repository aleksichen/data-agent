import { executeQuery, generateSqlQuery } from "@/lib/db/doris";
import { DataFetchParams } from "@/types/chart";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body: DataFetchParams = await request.json();

    const {
      table,
      fields = [],
      dimensions = [],
      measures = [],
      series = null,
      filters = [],
      groupBy = true,
      limit = 1000,
      orderBy = null,
      timeGranularity = 'day'
    } = body;

    // 基础验证
    if (!table) {
      return NextResponse.json(
        { error: 'Missing required field: table' },
        { status: 400 }
      );
    }

    // 确保fields是数组
    let requiredFields = Array.isArray(fields) ? [...fields] : fields ? [fields] : [];

    // 收集图表所需的所有字段
    const dimensionFields = dimensions.map((d: any) => d.field);
    const measureFields = measures.map((m: any) => m.field);
    const seriesField = series?.field;

    // 确保所有所需字段都包含在请求中
    if (seriesField) requiredFields.push(seriesField);
    requiredFields = [...new Set([...requiredFields, ...dimensionFields, ...measureFields])];

    // 构建高级SQL查询
    let query = '';

    // 如果需要分组聚合 (用于图表)
    if (groupBy && dimensions.length > 0 && measures.length > 0) {
      const selectClauses = [];
      const groupByClauses = [];

      // 处理维度字段
      dimensions.forEach((dim: any) => {
        // 添加处理带空格的字段名
        const fieldName = dim.field.includes(' ') ? `\`${dim.field}\`` : dim.field;

        // 处理日期粒度
        if (fieldName.toLowerCase().includes('date') && timeGranularity) {
          switch (timeGranularity) {
            case 'month':
              selectClauses.push(`DATE_FORMAT(${fieldName}, '%Y-%m') AS \`${dim.field}\``);
              break;
            case 'quarter':
              selectClauses.push(`CONCAT(YEAR(${fieldName}), '-Q', QUARTER(${fieldName})) AS \`${dim.field}\``);
              break;
            // ... 其他情况
            default: // day is default
              selectClauses.push(`${fieldName}`);
          }
        } else {
          selectClauses.push(`${fieldName}`);
        }
        groupByClauses.push(fieldName);
      });

      // 处理系列字段 (如果有)
      if (seriesField) {
        const seriesFieldName = seriesField.includes(' ') ? `\`${seriesField}\`` : seriesField;
        if (!groupByClauses.includes(seriesFieldName)) {
          selectClauses.push(seriesFieldName);
          groupByClauses.push(seriesFieldName);
        }
      }

      // 处理度量字段
      measures.forEach((measure: any) => {
        const fieldName = measure.field.includes(' ') ? `\`${measure.field}\`` : measure.field;
        const aggFunc = measure.aggregation || 'SUM';
        selectClauses.push(`${aggFunc}(${fieldName}) AS \`${measure.field}\``);
      });

      // 构建完整SQL
      query = `SELECT ${selectClauses.join(', ')} FROM ${table}`;

      // 添加过滤条件
      if (filters.length > 0) {
        const whereConditions = filters.map((filter: any) => {
          const { field, operator, value } = filter;
          const fieldName = field.includes(' ') ? `\`${field}\`` : field;
          return `${fieldName} ${operator} ${typeof value === 'string' ? `'${value}'` : value}`;
        });
        query += ` WHERE ${whereConditions.join(' AND ')}`;
      }

      // 添加分组
      if (groupByClauses.length > 0) {
        query += ` GROUP BY ${groupByClauses.join(', ')}`;
      }

      // 添加排序
      if (orderBy) {
        const { field, direction = 'ASC' } = orderBy;
        const fieldName = field.includes(' ') ? `\`${field}\`` : field;
        query += ` ORDER BY ${fieldName} ${direction}`;
      }

      // 添加限制
      if (limit) {
        query += ` LIMIT ${limit}`;
      }
    } else {
      // 简单查询 - 不需要分组
      query = generateSqlQuery(table, requiredFields);

      // 添加过滤条件
      if (filters.length > 0) {
        const whereConditions = filters.map((filter: any) => {
          const { field, operator, value } = filter;
          return `${field} ${operator} ${typeof value === 'string' ? `'${value}'` : value}`;
        });
        query += ` WHERE ${whereConditions.join(' AND ')}`;
      }

      // 添加排序
      if (orderBy) {
        const { field, direction = 'ASC' } = orderBy;
        query += ` ORDER BY ${field} ${direction}`;
      }

      // 添加限制
      if (limit) {
        query += ` LIMIT ${limit}`;
      }
    }

    console.log('Generated SQL:', query); // 添加日志以检查生成的SQL

    // 执行查询
    const data = await executeQuery(query);

    // 返回数据
    return NextResponse.json({
      success: true,
      data,
      metadata: {
        dimensions,
        measures,
        series,
        timeGranularity
      }
    });
  } catch (error) {
    console.error('Error fetching data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch data', details: (error as Error).message },
      { status: 500 }
    );
  }
}