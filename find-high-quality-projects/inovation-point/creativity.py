import requests
import csv
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import os
import concurrent.futures
import time
from langdetect import detect

# GitHub Personal Access Token (可选，提高速率限制)
GITHUB_ACCESS_TOKEN = "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"
GITHUB_HEADERS = {"Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}"} if GITHUB_ACCESS_TOKEN else {}

# Gitee相关配置
GITEE_ACCESS_TOKEN = "3fee73567ae04775e3e1ea4f122d394c"
GITEE_HEADERS = {"Authorization": f"token {GITEE_ACCESS_TOKEN}", "Content-Type": "application/json"}


# 下载 NLTK 数据
def download_nltk_data():
    required_corpora = [
        ('corpora/wordnet', 'wordnet'),
        ('corpora/stopwords', 'stopwords'),
        ('tokenizers/punkt', 'punkt')
    ]
    for subdir, name in required_corpora:
        try:
            nltk.data.find(subdir)
            print(f"{name} 语料库已找到并可使用。")
        except LookupError:
            try:
                print(f"开始下载 {name} 语料库...")
                nltk.download(name, raise_on_error=True)
                print(f"{name} 语料库下载成功")
            except Exception as e:
                print(f"下载 {name} 语料库时出错: {e}")
                raise
    try:
        from nltk.corpus import wordnet
        print("成功导入 wordnet 语料库，检查是否可正常使用...")
        synsets = wordnet.synsets('dog')
        if synsets:
            print("wordnet 语料库可正常使用。")
        else:
            print("虽然导入成功，但获取 synsets 时出现问题。")
    except Exception as e:
        print(f"检查 wordnet 语料库使用时出错: {e}")


# 确保所有必要的NLTK数据都已下载
download_nltk_data()


# 定义获取GitHub仓库README和标签的函数
def get_github_repo_info(org, repo):
    readme_url = f"https://raw.githubusercontent.com/{org}/{repo}/master/README.md"
    try:
        readme_response = requests.get(readme_url)
        print(f"GitHub Readme Request to {readme_url}, Status Code: {readme_response.status_code}")
        readme_text = readme_response.text if readme_response.status_code == 200 else ""
    except requests.RequestException as e:
        print(f"GitHub Readme Request Error to {readme_url}: {e}")
        readme_text = ""

    api_url = f"https://api.github.com/repos/{org}/{repo}"
    headers = GITHUB_HEADERS  # 使用 GitHub Token
    while True:
        try:
            api_response = requests.get(api_url, headers=headers)
            print(f"GitHub API Request to {api_url}, Status Code: {api_response.status_code}")
            if api_response.status_code == 403:
                if 'X-RateLimit-Remaining' in api_response.headers and int(
                        api_response.headers['X-RateLimit-Remaining']) == 0:
                    reset_time = int(api_response.headers['X-RateLimit-Reset']) - int(time.time())
                    print(f"达到速率限制，等待 {reset_time + 1} 秒...")
                    time.sleep(reset_time + 1)
                    continue
            if api_response.status_code == 200:
                data = api_response.json()
                topics = data.get('topics', [])
                break
            else:
                topics = []
                break
        except requests.RequestException as e:
            print(f"GitHub API Request Error to {api_url}: {e}")
            topics = []
            break

    return readme_text, topics


# 定义获取Gitee仓库README和标签的函数
def get_gitee_repo_info(org, repo):
    readme_url = f"https://gitee.com/{org}/{repo}/raw/master/README.md"
    try:
        readme_response = requests.get(readme_url, headers=GITEE_HEADERS)  # 使用 Gitee Token
        print(f"Gitee Readme Request to {readme_url}, Status Code: {readme_response.status_code}")
        readme_text = readme_response.text if readme_response.status_code == 200 else ""
    except requests.RequestException as e:
        print(f"Gitee Readme Request Error to {readme_url}: {e}")
        readme_text = ""

    api_url = f"https://gitee.com/api/v5/repos/{org}/{repo}"
    headers = GITEE_HEADERS  # 使用 Gitee Token
    try:
        api_response = requests.get(api_url, headers=headers)
        print(f"Gitee API Request to {api_url}, Status Code: {api_response.status_code}")
        if api_response.status_code == 200:
            data = api_response.json()
            topics = data.get('topics', [])
        else:
            topics = []
    except requests.RequestException as e:
        print(f"Gitee API Request Error to {api_url}: {e}")
        topics = []

    return readme_text, topics


# 定义文本分析函数（支持多语种）
def analyze_text(text, topics):
    # 语言检测
    try:
        language = detect(text)
    except Exception as e:
        print(f"语言检测失败: {e}")
        language = "en"  # 默认英语

    # 英文的关键词
    english_keywords = ["innovation", "new", "cutting-edge", "novel", "revolutionary"]
    # 中文的关键词
    chinese_keywords = ["创新", "新", "前沿", "革命性", "新颖"]
    # 德语的关键词
    german_keywords = ["Innovation", "neu", "bahnbrechend", "neuartig", "revolutionär"]
    # 法语的关键词
    french_keywords = ["innovation", "nouveau", "de pointe", "révolutionnaire", "novateur"]
    # 西班牙语的关键词
    spanish_keywords = ["innovación", "nuevo", "de vanguardia", "revolucionario", "nuevo"]
    # 俄语的关键词
    russian_keywords = ["инновация", "новый", "передовой", "революционный", "новаторский"]

    # 合并文本和标签
    all_text = text + " ".join(topics)

    # 根据语言选择关键词
    if language == "en":
        keywords = english_keywords
    elif language == "zh":
        keywords = chinese_keywords
    elif language == "de":
        keywords = german_keywords
    elif language == "fr":
        keywords = french_keywords
    elif language == "es":
        keywords = spanish_keywords
    elif language == "ru":
        keywords = russian_keywords
    else:
        keywords = english_keywords + chinese_keywords + german_keywords + french_keywords + spanish_keywords + russian_keywords  # 如果是其他语言，混合使用

    # 词汇处理
    tokens = word_tokenize(all_text.lower())
    stop_words = set(stopwords.words('english')) if language == "en" else set()
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    keyword_count = sum([lemmatized_tokens.count(keyword) for keyword in keywords])
    total_word_count = len(lemmatized_tokens)
    innovation_score = round((keyword_count / total_word_count) * 10000, 4) if total_word_count > 0 else 0

    return innovation_score


# 从CSV文件中读取仓库信息
def read_repos_from_csv(file_path):
    repos = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            repo_name = row['repo_name']
            platform = row['platform'].lower()
            if platform not in ['github', 'gitee']:
                print(f"不支持的平台: {platform} 对于仓库 {repo_name}")
                continue
            org, repo = repo_name.split('/')
            repos.append((org, repo, platform))
    print(f"从 {file_path} 读取了 {len(repos)} 个仓库信息")
    return repos


# 处理单个仓库的函数
def process_repo(org, repo, platform, counter):
    print(f"正在处理仓库: {org}/{repo}")
    if platform == 'github':
        readme_text, topics = get_github_repo_info(org, repo)
    elif platform == 'gitee':
        readme_text, topics = get_gitee_repo_info(org, repo)
    else:
        print(f"不支持的平台: {platform} 对于仓库 {org}/{repo}")
        return None

    innovation_score = analyze_text(readme_text, topics)
    return {"repo": f"{org}/{repo}", "readme_text": readme_text, "innovation_score": innovation_score}


# 主函数
def main():
    csv_file_path = '../point/cold_repositories.csv'
    output_file_path_innovation = 'repo_innovation_scores.csv'
    output_file_path_readme = 'repo_readme_contents.csv'

    repos = read_repos_from_csv(csv_file_path)
    page_size = 20
    num_pages = len(repos) // page_size + (1 if len(repos) % page_size != 0 else 0)

    with open(output_file_path_innovation, 'w', newline='', encoding='utf-8') as csvfile_innovation, \
            open(output_file_path_readme, 'w', newline='', encoding='utf-8') as csvfile_readme:

        fieldnames_innovation = ['repo', 'innovation_score']
        writer_innovation = csv.DictWriter(csvfile_innovation, fieldnames=fieldnames_innovation)
        writer_innovation.writeheader()

        fieldnames_readme = ['repo', 'readme_text']
        writer_readme = csv.DictWriter(csvfile_readme, fieldnames=fieldnames_readme)
        writer_readme.writeheader()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for page in range(num_pages):
                start = page * page_size
                end = min((page + 1) * page_size, len(repos))
                current_repos = repos[start:end]
                print(f"正在处理第 {page + 1} 页，仓库范围: {start}-{end - 1}")

                futures = [executor.submit(process_repo, org, repo, platform, idx + 1) for idx, (org, repo, platform) in
                           enumerate(current_repos)]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        writer_innovation.writerow(
                            {"repo": result["repo"], "innovation_score": result["innovation_score"]})
                        writer_readme.writerow({"repo": result["repo"], "readme_text": result["readme_text"]})

                print(f"第 {page + 1} 页处理完成")


# 运行主函数
if __name__ == "__main__":
    main()
