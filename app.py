import os
from flask import Flask, render_template, request, jsonify
import pandas as pd
from wordcloud import WordCloud
from transformers import pipeline
import matplotlib.pyplot as plt

app = Flask(__name__)

# 加载数据
total_data_path = 'total.csv'
source_data_path = 'source.csv'
readme_data_path = 'repo_readme_contents.csv'

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

# 初始化文本生成模型
generator = pipeline("text-generation", model="D:/Learning/MyCode/intro/model/gpt2", truncation=True)

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
            font_path="static/fonts/simhei.ttf"  # 指定支持中文的字体
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

    # 构建模型输入文本
    prompt = f"""
        Below is the README content of an open-source project along with its rating information (innovation, complexity, popularity). Please analyze the reasons for its low popularity and provide corresponding optimization suggestions based on these details:\n\n
        Project README:\n{readme_content}\n\n
        Project Ratings:\n
        Innovation Rating: {innovation}\n
        Complexity Rating: {complexity}\n
        Popularity Rating: {popularity}\n\n
        Please output the results in the following format:\n
        1. Reasons for low popularity:\n
        2. Optimization suggestions for the project:\n
        3. README improvement suggestions:\n
    """

    try:
        # 生成分析报告
        response = generator(prompt, max_length=500, num_return_sequences=1, do_sample=True, top_k=50, top_p=0.95)
        analysis_result = response[0]['generated_text'] if response else "生成失败，请检查输入或 API 设置。"
        if prompt in analysis_result:
            analysis_result = analysis_result.replace(prompt, '').strip()
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
