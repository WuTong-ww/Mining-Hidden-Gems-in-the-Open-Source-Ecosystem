import pandas as pd

# 加载原始 CSV 文件
total_file_path = 'total.csv'  # 替换为你的文件路径
total_data = pd.read_csv(total_file_path, encoding='ISO-8859-1')

# 确保需要归一化的列是数值类型
for col in ['complexity_score', 'innovation_score', 'popularity_score']:
    total_data[col] = pd.to_numeric(total_data[col], errors='coerce')  # 无法转换的值将变为 NaN

# 填充 NaN 值为 0，避免计算时出现问题
total_data.fillna(0, inplace=True)

# 对需要归一化的列进行 0-100 百分比转换
for col in ['complexity_score', 'innovation_score', 'popularity_score']:
    total_data[col] = (
        (total_data[col] - total_data[col].min()) /
        (total_data[col].max() - total_data[col].min())
    ) * 100

# 保留两位小数
total_data[['complexity_score', 'innovation_score', 'popularity_score']] = total_data[
    ['complexity_score', 'innovation_score', 'popularity_score']
].round(2)

# 保存归一化后的数据回原始文件
total_data.to_csv(total_file_path, index=False, encoding='ISO-8859-1')

print(f"归一化后的数据已保存到 {total_file_path}")
