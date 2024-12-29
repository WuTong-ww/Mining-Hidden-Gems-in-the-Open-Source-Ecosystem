import pandas as pd

# 读取原始 CSV 文件
file_path = "repo_list.csv"  # 替换为你的文件路径
data = pd.read_csv(file_path, delimiter="\t")  # 使用制表符作为分隔符

# 随机抽样 10,000 条数据
sampled_data = data.sample(n=10000, random_state=42)  # random_state 确保每次结果一致

# 保存抽样后的数据到新文件
sampled_data.to_csv("sampled_dataset.csv", index=False, sep="\t")

print("已随机抽样 10,000 条数据并保存到 sampled_dataset.csv 文件中。")
