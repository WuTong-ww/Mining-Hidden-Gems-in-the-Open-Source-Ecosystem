import pandas as pd
import numpy as np
"""
知名度得分= (a * log(Stars + 1) + b * log(Forks + 1)) / (1 + c * (Stars + Forks))

参数:
    - a: Star数的权重，决定Star对知名度得分的影响。
    - b: Fork数的权重，决定Fork对知名度得分的影响。
    - c: 总数（Star + Fork）的惩罚项系数，避免Star或Fork数过大导致得分过大。
    
log(Stars + 1) 和 log(Forks + 1)：
对数变换有助于减轻较大值（例如Stars为几万或Forks为几千时）的影响，从而避免它们过度拉高最终得分。
加1是为了避免对数计算时出现负数或者零的情况。

a * log(Stars + 1) + b * log(Forks + 1)：
这个部分是基础得分计算，Stars和Forks对得分的影响由a和b两个权重控制。
如果Stars被认为比Forks重要，可以将a设为大于b的值，反之亦然。

(1 + c * (Stars + Forks))：
这是一个归一化的惩罚项，主要用于减少过度影响大的仓库（例如，Stars + Forks 非常大的仓库）对得分的影响。
c值的设定会影响得分的平滑度，c值越大，过大的Stars和Fork数量对得分的影响越小
"""

# 定义改进版的知名度评分规则函数
def calculate_improved_popularity_score(stars, forks, a=1, b=0.5, c=0.01):
    # 对数变换，避免数据过于分散，log(Stars + 1) 和 log(Forks + 1)
    star_log = np.log(stars + 1)
    fork_log = np.log(forks + 1)

    # 计算得分
    score = (a * star_log + b * fork_log) / (1 + c * (stars + forks))
    return score


# 读取已有的 repo_metrics.csv 文件
input_file = "repo_metrics.csv"  # 替换为实际文件路径
output_file = "popu_scores.csv"  # 输出文件路径

try:
    # 读取数据
    repo_df = pd.read_csv(input_file)

    # 确保数据中包含所需的列
    if all(col in repo_df.columns for col in ["stargazers_count", "forks_count", "repo_name"]):
        # 计算改进后的知名度得分
        repo_df["popularity_score"] = repo_df.apply(
            lambda row: calculate_improved_popularity_score(row["stargazers_count"], row["forks_count"]), axis=1
        )

        # 只保留 "id", "repo_name" 和 "popularity_score" 列
        result_df = repo_df[["id", "repo_name", "popularity_score"]]

        # 保存带有知名度得分的新文件
        result_df.to_csv(output_file, index=False)
        print(f"计算完成，结果已保存到 {output_file}")
    else:
        print("数据中缺少所需列（stargazers_count 或 forks_count 或 repo_name）。")
except FileNotFoundError:
    print(f"文件 {input_file} 未找到，请检查文件路径。")
except pd.errors.EmptyDataError:
    print(f"文件 {input_file} 为空，请检查内容。")
except Exception as e:
    print(f"处理时出错: {e}")
