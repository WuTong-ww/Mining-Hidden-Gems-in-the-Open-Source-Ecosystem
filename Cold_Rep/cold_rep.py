import pandas as pd

# 读取已有的 repo_popularity_scores.csv 文件
input_file = "popu_scores.csv"  # 替换为实际文件路径
output_file = "cold_repositories.csv"  # 输出冷门仓库的文件路径

try:
    # 读取数据
    repo_df = pd.read_csv(input_file)

    # 筛选出知名度得分较低的仓库，假设知名度得分 < 1 为冷门仓库
    cold_repositories_df = repo_df[repo_df["popularity_score"] < 1]

    # 将冷门仓库保存到新的文件
    cold_repositories_df.to_csv(output_file, index=False)
    print(f"冷门仓库已保存到 {output_file}")
except FileNotFoundError:
    print(f"文件 {input_file} 未找到，请检查文件路径。")
except pd.errors.EmptyDataError:
    print(f"文件 {input_file} 为空，请检查内容。")
except Exception as e:
    print(f"处理时出错: {e}")
