from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os
from transformers import pipeline

app = Flask(__name__)

# 加载评分数据和 README 数据
total_data_path = 'total.csv'  # 评分数据路径
readme_data_path = 'repo_readme_contents.csv'  # README 数据路径

# # 加载评分数据
total_data = pd.read_csv(total_data_path,  encoding='utf-8')
for col in ['complexity_score', 'innovation_score', 'popularity_score']:
    total_data[col] = pd.to_numeric(total_data[col], errors='coerce')  # 确保数值列为浮点型
total_data['repo_name'] = total_data['repo_name'].astype(str)  # 确保仓库名为字符串
total_data.fillna(0, inplace=True)  # 填充缺失值为 0

# 计算加权分数
total_data['weighted_score'] = (
        total_data['complexity_score'] +
        total_data['innovation_score'] -
        10 * total_data['popularity_score']
)

# 加载 README 数据
readme_data = pd.read_csv(readme_data_path, encoding='utf-8')
readme_data['repo'] = readme_data['repo'].astype(str)  # 确保仓库名为字符串

# 排序前 100 项目
top_projects = total_data.nlargest(100, 'weighted_score')

# 生成柱状图（前 10 项目）
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


from flask import Flask, render_template, request
from transformers import pipeline

app = Flask(__name__)

@app.route('/')
def index():
    # 将前 100 个仓库发送到前端供用户选择
    return render_template('index.html', projects=top_projects.to_dict(orient='records'))


@app.route('/analyze', methods=['POST'])
def analyze():
    repo_name = request.form.get('repo_name', '').strip()

    # 查找评分数据
    repo_data = total_data[total_data['repo_name'] == repo_name]
    if repo_data.empty:
        return render_template('result.html', repo_name=repo_name,
                               analysis_result="未找到该仓库的数据，请检查仓库名称是否正确。")

    # 提取评分信息
    complexity = repo_data['complexity_score'].values[0]
    innovation = repo_data['innovation_score'].values[0]
    popularity = repo_data['popularity_score'].values[0]
    weighted_score = repo_data['weighted_score'].values[0]

    # 查找 README 内容
    repo_readme_entry = readme_data[readme_data['repo'] == repo_name]
    repo_readme = repo_readme_entry['readme_text'].values[0] if not repo_readme_entry.empty else "无 README 内容"

    # 在结果页面上先展示项目信息
    return render_template('result.html', repo_name=repo_name, repo_readme=repo_readme,
                           complexity=complexity, innovation=innovation, popularity=popularity,
                           weighted_score=weighted_score)


@app.route('/generate_analysis', methods=['POST'])
def generate_analysis():
    # 获取来自表单的数据
    repo_name = request.form.get('repo_name', '').strip()
    repo_readme = request.form.get('repo_readme', None)

    complexity_str = request.form.get('complexity', '0')  # 获取字符串形式的值，默认值设为 '0'
    if complexity_str.strip():  # 判断去除空白字符后是否有内容
        complexity = float(complexity_str)
    else:
        complexity = 0  # 如果为空字符串，设置为默认值0

    innovation_str = request.form.get('innovation', '0')
    if innovation_str.strip():
        innovation = float(innovation_str)
    else:
        innovation = 0

    popularity_str = request.form.get('popularity', '0')
    if popularity_str.strip():
        popularity = float(popularity_str)
    else:
        popularity = 0
    # 构建 API 输入文本
    if repo_readme:
        prompt = f"""
            Below is the README content of an open-source project along with its rating information (innovation, complexity, popularity). Please analyze the reasons for its low popularity and provide corresponding optimization suggestions based on these details:\n\n
            Project README:\n{repo_readme}\n\n
            Project Ratings:\n
            Innovation Rating: {innovation}\n
            Complexity Rating: {complexity}\n
            Popularity Rating: {popularity}\n\n
            Please output the results in the following format:\n
            1. Reasons for low popularity:\n[Please fill in here]\n
            2. Optimization suggestions for the project:\n[Please fill in here]\n
            3. README improvement suggestions:\n[Please fill in here]\n
        """
    else:
        prompt = f"""
            Below are the rating details of an open-source project (innovation, complexity, popularity). Please analyze the reasons for its low popularity and provide corresponding optimization suggestions based on these details:\n\n
            Project Ratings:\n
            Innovation Rating: {innovation}\n
            Complexity Rating: {complexity}\n
            Popularity Rating: {popularity}\n\n
            Please output the results in the following format:\n
            1. Reasons for low popularity:\n[Please fill in here]\n
            2. Optimization suggestions for the project:\n[Please fill in here]\n
            3. README improvement suggestions:\n[Please fill in here]\n
        """

    try:
        generator = pipeline("text-generation", model="D:/Learning/MyCode/intro/model/gpt2", truncation=True)
        response = generator(prompt, max_length=500, num_return_sequences=1, do_sample=True, top_k=50, top_p=0.95)
        analysis_result = response[0]['generated_text'] if response else "生成失败，请检查输入或 API 设置。"
        # 删除生成文本中多余的 Prompt 部分
        if prompt in analysis_result:
            analysis_result = analysis_result.replace(prompt, '').strip()
    except Exception as e:
        analysis_result = f"生成失败：{e}"

    # 返回渲染结果页面，显示分析结果
    return render_template('result.html', repo_name=repo_name, analysis_result=analysis_result)

if __name__ == '__main__':
    app.run(debug=True)
