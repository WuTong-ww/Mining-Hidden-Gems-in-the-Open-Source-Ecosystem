import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import requests
import json
import time

app = Flask(__name__)

# 加载数据
total_data_path = 'screen_data/total.csv'
source_data_path = 'screen_data/source.csv'
readme_data_path = 'screen_data/repo_readme_contents.csv'

# 加载评分数据
total_data = pd.read_csv(total_data_path, encoding='utf-8')
for col in ['complexity_score', 'innovation_score', 'popularity_score']:
    total_data[col] = pd.to_numeric(total_data[col], errors='coerce')  # 确保数值列为浮点型
total_data['repo_name'] = total_data['repo_name'].astype(str)  # 确保仓库名为字符串
total_data.fillna(0, inplace=True)  # 填充缺失值为 0

# 动态计算加权分数
total_data['weighted_score'] = (
        total_data['complexity_score'] +
        total_data['innovation_score'] -
        total_data['popularity_score']
)

# 加载 README 数据
readme_data = pd.read_csv(readme_data_path, encoding='utf-8')
readme_data['repo'] = readme_data['repo'].astype(str)  # 确保仓库名为字符串

# 合并来源数据
source_data = pd.read_csv(source_data_path, encoding='utf-8')
total_data = total_data.merge(source_data, on='repo_name', how='left')  # 左连接，基于 repo_name 合并

# 根据 platform 和 repo_name 生成 source 列
total_data['source'] = total_data.apply(
    lambda row: f"https://{row['platform']}.com/{row['repo_name']}" if pd.notna(row['platform']) else "未知", axis=1
)

# 确保词云图片的保存目录存在
if not os.path.exists('static/wordclouds'):
    os.makedirs('static/wordclouds')

# 生成柱状图（前 10 项目）
top_projects = total_data.nlargest(100, 'weighted_score')
plt.figure(figsize=(10, 6))
plt.barh(top_projects['repo_name'].head(10), top_projects['weighted_score'].head(10), color='skyblue')
plt.xlabel('Weighted Score')
plt.ylabel('Repository Name')
plt.title('Top 10 Repositories by Weighted Score')
plt.gca().invert_yaxis()

if not os.path.exists('static'):
    os.makedirs('static')  # 确保 static 文件夹存在
chart_path = os.path.join('static', 'top_projects_chart.png')
plt.savefig(chart_path)
plt.close()

# 云端大模型API调用函数
def call_cloud_llm(prompt, max_tokens=300, retry=3):
    """
    调用云端大语言模型API

    Args:
        prompt (str): 输入提示文本
        max_tokens (int): 生成的最大token数
        retry (int): 重试次数

    Returns:
        str: 模型生成的文本
    """

    # 明确指定API配置信息
    api_key = os.getenv("CLOUD_LLM_API_KEY", "xxx")  # 实际使用时替换为您的API密钥
    api_url = "https://chat.ecnu.edu.cn/open/api/v1/chat/completions"  # 明确指定URL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # API请求数据
    data = {
        "model": "ecnu-max",  # 直接明确指定使用ecnu-max模型
        "messages": [
            {
                "role": "system",
                "content": "你是一名代码分析专家，擅长分析开源项目并提供改进建议。请根据用户提供的项目信息，分析项目流行度低的原因并给出优化建议。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.5,
        "max_tokens": max_tokens,
        "top_p": 0.9
    }

    # 重试机制
    for attempt in range(retry):
        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"API请求失败，尝试 {attempt + 1}/{retry}，状态码：{response.status_code}")
                print(f"响应内容：{response.text}")
                time.sleep(1)  # 失败后短暂延迟再重试

        except Exception as e:
            print(f"API调用异常 (尝试 {attempt + 1}/{retry})：{str(e)}")
            time.sleep(2)  # 异常后稍长延迟再重试

    return "分析服务暂时不可用，请稍后再试。"


@app.route('/')
def index():
    # 将前 100 个仓库发送到前端供用户选择
    # 综合评分最高的 100 个仓库
    top_100_repos = total_data.nlargest(100, 'weighted_score')
    # 将数据分组，每组 20 个
    grouped_repos = [top_100_repos[i:i + 20] for i in range(0, 100, 20)]
    grouped_repos = [
        group[['repo_name', 'weighted_score']].to_dict(orient='records') for group in grouped_repos
    ]

    # 获取来源链接数据
    source_data = total_data[['platform', 'repo_name']]
    source_data['source'] = source_data.apply(
        lambda row: f"https://{row['platform']}.com/{row['repo_name']}" if pd.notna(row['platform']) else "未知", axis=1
    )
    source_links = source_data.set_index('repo_name')['source'].to_dict()

    # 获取复杂性评分和创新性评分最高的前 10 名，用于柱状图
    top_complexity = total_data.nlargest(10, 'complexity_score')[['repo_name', 'complexity_score']].to_dict(
        orient='records')
    top_innovation = total_data.nlargest(10, 'innovation_score')[['repo_name', 'innovation_score']].to_dict(
        orient='records')

    # 将高分仓库列表用于下拉菜单选择
    top_weighted_dropdown = top_100_repos[['repo_name', 'weighted_score']].head(10).to_dict(orient='records')
    top_complexity_dropdown = total_data.nlargest(10, 'complexity_score')[['repo_name', 'complexity_score']].to_dict(
        orient='records')
    top_innovation_dropdown = total_data.nlargest(10, 'innovation_score')[['repo_name', 'innovation_score']].to_dict(
        orient='records')

    return render_template(
        'index.html',
        grouped_repos=grouped_repos,  # 分组后的 100 个仓库
        source_links=source_links,  # 来源链接
        top_complexity=top_complexity,  # 复杂性评分前 10 名
        top_innovation=top_innovation,  # 创新性评分前 10 名
        top_weighted_dropdown=top_weighted_dropdown,  # 综合评分前 10 名，用于下拉框
        top_complexity_dropdown=top_complexity_dropdown,  # 复杂性评分前 10 名，用于下拉框
        top_innovation_dropdown=top_innovation_dropdown  # 创新性评分前 10 名，用于下拉框
    )


@app.route('/analyze', methods=['POST'])
def analyze():
    repo_name = request.form['repo_name']
    repo_data = total_data[total_data['repo_name'] == repo_name]

    if repo_data.empty:
        return render_template('result.html', repo_name=repo_name,
                               repo_url="#", repo_source="未知",
                               analysis_result="未找到该仓库的数据，请检查仓库名称是否正确。",
                               complexity=0,
                               innovation=0,
                               popularity=0,
                               wordcloud_path=None,
                               cold_reasons="无法提供冷门原因分析。",
                               optimization_suggestions="无优化建议。")

    # 获取评分数据
    complexity = repo_data['complexity_score'].values[0]
    innovation = repo_data['innovation_score'].values[0]
    popularity = repo_data['popularity_score'].values[0]
    weighted_score = complexity + innovation - popularity

    # 获取来源信息
    repo_source = repo_data['source'].values[0]
    repo_url = repo_source

    # 从 readme_data 中获取 README 内容
    readme_content = readme_data[readme_data['repo'] == repo_name]['readme_text'].values
    if len(readme_content) > 0 and isinstance(readme_content[0], str):
        readme_content = readme_content[0]
    elif len(readme_content) > 0:
        readme_content = str(readme_content[0])  # 转换为字符串
    else:
        readme_content = "无内容"  # 如果内容为空或不是字符串，设置为默认值

    # 生成词云
    wordcloud_path = None
    if readme_content.strip():  # 确保内容非空
        # 构建词云图片路径
        wordcloud_path = f'static/wordclouds/{repo_name}.png'
        wordcloud_dir = os.path.dirname(wordcloud_path)

        # 创建父目录（如果不存在）
        if not os.path.exists(wordcloud_dir):
            os.makedirs(wordcloud_dir)

        # 生成词云并保存
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color=None,  # 透明背景
            mode="RGBA",
            colormap="viridis",
            #font_path="static/fonts/simhei.ttf"  # 指定支持中文的字体
        ).generate(readme_content)
        wordcloud.to_file(wordcloud_path)

    # 基于 README 分析冷门原因
    cold_reasons = []
    if "TODO" in readme_content or len(readme_content) < 200:
        cold_reasons.append("文档可能不够完善。")
    if popularity < 50:
        cold_reasons.append("仓库可能因为缺乏推广而冷门。")
    if innovation < 30:
        cold_reasons.append("项目可能缺乏创新性，导致吸引力不足。")
    if complexity > 70:
        cold_reasons.append("仓库可能过于复杂，学习成本高，劝退了部分用户。")

    # 动态生成发展建议
    optimization_suggestions = []
    if "TODO" in readme_content:
        optimization_suggestions.append("完善 README 文档内容，减少 TODO 未完成项。")
    if len(readme_content) < 200:
        optimization_suggestions.append("增加文档内容，详细介绍项目功能和使用方法。")
    if popularity < 50:
        optimization_suggestions.append("尝试通过社交媒体或开发者社区推广仓库。")
    if innovation < 30:
        optimization_suggestions.append("探索新功能或实现新的创新点来吸引用户。")
    if complexity > 70:
        optimization_suggestions.append("优化项目结构，降低复杂性，让新手更容易上手。")

    # 构建模型输入文本（中文版）
    prompt = f"""
        以下是一个开源项目的README内容以及其评分信息（创新性、复杂性、流行度）。请分析该项目流行度较低的原因，并根据这些详细信息提供相应的优化建议：\n\n
        项目README内容：\n{readme_content}\n\n
        项目评分：\n
        创新性评分：{innovation}\n
        复杂性评分：{complexity}\n
        流行度评分：{popularity}\n\n
        请按照以下格式输出结果：\n
        1. 流行度低的原因：\n
        2. 项目优化建议：\n
        3. README改进建议：\n
    """

    try:
        # 调用云端大模型API替代本地模型
        analysis_result = call_cloud_llm(prompt, max_tokens=500, retry=3)
    except Exception as e:
        analysis_result = f"生成失败：{e}"

    # 传递评分数据给前端，用于柱状图和饼状图
    scores = {
        "complexity": complexity,
        "innovation": innovation,
        "popularity": popularity
    }

    return render_template(
        'result.html',
        repo_name=repo_name,
        repo_url=repo_url,
        repo_source=repo_source,
        complexity=complexity,
        innovation=innovation,
        popularity=popularity,
        wordcloud_path=wordcloud_path,
        analysis_result=analysis_result,
        cold_reasons=" ".join(cold_reasons),
        optimization_suggestions=" ".join(optimization_suggestions),
        scores=scores  # 传递分数数据
    )
    # return jsonify({
    #     'repo_name': repo_name,
    #     'repo_url': repo_url,
    #     'repo_source': repo_source,
    #     'complexity': complexity,
    #     'innovation': innovation,
    #     'popularity': popularity,
    #     'wordcloud_path': wordcloud_path,
    #     'analysis_result': analysis_result,
    #     'cold_reasons': cold_reasons,
    #     'optimization_suggestions': optimization_suggestions,
    #     'scores': scores
    # })


if __name__ == '__main__':
    app.run(debug=True)