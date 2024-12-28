import nltk
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

# 下载nltk所需的数据
nltk.download('punkt')
nltk.download('stopwords')


def get_readme_text(repo_owner, repo_name):
    url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/master/README.md"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"无法获取 {repo_owner}/{repo_name} 的README文件，状态码: {response.status_code}")
            return ""
    except Exception as e:
        print(f"获取 {repo_owner}/{repo_name} 的README文件时出错: {e}")
        return ""


repos = [
    ("jOOQ", "jOOQ"),
    ("square", "okio"),
    ("alibaba", "fastjson2"),
    ("quarkusio", "quarkus"),
    ("vavr-io", "vavr"),
    ("neo4j", "neo4j"),
    ("elastic", "elasticsearch"),
    ("infinispan", "infinispan"),
    ("wildfly", "wildfly"),
    ("hazelcast", "hazelcast"),
    ("eclipse-vertx", "vert.x"),
    ("cucumber", "cucumber-jvm"),
    ("eclipse", "microprofile"),
    ("apache", "iceberg"),
    ("grpc", "grpc-java"),
    ("graphql-java", "graphql-java"),
    ("reactor", "reactor-core"),
    ("google", "guava"),
    ("square", "leakcanary"),
    ("google", "auto")
]


def analyze_keywords(repo_owner, repo_name):
    readme_text = get_readme_text(repo_owner, repo_name)
    if readme_text:
        words = word_tokenize(readme_text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.lower() not in stop_words]
        keywords = [word for word in filtered_words if len(word) > 3]
        return keywords
    return []


def generate_report(repo_owner, repo_name, keywords):
    if not keywords:
        report = f"优化建议报告 - {repo_owner}/{repo_name}\n\n仓库无对应README文件，暂无建议\n"
    else:
        report = f"优化建议报告 - {repo_owner}/{repo_name}\n\n"

        # 项目宣传改进建议
        if "usage" not in [k.lower() for k in keywords]:
            report += "项目宣传方面：\n"
            report += " - README中应明确添加项目的使用方法和示例，以便用户快速了解如何使用该项目。\n"
        if "features" not in [k.lower() for k in keywords]:
            report += " - 详细列举项目的主要功能特性，突出项目的独特之处。\n"
        if "installation" not in [k.lower() for k in keywords]:
            report += " - 提供清晰的安装指南，包括依赖项和安装步骤。\n"

        # 吸引社区贡献建议
        report += "\n吸引社区贡献方面：\n"
        report += " - 在项目文档中制定清晰的贡献指南，明确说明如何参与项目开发、提交代码、报告问题等流程。\n"
        report += " - 设立贡献奖励机制，例如在README中提及贡献者会在项目文档或代码库中得到认可，或者给予一定的小礼品、虚拟徽章等激励。\n"
        report += " - 积极回复社区成员的问题和反馈，建立良好的沟通渠道，增强社区成员的参与感。\n"

    return report


# 整合所有仓库的报告
all_report = "所有仓库优化建议报告\n\n"
all_keywords = []
for repo_owner, repo_name in repos:
    keywords = analyze_keywords(repo_owner, repo_name)
    all_keywords.extend(keywords)
    report = generate_report(repo_owner, repo_name, keywords)
    all_report += report + "\n\n"

# 将整合后的报告保存为txt文件
with open("all_repos_report.txt", "w") as f:
    f.write(all_report)

word_freq = Counter(all_keywords)
for word, freq in word_freq.most_common(10):
    print(f"{word}: {freq}")


# 整合所有仓库的报告
all_report = "所有仓库优化建议报告\n\n"
all_keywords = []
for repo_owner, repo_name in repos:
    # 分析每个仓库的关键词
    keywords = analyze_keywords(repo_owner, repo_name)
    all_keywords.extend(keywords)
    # 生成每个仓库的优化建议报告
    report = generate_report(repo_owner, repo_name, keywords)
    # 将每个仓库的报告添加到整合报告中
    all_report += report + "\n\n"

# 将整合后的报告保存为txt文件
with open("all_repos_report.txt", "w") as f:
    f.write(all_report)
