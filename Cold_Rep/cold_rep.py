import pandas as pd
"""
按照知名度中位数来定义冷门仓库
防止异常数据的产生，还设置了star数小于150的阈值
"""
# 读取已有的 popu_scores.csv 和 repo_metrics.csv 文件
popu_scores_file = "popu_scores.csv"  # 低知名度仓库得分文件
repo_metrics_file = "repo_metrics.csv"  # 仓库的详细信息文件，包含stargazers_count

output_file = "cold_repositories.csv"  # 输出冷门仓库的文件路径

try:
    # 读取数据
    popu_scores_df = pd.read_csv(popu_scores_file)
    repo_metrics_df = pd.read_csv(repo_metrics_file)

    # 根据id将两个数据集进行合并，保留popu_scores_df的所有列
    merged_df = pd.merge(popu_scores_df, repo_metrics_df[['id', 'stargazers_count']], on='id', how='left')

    # 计算知名度得分的中位数
    median_score = merged_df["popularity_score"].median()
    print(f"知名度得分的中位数: {median_score}")

    # 筛选出知名度得分低于中位数的仓库
    cold_repositories_df = merged_df[merged_df["popularity_score"] < median_score]

    # 进一步筛选出stargazers_count大于150的仓库，去除这些仓库
    cold_repositories_df = cold_repositories_df[cold_repositories_df["stargazers_count"] <= 150]

    # 只保留 "id", "repo_name", "platform" 和 "popularity_score" 列
    cold_repositories_df = cold_repositories_df[["id", "platform", "repo_name",  "popularity_score"]]

    # 将冷门仓库保存到新的文件
    cold_repositories_df.to_csv(output_file, index=False)
    print(f"冷门仓库已保存到 {output_file}")

except FileNotFoundError:
    print(f"文件 {popu_scores_file} 或 {repo_metrics_file} 未找到，请检查文件路径。")
except pd.errors.EmptyDataError:
    print(f"文件 {popu_scores_file} 或 {repo_metrics_file} 为空，请检查内容。")
except Exception as e:
    print(f"处理时出错: {e}")
