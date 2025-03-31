from typing import Any, Dict, List, Optional, Union
import pandas as pd
import os
import time
import csv

try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:
    raise ImportError(
        "`pymysql` not installed. Please install using `pip install pymysql`."
    )

from agno.tools import Toolkit
from agno.utils.log import log_debug, log_info


class DorisTools(Toolkit):
    """A simple toolkit to connect to Apache Doris database with basic Data Dictionary support.
    
    This tool allows AI agents to query, analyze, and write data to Doris,
    while maintaining a data dictionary to track basic descriptions of tables and columns.
    """

    def __init__(
        self,
        host: str,
        port: int = 9030,
        user: str = "root",
        password: str = "",
        database: str = "",
        read_only: bool = False
    ):
        """Initialize the DorisTools.
        
        Args:
            host: Doris server host
            port: Doris server port (MySQL protocol)
            user: Username for authentication
            password: Password for authentication
            database: Default database to connect to
            read_only: If True, write operations will be disabled
        """
        super().__init__(name="doris_tools")
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.read_only = read_only
        self._connection = None
        
        # Register tools
        self.register(self.query)
        self.register(self.show_tables)
        self.register(self.describe_table)
        self.register(self.analyze_data)
        self.register(self.export_to_csv)
        self.register(self.search_dictionary)
        
        if not read_only:
            self.register(self.insert_data)
            self.register(self.update_data)
            self.register(self.execute_sql)
            self.register(self.save)
        
        # Ensure data dictionary table exists
        self._ensure_data_dictionary_exists()

    @property
    def connection(self) -> pymysql.connections.Connection:
        """Get or create the PyMySQL connection."""
        if self._connection is None:
            self._connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=DictCursor,
                charset='utf8mb4'
            )
            
            # Set session to read-only if specified
            if self.read_only:
                cursor = self._connection.cursor()
                cursor.execute("SET SESSION TRANSACTION READ ONLY;")
                cursor.close()
                
        return self._connection

    def _ensure_connection(self):
        """Ensure the connection is active and reconnect if needed."""
        try:
            self.connection.ping(reconnect=True)
        except:
            self._connection = None
            self.connection  # This will recreate the connection
    
    def _ensure_data_dictionary_exists(self):
        """Ensure data dictionary table exists."""
        if self.read_only:
            log_info("In read-only mode. Cannot create data dictionary table if it doesn't exist.")
            return
        
        try:
            self._ensure_connection()
            cursor = self.connection.cursor()
            
            # Create a simple data dictionary table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS `data_dictionary` (
                `table_name` VARCHAR(255) NOT NULL COMMENT '表名',
                `column_name` VARCHAR(255) NOT NULL COMMENT '列名（表名为表记录，列名为空为表描述）',
                `description` TEXT COMMENT '描述信息',
                `updated_at` DATETIME COMMENT '更新时间'
            ) ENGINE=OLAP
            DUPLICATE KEY(`table_name`, `column_name`)
            DISTRIBUTED BY HASH(`table_name`) BUCKETS 1
            PROPERTIES('replication_num' = '1');
            """)
            
            cursor.close()
            log_info("Data dictionary initialized")
        except Exception as e:
            log_debug(f"Error ensuring data dictionary exists: {str(e)}")

    def query(self, sql: str, as_pandas: bool = True) -> Union[str, pd.DataFrame]:
        """Execute a query and return the results.
        
        Args:
            sql: SQL query to execute
            as_pandas: If True, return a pandas DataFrame (when returning to the agent, will be converted to string)
            
        Returns:
            Query results as a string or DataFrame
        """
        log_info(f"Executing query: {sql}")
        self._ensure_connection()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            
            if sql.strip().upper().startswith(('SELECT', 'SHOW', 'DESC', 'EXPLAIN')):
                result = cursor.fetchall()
                cursor.close()
                
                if not result:
                    return "Query executed successfully, but returned no data."
                
                if as_pandas:
                    df = pd.DataFrame(result)
                    return df if not isinstance(df, str) else "Empty result"
                else:
                    # Format as string
                    if result:
                        # Get column names from first row
                        columns = list(result[0].keys())
                        header = ", ".join(columns)
                        rows = []
                        for row in result:
                            row_values = [str(row.get(col, '')) for col in columns]
                            rows.append(", ".join(row_values))
                        return header + "\n" + "\n".join(rows)
                    return "No data returned"
            else:
                affected_rows = cursor.rowcount
                cursor.close()
                self.connection.commit()
                return f"Query executed successfully. Affected rows: {affected_rows}"
        except Exception as e:
            error_msg = f"Query error: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def show_tables(self) -> str:
        """Show all tables with their descriptions from the data dictionary.
        
        Returns:
            List of tables with descriptions
        """
        try:
            # First check if the data dictionary table exists
            self._ensure_connection()
            cursor = self.connection.cursor()
            
            try:
                cursor.execute("SELECT 1 FROM data_dictionary LIMIT 1")
                dict_exists = True
            except:
                dict_exists = False
            
            # If data dictionary exists and has data, use it
            if dict_exists:
                # Query to get tables and their descriptions
                query = """
                SELECT 
                    d1.table_name as '表名', 
                    d1.description as '表描述'
                FROM data_dictionary d1
                WHERE d1.column_name = ''
                ORDER BY d1.table_name
                """
                result = self.query(query, as_pandas=True)
                
                # If we got results from the data dictionary
                if isinstance(result, pd.DataFrame) and not result.empty:
                    return result.to_string(index=False)
            
            # Fallback to standard SHOW TABLES if dictionary is empty or doesn't exist
            log_info("Data dictionary empty or not found. Using standard SHOW TABLES.")
            result = self.query("SHOW TABLES", as_pandas=True)
            if isinstance(result, pd.DataFrame):
                return result.to_string(index=False)
            return result
            
        except Exception as e:
            error_msg = f"Error showing tables: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def describe_table(self, table: str) -> str:
        """Describe a table using data dictionary information if available.
        
        Args:
            table: Name of the table to describe
            
        Returns:
            Enhanced table description with column descriptions from data dictionary
        """
        try:
            # First get the standard table structure
            std_desc = self.query(f"DESC `{table}`", as_pandas=True)
            
            # Try to get table and column descriptions from data dictionary
            try:
                # Get table description
                table_query = f"""
                SELECT description 
                FROM data_dictionary 
                WHERE table_name = '{table}' AND column_name = ''
                """
                table_desc_result = self.query(table_query, as_pandas=True)
                table_description = table_desc_result.iloc[0]['description'] if isinstance(table_desc_result, pd.DataFrame) and not table_desc_result.empty else None
                
                # Get column descriptions
                columns_query = f"""
                SELECT column_name, description 
                FROM data_dictionary 
                WHERE table_name = '{table}' AND column_name != ''
                """
                columns_desc_result = self.query(columns_query, as_pandas=True)
                
                # Create a dictionary of column descriptions
                column_descriptions = {}
                if isinstance(columns_desc_result, pd.DataFrame) and not columns_desc_result.empty:
                    for _, row in columns_desc_result.iterrows():
                        column_descriptions[row['column_name']] = row['description']
                
                # If we found data in the dictionary, use it to enhance output
                if table_description or column_descriptions:
                    # Start building enhanced output
                    output = []
                    
                    # Add table information
                    output.append(f"=== 表信息: {table} ===")
                    if table_description:
                        output.append(f"描述: {table_description}")
                    
                    # Add column information
                    output.append("\n=== 字段信息 ===")
                    
                    if isinstance(std_desc, pd.DataFrame) and not std_desc.empty:
                        # Create a new DataFrame with combined info
                        data = []
                        for _, row in std_desc.iterrows():
                            field_name = row['Field']
                            data_type = row['Type']
                            is_nullable = row['Null']
                            is_key = row['Key']
                            
                            # Get description from dictionary
                            description = column_descriptions.get(field_name, '')
                            
                            data.append({
                                '字段名': field_name,
                                '类型': data_type,
                                '可为空': is_nullable,
                                '主键': is_key,
                                '描述': description
                            })
                        
                        combined_df = pd.DataFrame(data)
                        output.append(combined_df.to_string(index=False))
                    
                    return "\n".join(output)
            except Exception as e:
                # If any error in data dictionary lookup, fall back to standard describe
                log_debug(f"Error getting data dictionary info: {str(e)}")
            
            # Fallback to standard DESC if dictionary lookup fails
            if isinstance(std_desc, pd.DataFrame):
                return std_desc.to_string(index=False)
            return str(std_desc)
            
        except Exception as e:
            error_msg = f"Error describing table: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def analyze_data(self, sql: str) -> str:
        """Analyze data using a SQL query and provide statistics.
        
        Args:
            sql: SQL query to execute
            
        Returns:
            Data analysis results
        """
        try:
            # Execute the query
            result = self.query(sql, as_pandas=True)
            
            if not isinstance(result, pd.DataFrame) or result.empty:
                return "No data to analyze."
            
            # Generate basic statistics
            stats = []
            stats.append(f"Rows: {len(result)}")
            stats.append(f"Columns: {', '.join(result.columns)}")
            
            # Analyze numeric columns
            numeric_cols = result.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats.append("\nNumeric Column Statistics:")
                for col in numeric_cols:
                    stats.append(f"\n{col}:")
                    stats.append(f"  Min: {result[col].min()}")
                    stats.append(f"  Max: {result[col].max()}")
                    stats.append(f"  Mean: {result[col].mean()}")
                    stats.append(f"  Null count: {result[col].isna().sum()}")
            
            # Analyze non-numeric columns
            non_numeric_cols = result.select_dtypes(exclude=['number']).columns
            if len(non_numeric_cols) > 0:
                stats.append("\nNon-numeric Column Statistics:")
                for col in non_numeric_cols:
                    stats.append(f"\n{col}:")
                    stats.append(f"  Unique values: {result[col].nunique()}")
                    top_value = result[col].value_counts().index[0] if not result[col].value_counts().empty else 'N/A'
                    stats.append(f"  Most common: {top_value}")
                    stats.append(f"  Null count: {result[col].isna().sum()}")
            
            return "\n".join(stats)
        except Exception as e:
            error_msg = f"Analysis error: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def export_to_csv(self, sql: str, file_path: str) -> str:
        """Export query results to a CSV file.
        
        Args:
            sql: SQL query to execute
            file_path: Path to save the CSV file
            
        Returns:
            Status message
        """
        try:
            # Execute the query
            result = self.query(sql, as_pandas=True)
            
            if not isinstance(result, pd.DataFrame) or result.empty:
                return "No data to export."
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save to CSV
            result.to_csv(file_path, index=False)
            
            return f"Successfully exported {len(result)} rows to {file_path}"
        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def search_dictionary(self, search_term: str) -> str:
        """Search the data dictionary for tables or columns matching a term.
        
        Args:
            search_term: Term to search for
            
        Returns:
            Search results formatted as a string
        """
        try:
            search_query = f"""
            SELECT 
                table_name as '表名',
                CASE WHEN column_name = '' THEN '(表)' ELSE column_name END as '字段名',
                description as '描述'
            FROM data_dictionary
            WHERE 
                table_name LIKE '%{search_term}%' OR
                column_name LIKE '%{search_term}%' OR
                description LIKE '%{search_term}%'
            ORDER BY table_name, column_name
            """
            
            result = self.query(search_query, as_pandas=True)
            
            if isinstance(result, pd.DataFrame) and not result.empty:
                return result.to_string(index=False)
            else:
                return f"No matches found for '{search_term}'"
            
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def insert_data(self, table: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> str:
        """Insert data into a table.
        
        Args:
            table: Table name
            data: Dictionary or list of dictionaries with column:value pairs
            
        Returns:
            Status message
        """
        if self.read_only:
            return "Cannot insert data in read-only mode."
        
        self._ensure_connection()
        
        try:
            # Check if data is a list or single dictionary
            if not isinstance(data, list):
                data = [data]
            
            cursor = self.connection.cursor()
            insert_count = 0
            
            for row_data in data:
                columns = list(row_data.keys())
                placeholders = ', '.join(['%s'] * len(columns))
                column_str = ', '.join([f"`{col}`" for col in columns])
                
                values = [row_data[col] for col in columns]
                
                sql = f"INSERT INTO `{table}` ({column_str}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                insert_count += 1
            
            self.connection.commit()
            cursor.close()
            
            return f"Successfully inserted {insert_count} rows into {table}"
        except Exception as e:
            error_msg = f"Insert error: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def update_data(self, table: str, set_values: Dict[str, Any], where_clause: str) -> str:
        """Update data in a table.
        
        Args:
            table: Table name
            set_values: Dictionary of column:value pairs to update
            where_clause: WHERE clause to identify rows to update
            
        Returns:
            Status message
        """
        if self.read_only:
            return "Cannot update data in read-only mode."
        
        self._ensure_connection()
        
        try:
            cursor = self.connection.cursor()
            
            # Generate SET clause and values
            set_parts = []
            values = []
            
            for col, val in set_values.items():
                set_parts.append(f"`{col}` = %s")
                values.append(val)
            
            set_clause = ', '.join(set_parts)
            
            # Construct and execute UPDATE statement
            sql = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"
            cursor.execute(sql, values)
            
            affected_rows = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            return f"Successfully updated {affected_rows} rows in {table}"
        except Exception as e:
            error_msg = f"Update error: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def execute_sql(self, sql: str) -> str:
        """Execute a SQL statement with no return value.
        
        Args:
            sql: SQL statement to execute
            
        Returns:
            Status message
        """
        if self.read_only and not sql.strip().upper().startswith(('SELECT', 'SHOW', 'DESC', 'EXPLAIN')):
            return "Cannot execute write operations in read-only mode."
        
        return self.query(sql, as_pandas=False)

    def save(self, table: str, df: pd.DataFrame, 
            if_exists: str = 'append', 
            key_columns: Optional[List[str]] = None,
            table_description: Optional[str] = None,
            column_descriptions: Optional[Dict[str, str]] = None) -> str:
        """Save a pandas DataFrame to a Doris table and update the data dictionary.
        
        Args:
            table: Name of the table to save data to
            df: pandas DataFrame to save
            if_exists: What to do if the table exists ('fail', 'append', 'replace')
            key_columns: List of column names to use as the Doris table's key. 
                        If not provided, the first column will be used.
            table_description: Description of the table's purpose
            column_descriptions: Dictionary of column descriptions (column_name: description)
        
        Returns:
            Schema information of the saved data and data dictionary update status
        """
        if self.read_only:
            return "Cannot save data in read-only mode."
        
        if df.empty:
            return "Cannot save empty DataFrame."
                
        self._ensure_connection()
        
        try:
            cursor = self.connection.cursor()
            
            # Check if table exists
            cursor.execute("SHOW TABLES LIKE %s", (table,))
            table_exists = bool(cursor.fetchone())
            
            # Handle table existence based on if_exists parameter
            if table_exists:
                if if_exists.lower() == 'fail':
                    cursor.close()
                    return f"Table '{table}' already exists and if_exists is set to 'fail'."
                        
                elif if_exists.lower() == 'replace':
                    cursor.execute(f"DROP TABLE `{table}`")
                    table_exists = False
                        
                elif if_exists.lower() != 'append':
                    cursor.close()
                    return f"Invalid value for if_exists: {if_exists}. Must be one of: 'fail', 'append', 'replace'."
            
            # Create table if it doesn't exist
            if not table_exists:
                # Generate CREATE TABLE statement based on DataFrame schema
                column_defs = []
                
                for col_name, dtype in df.dtypes.items():
                    sql_type = self._pandas_dtype_to_sql(dtype)
                    column_defs.append(f"`{col_name}` {sql_type}")
                
                columns_str = ", ".join(column_defs)
                
                # Determine key columns
                if not key_columns:
                    # Default to first column if not specified
                    key_columns = [df.columns[0]]
                
                # Validate that all key columns exist in the dataframe
                for col in key_columns:
                    if col not in df.columns:
                        cursor.close()
                        return f"Error: Key column '{col}' does not exist in the DataFrame."
                
                # Format key columns and build table options
                key_cols_str = ", ".join([f"`{col}`" for col in key_columns])
                distribution_col = key_columns[0]  # Use first key column for distribution
                
                table_options = f"ENGINE=OLAP DUPLICATE KEY({key_cols_str}) DISTRIBUTED BY HASH(`{distribution_col}`) BUCKETS 5 PROPERTIES('replication_num' = '1')"
                
                create_stmt = f"CREATE TABLE `{table}` ({columns_str}) {table_options}"
                cursor.execute(create_stmt)
                log_info(f"Created table {table} with key columns: {key_columns}")
            
            # Insert data in batches
            batch_size = 1000
            total_rows = len(df)
            inserted_rows = 0
            
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i+batch_size]
                
                if not batch.empty:
                    # Prepare for bulk insert
                    columns = [f"`{col}`" for col in batch.columns]
                    columns_str = ", ".join(columns)
                    placeholders = ", ".join(["%s"] * len(columns))
                    
                    # Construct the INSERT statement
                    insert_stmt = f"INSERT INTO `{table}` ({columns_str}) VALUES ({placeholders})"
                    
                    # Prepare data for insertion
                    values = []
                    for _, row in batch.iterrows():
                        row_values = [None if pd.isna(v) else v for v in row]
                        values.append(row_values)
                    
                    # Execute batch insert
                    cursor.executemany(insert_stmt, values)
                    inserted_rows += len(batch)
            
            self.connection.commit()
            
            # Update data dictionary
            self._update_data_dictionary(
                table=table,
                df=df,
                table_description=table_description,
                column_descriptions=column_descriptions
            )
            
            # Get schema information
            cursor.execute(f"DESC `{table}`")
            schema_info = cursor.fetchall()
            
            # Start building output message
            schema_output = [f"Successfully saved {inserted_rows} rows to table '{table}'"]
            
            # Add data dictionary information if it was provided
            if table_description or column_descriptions:
                schema_output.append("\nData Dictionary updated with descriptions")
            
            schema_output.append("\nTable Schema:")
            
            # Format schema info
            if schema_info:
                df_schema = pd.DataFrame(schema_info)
                schema_output.append(df_schema.to_string(index=False))
            
            cursor.close()
            return "\n".join(schema_output)
                
        except Exception as e:
            error_msg = f"Error saving DataFrame: {str(e)}"
            log_debug(error_msg)
            return error_msg

    def _update_data_dictionary(self, table: str, df: pd.DataFrame, 
                              table_description: Optional[str] = None,
                              column_descriptions: Optional[Dict[str, str]] = None):
        """Update the data dictionary with table and column descriptions.
        
        Args:
            table: Table name
            df: DataFrame with the data
            table_description: Table description
            column_descriptions: Column descriptions
        """
        try:
            self._ensure_connection()
            cursor = self.connection.cursor()
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Update table description if provided
            if table_description:
                # Check if table description exists
                cursor.execute(f"SELECT 1 FROM data_dictionary WHERE table_name = '{table}' AND column_name = '' LIMIT 1")
                exists = bool(cursor.fetchone())
                
                if exists:
                    # Update existing record
                    cursor.execute(f"""
                    UPDATE data_dictionary 
                    SET description = %s, updated_at = '{now}'
                    WHERE table_name = '{table}' AND column_name = ''
                    """, (table_description,))
                else:
                    # Insert new record
                    cursor.execute(f"""
                    INSERT INTO data_dictionary (table_name, column_name, description, updated_at)
                    VALUES (%s, '', %s, '{now}')
                    """, (table, table_description))
            
            # Update column descriptions if provided
            if column_descriptions:
                for col_name, description in column_descriptions.items():
                    if col_name in df.columns:  # Only add descriptions for columns that exist
                        # Check if column description exists
                        cursor.execute(f"SELECT 1 FROM data_dictionary WHERE table_name = '{table}' AND column_name = '{col_name}' LIMIT 1")
                        exists = bool(cursor.fetchone())
                        
                        if exists:
                            # Update existing record
                            cursor.execute(f"""
                            UPDATE data_dictionary 
                            SET description = %s, updated_at = '{now}'
                            WHERE table_name = '{table}' AND column_name = '{col_name}'
                            """, (description,))
                        else:
                            # Insert new record
                            cursor.execute(f"""
                            INSERT INTO data_dictionary (table_name, column_name, description, updated_at)
                            VALUES (%s, %s, %s, '{now}')
                            """, (table, col_name, description))
            
            self.connection.commit()
            cursor.close()
            
        except Exception as e:
            log_debug(f"Error updating data dictionary: {str(e)}")
    
    def _pandas_dtype_to_sql(self, dtype) -> str:
        """Convert pandas dtype to SQL data type."""
        dtype_str = str(dtype).lower()
        
        if "int" in dtype_str:
            return "BIGINT"
        elif "float" in dtype_str:
            return "DOUBLE"
        elif "bool" in dtype_str:
            return "BOOLEAN"
        elif "datetime" in dtype_str:
            return "DATETIME"
        elif "date" in dtype_str:
            return "DATE"
        elif "object" in dtype_str or "category" in dtype_str:
            return "VARCHAR(255)"
        else:
            # Default for unknown types
            return "VARCHAR(255)"
            
    def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

            
if __name__ == "__main__":
    doris = DorisTools(
        host="192.168.50.97",
        port=30930,
        user="root",
        password="",
        database="wedata",
        read_only=False  # 设置为 True 禁用数据修改功能
    )
    
    # 创建示例 DataFrame
    df = pd.DataFrame({
        'id': range(1, 101),
        'user_name': [f'User {i}' for i in range(1, 101)],
        'age': [20 + i % 50 for i in range(1, 101)],
        'score': [round(50 + i * 0.5, 1) for i in range(1, 101)]
    })
    
    # 保存数据并同时更新数据字典
    print("=== 保存数据并更新数据字典 ===")
    result = doris.save(
        table="users_data", 
        df=df, 
        if_exists="replace",
        create_table_options="ENGINE=OLAP DUPLICATE KEY(`id`) DISTRIBUTED BY HASH(`id`) BUCKETS 5 PROPERTIES('replication_num' = '1')",
        # 表和字段描述
        table_description="用户基础信息表 - 存储用户的基本信息和评分数据，用于用户画像分析和推荐系统",
        column_descriptions={
            'id': "用户唯一标识符，自增ID",
            'user_name': "用户名称，系统登录名",
            'age': "用户年龄，以年为单位",
            'score': "用户评分，范围0-100，用于评估用户活跃度和价值"
        }
    )
    print(result)
    
    # 使用增强版的 show_tables 方法查看表及其描述
    print("\n=== 查看表列表（包含表描述） ===")
    tables = doris.show_tables()
    print(tables)
    
    # 使用增强版的 describe_table 方法查看表字段及其描述
    print("\n=== 查看表结构（包含字段描述） ===")
    desc = doris.describe_table("users_data")
    print(desc)
    
    # 分析数据
    print("\n=== 分析表数据 ===")
    analysis = doris.analyze_data("SELECT * FROM users_data")
    print(analysis)
    
    # 搜索数据字典
    print("\n=== 搜索数据字典（关键词：用户） ===")
    search_result = doris.search_dictionary("用户")
    print(search_result)
    
    # 关闭连接
    doris.close()