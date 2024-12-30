from flask import Flask, render_template, request
import openai
import pandas as pd

# 初始化 Flask 应用
app = Flask(__name__)

# 配置 OpenAI API 密钥
openai.api_key = ''

# 读取评分和 README 内容的 CSV 文件
score_df = pd.read_csv('score.csv')  # 包含评分数据 (innovation_score, complexity_score, popularity_score, total_score)
readme_df = pd.read_csv('readme.csv')  # 包含仓库的 README 内容

# 合并评分数据和 README 内容
df = pd.merge(score_df, readme_df, on='repo_name')


# 首页路由：展示输入表单
@app.route('/')
def index():
    return render_template('index.html')


# 结果页面路由：展示分析结果
@app.route('/analyze', methods=['POST'])
def analyze():
    # 获取表单输入的仓库名称
    repo_name = request.form['repo_name']

    # 查找对应仓库的信息
    repo_info = df[df['repo_name'] == repo_name]
    if repo_info.empty:
        return f"未找到名为 '{repo_name}' 的仓库数据。"

    # 提取仓库数据
    repo_data = repo_info.iloc[0]
    repo_readme = repo_data['readme']
    innovation_score = repo_data['innovation_score']
    complexity_score = repo_data['complexity_score']
    popularity_score = repo_data['popularity_score']

    # 基于评分和README生成分析报告
    cold_reasons, optimization_suggestions = generate_analysis_report(repo_readme, innovation_score, complexity_score,
                                                                      popularity_score)
    # 构造最终的分析报告
    report = {
        "repo_name": repo_name,
        "cold_reasons": cold_reasons,
        "optimization_suggestions": optimization_suggestions
    }

    # 返回结果页面
    return render_template('result.html', repo_name=repo_name, report=report)


# 使用OpenAI生成冷门原因分析报告和优化建议的函数
def generate_analysis_report(readme_content, innovation_score, complexity_score, popularity_score):
    # 通过大模型接口生成冷门原因分析
    # 构造大模型输入
    prompt = f"""
        以下是一个开源项目的README内容，以及该项目的评分信息（创新性、复杂度、知名度）。请根据这些信息自动生成冷门原因分析，并给出相应的优化建议：

        项目README：
        {readme_content}

        项目评分：
        创新性评分（innovation_score）：{innovation_score}
        复杂度评分（complexity_score）：{complexity_score}
        知名度评分（popularity_score）：{popularity_score}

        1. 项目冷门原因分析：
        2. 项目优化建议：
        分析可以从以下几个方面入手：
        1.项目描述是否清晰，是否能够吸引用户的关注？
        2.项目是否属于小众领域？是否缺乏足够的市场需求或竞争？
        3.任何其他可能导致低关注度的原因及改进建议。
        """

    # 调用 OpenAI API 获取分析结果
    response = openai.Completion.create(
        engine="text-davinci-003",  # 使用适当的模型
        prompt=prompt,
        max_tokens=500,  # 可根据需要调整 token 数量
        temperature=0.7,  # 控制输出的创造性
    )

    # 提取返回的分析和建议
    generated_text = response.choices[0].text.strip()

    # 分离分析报告和优化建议
    cold_reasons, optimization_suggestions = generated_text.split("\n\n", 1)

    return cold_reasons, optimization_suggestions


# 运行 Flask 应用
if __name__ == '__main__':
    app.run(debug=True)
