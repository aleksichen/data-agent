import pymysql
try:
    conn = pymysql.connect(
        host='192.168.50.97', 
        port=30930,
        user='root',
        password='',
        connect_timeout=5,
        ssl={'ssl': {}}
    )
    print('连接成功!')
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Execute the CREATE DATABASE command
    cursor.execute('CREATE DATABASE IF NOT EXISTS wedata')
    
    print('wedata 数据库创建成功!')
    
    # Close cursor and connection
    cursor.close()
    conn.close()
except Exception as e:
    print(f'操作失败: {e}')