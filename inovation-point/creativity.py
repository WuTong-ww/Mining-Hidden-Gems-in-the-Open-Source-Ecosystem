import requests
import csv
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# 确保所有必要的NLTK数据都已下载
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')


# 定义获取仓库README和标签的函数
def get_repo_info(org, repo):
    readme_url = f"https://raw.githubusercontent.com/{org}/{repo}/master/README.md"
    try:
        readme_response = requests.get(readme_url)
        readme_text = readme_response.text if readme_response.status_code == 200 else ""
    except requests.RequestException:
        readme_text = ""

    api_url = f"https://api.github.com/repos/{org}/{repo}"
    try:
        api_response = requests.get(api_url)
        if api_response.status_code == 200:
            data = api_response.json()
            topics = data.get('topics', [])
        else:
            topics = []
    except requests.RequestException:
        topics = []

    return readme_text, topics


# 定义文本分析函数
def analyze_text(text, topics):
    unique_keywords = ["unique", "efficient", "innovative", "novel", "cutting - edge","new", "revolutionary"]
    all_text = text + " ".join(topics)
    tokens = word_tokenize(all_text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    keyword_count = sum([lemmatized_tokens.count(keyword) for keyword in unique_keywords])
    total_word_count = len(lemmatized_tokens)
    innovation_score = round((keyword_count / total_word_count) * 1000, 4) if total_word_count > 0 else 0

    return innovation_score


# 仓库列表
repos = [
    "jOOQ/jOOQ",
    "square/okio",
    "alibaba/fastjson2",
    "quarkusio/quarkus",
    "vavr-io/vavr",
    "neo4j/neo4j",
    "elastic/elasticsearch",
    "infinispan/infinispan",
    "wildfly/wildfly",
    "hazelcast/hazelcast",
    "eclipse-vertx/vert.x",
    "cucumber/cucumber-jvm",
    "eclipse/microprofile",
    "apache/iceberg",
    "grpc/grpc-java",
    "graphql-java/graphql-java",
    "reactor/reactor-core",
    "google/guava",
    "square/leakcanary",
    "google/auto"
]

# 存储结果
results = []

for repo in repos:
    org, repo_name = repo.split('/')
    readme_text, topics = get_repo_info(org, repo_name)
    innovation_score = analyze_text(readme_text, topics)
    results.append({"repo": repo, "innovation_score": innovation_score})

# 写入CSV文件
with open('repo_innovation_scores.csv', 'w', newline='', encoding='utf - 8') as csvfile:
    fieldnames = ['repo', 'innovation_score']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
