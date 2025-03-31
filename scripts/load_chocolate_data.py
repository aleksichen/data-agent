import os
import kagglehub
import pandas as pd

from src.tools.doris import DorisTools

# 下载最新版本
path = kagglehub.dataset_download("atharvasoundankar/chocolate-sales")

# 查看下载目录中的文件
files = os.listdir(path)
print(f"下载的文件: {files}")

# 读取CSV文件
csv_files = [f for f in files if f.endswith('.csv')]

if csv_files:
    # 构建完整的文件路径
    file_path = os.path.join(path, csv_files[0])
    print(f"读取文件: {file_path}")
    
    # 使用pandas读取数据
    df = pd.read_csv(file_path)
    
    # 显示数据
    print("数据预览:")
    print(df.head())
    print(f"数据形状: {df.shape}，列名: {list(df.columns)}")
    
    # 添加一个id列作为主键（确保它是第一列）
    print("\n添加id列作为主键（作为第一列）...")
    df.insert(0, 'id', range(1, len(df) + 1))
    
    # 显示修改后的数据结构
    print("修改后的列名:", list(df.columns))
    print(df.head())
    
    # 初始化DorisTools
    doris = DorisTools(
        host="192.168.50.97",
        port=30930,
        user="root",
        password="",
        database="wedata",
        read_only=False
    )
    
    # 清理数据 - 处理特殊字符和格式
    # 例如，'Amount'列含有美元符号，需要转换为数值
    print("\n清理数据...")
    df['Amount'] = df['Amount'].str.replace('$', '').str.replace(',', '').astype(float)
    
    # 准备数据描述信息
    table_name = "chocolate_sales"
    table_description = "巧克力销售数据集 - 包含不同区域和产品的销售情况，用于销售分析和趋势预测"
    
    # 根据实际列名准备列描述
    column_descriptions = {
        'id': "唯一标识符，自增ID",
        'Sales Person': "销售人员姓名",
        'Country': "销售所在国家",
        'Product': "巧克力产品名称",
        'Date': "销售日期",
        'Amount': "销售金额（美元）",
        'Boxes Shipped': "出货盒数"
    }
    
    # 将数据保存到Doris（使用新的key_columns参数代替create_table_options）
    print("\n将数据保存到Doris...")
    result = doris.save(
        table=table_name,
        df=df,
        if_exists="replace",
        key_columns=["id"],  # 使用id列作为主键
        table_description=table_description,
        column_descriptions=column_descriptions
    )
    
    print(result)
    
    # 查看保存后的表结构
    print("\n查看表结构:")
    desc = doris.describe_table(table_name)
    print(desc)
    
    # 关闭连接
    doris.close()
else:
    print("未找到CSV文件")