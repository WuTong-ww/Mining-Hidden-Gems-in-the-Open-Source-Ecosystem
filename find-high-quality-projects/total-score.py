import pandas as pd
from flask import Flask, render_template


def calculate_total_score():
    """
    读取原始数据，处理并计算综合得分，然后保存到新的CSV文件
    """
    try:
        # 读取total_score.csv文件
        df = pd.read_csv('three-score.csv')

        # 将activity_score除以1000
        df['activity_score'] = df['activity_score'] / 1000

        # 设定权重参数
        alpha = 0.3
        beta = 0.3
        gamma = 0.4

        # 计算综合得分
        df['total_score'] = alpha * df['complexity_score'] + beta * df['inovation_score'] - gamma * df['activity_score']

        # 将总分保留小数点后两位
        df['total_score'] = df['total_score'].apply(lambda x: round(x, 2))

        # 保存到新的CSV文件
        df.to_csv('new_total_score.csv', index=False)
    except FileNotFoundError:
        print("total_score.csv文件未找到，请确保文件存在。")





