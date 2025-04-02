/**
 * Doris database connection utility
 * This file provides functionality to connect to and query the Doris database
 */

import mysql from 'mysql2/promise';

// Configuration should be loaded from environment variables in production
const dorisConfig = {
  host: '192.168.50.97',
  port: 30930,
  database: 'wedata',
  user: 'root',
  password: '',
  connectionLimit: 10, // 降低限制
  acquireTimeout: 10000, // 10秒内如果无法获取连接则超时
  idleTimeout: 60000, // 空闲连接60秒后自动关闭
  enableKeepAlive: true, // 启用保持连接活跃
  keepAliveInitialDelay: 30000, // 30秒后发送保持活跃信号
};

// Create a connection pool for Doris
// We use MySQL client as Doris is compatible with MySQL protocol
const pool = mysql.createPool(dorisConfig);

/**
 * Execute a SQL query against the Doris database
 * @param query SQL query string
 * @param params Query parameters
 * @returns Query result
 */
export async function executeQuery(query: string, params: unknown[] = []): Promise<any> {
  let connection;
  try {
    connection = await pool.getConnection();
    const [rows] = await connection.query(query, params);
    return rows;
  } catch (error) {
    console.error('Database query error:', error);
    throw error;
  } finally {
    if (connection) {
      try {
        connection.release();
      } catch (err) {
        console.error('Error releasing connection:', err);
      }
    }
  }
}

/**
 * Generate a SQL query for chart data
 * @param table Table name
 * @param fields Array of field names
 * @returns SQL query string
 */
export function generateSqlQuery(table: string, fields: string[]): string {
  // 检查是否需要查询所有列
  if (fields.length === 0 || (fields.length === 1 && fields[0] === '*')) {
    return `SELECT * FROM ${table}`;
  }

  // 正确处理包含空格的字段名
  const escapedFields = fields.map(field => `\`${field}\``).join(', ');

  return `SELECT ${escapedFields} FROM ${table}`;
}

/**
 * Validate that fields exist in the specified table
 * @param table Table name
 * @param fields Array of field names
 * @returns Promise resolving to boolean indicating if fields are valid
 */
export async function validateFields(table: string, fields: string[]): Promise<boolean> {
  try {
    // Get table schema
    const schema = await executeQuery(
      'DESCRIBE `' + table + '`'
    );

    // Extract field names from schema
    const tableFields = schema.map((row: any) => row.Field);

    // Check if all requested fields exist in the table
    return fields.every(field => tableFields.includes(field));
  } catch (error) {
    console.error('Error validating fields:', error);
    return false;
  }
}