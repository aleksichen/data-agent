from typing import Any, Dict, List, Optional, Union
import pandas as pd
import os
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
    """A simple toolkit to connect to Apache Doris database using PyMySQL.
    
    This tool allows AI agents to query, analyze, and write data to Doris.
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
        
        if not read_only:
            self.register(self.insert_data)
            self.register(self.update_data)
            self.register(self.execute_sql)

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
        """Show all tables in the current database.
        
        Returns:
            List of tables
        """
        result = self.query("SHOW TABLES", as_pandas=True)
        if isinstance(result, pd.DataFrame):
            return result.to_string(index=False)
        return result

    def describe_table(self, table: str) -> str:
        """Describe the structure of a table.
        
        Args:
            table: Name of the table to describe
            
        Returns:
            Table structure information
        """
        result = self.query(f"DESC `{table}`", as_pandas=True)
        if isinstance(result, pd.DataFrame):
            return result.to_string(index=False)
        return result

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
            if not numeric_cols.empty:
                stats.append("\nNumeric Column Statistics:")
                for col in numeric_cols:
                    stats.append(f"\n{col}:")
                    stats.append(f"  Min: {result[col].min()}")
                    stats.append(f"  Max: {result[col].max()}")
                    stats.append(f"  Mean: {result[col].mean()}")
                    stats.append(f"  Null count: {result[col].isna().sum()}")
            
            # Analyze non-numeric columns
            non_numeric_cols = result.select_dtypes(exclude=['number']).columns
            if not non_numeric_cols.empty:
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

    def save(self, table: str, df: pd.DataFrame, if_exists: str = 'append', 
             create_table_options: Optional[str] = None) -> str:
        """Save a pandas DataFrame to a Doris table.
        
        Args:
            table: Name of the table to save data to
            df: pandas DataFrame to save
            if_exists: What to do if the table exists ('fail', 'append', 'replace')
            create_table_options: Additional Doris-specific CREATE TABLE options
                                  (e.g., "ENGINE=OLAP DUPLICATE KEY(`id`) DISTRIBUTED BY HASH(`id`) BUCKETS 10")
        
        Returns:
            Schema information of the saved data
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
                
                # Add default options if not provided
                if not create_table_options:
                    # Choose first column as key by default
                    key_col = df.columns[0]
                    create_table_options = f"ENGINE=OLAP DUPLICATE KEY(`{key_col}`) DISTRIBUTED BY HASH(`{key_col}`) BUCKETS 10 PROPERTIES('replication_num' = '1')"

                create_stmt = f"CREATE TABLE `{table}` ({columns_str}) {create_table_options}"
                cursor.execute(create_stmt)
                log_info(f"Created table {table}")
            
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
            
            # Get schema information
            cursor.execute(f"DESC `{table}`")
            schema_info = cursor.fetchall()
            
            schema_output = f"Successfully saved {inserted_rows} rows to table '{table}'\n\nTable Schema:"
            
            # Format schema info
            if schema_info:
                df_schema = pd.DataFrame(schema_info)
                schema_output += "\n" + df_schema.to_string(index=False)
            
            cursor.close()
            return schema_output
            
        except Exception as e:
            error_msg = f"Error saving DataFrame: {str(e)}"
            log_debug(error_msg)
            return error_msg
    
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
        'name': [f'User {i}' for i in range(1, 101)],
        'age': [20 + i % 50 for i in range(1, 101)],
        'score': [round(50 + i * 0.5, 1) for i in range(1, 101)]
    })
    
    # 保存到新表，自动创建表
    result = doris.save(
        table="users_data", 
        df=df,
        if_exists="replace",
    )
    print(result)