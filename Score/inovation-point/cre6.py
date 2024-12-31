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
GITHUB_ACCESS_TOKEN = ""
GITHUB_HEADERS = {"Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}"} if GITHUB_ACCESS_TOKEN else {}

# Gitee相关配置
GITEE_ACCESS_TOKEN = ""
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
nltk.download('punkt_tab')

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

    # 语言和关键词的映射表
    LANGUAGE_KEYWORDS = {
        "en": ["innovation", "new", "cutting-edge", "novel", "revolutionary"],
        "sk": ["inovácia", "nový", "prielomový", "nový", "revolučný"],
        "ja": ["革新", "新しい", "最先端", "新規", "革命的"],
        "es": ["innovación", "nuevo", "de vanguardia", "revolucionario", "nuevo"],
        "de": ["Innovation", "neu", "bahnbrechend", "neuartig", "revolutionär"],
        "it": ["innovazione", "nuovo", "avanzato", "rivoluzionario", "nuovo"],
        "pt": ["inovação", "novo", "avançado", "revolucionário", "novo"],
        "hu": ["innováció", "új", "úttörő", "forradalmi", "új"],
        "hi": ["नवोन्मेष", "नया", "कटिंग-एज", "क्रांतिकारी", "नवीन"],
        "fi": ["innovaatio", "uusi", "huipputeknologia", "uudistava", "revolutionäärinen"],
        "sv": ["innovation", "ny", "banbrytande", "ny", "revolutionerande"],
        "nl": ["innovatie", "nieuw", "doorbraak", "nieuw", "revolutionair"],
        "zh": ["创新", "新", "前沿", "革命性", "新颖"],
        "fr": ["innovation", "nouveau", "de pointe", "révolutionnaire", "novateur"],
        "pl": ["innowacja", "nowy", "przełomowy", "rewolucyjny", "nowy"],
        "et": ["innovatsioon", "uus", "tipptasemel", "revolutsiooniline", "uus"],
        "hr": ["inovacija", "novi", "prekretnica", "revolucionaran", "novi"],
        "da": ["innovation", "ny", "banebrydende", "ny", "revolutionær"],
        "lb": ["Innovation", "nei", "bahnbrechend", "neuartig", "revolutionär"],
        "el": ["καινοτομία", "νέο", "πρωτοποριακό", "επανάσταση", "νέο"],
        "ru": ["инновация", "новый", "передовой", "революционный", "новаторский"],
        "id": ["inovasi", "baru", "terdepan", "revolusioner", "baru"],
        "ro": ["inovație", "nou", "de vârf", "revoluționar", "nou"],
        "bg": ["иновация", "нов", "революционен", "новаторски", "нов"],
        "sl": ["inovacija", "nov", "prelomni", "revolucionaren", "nov"],
        "lv": ["inovācija", "jauns", "pārrāvuma", "revolucionārs", "jauns"],
        "mt": ["innovazzjoni", "ġdid", "avvanzat", "rivoluzzjonarju", "ġdid"],
        "th": ["นวัตกรรม", "ใหม่", "ทันสมัย", "ปฏิวัติ", "แปลกใหม่"]
    }

    # 合并文本和标签
    all_text = text + " ".join(topics)

    # 根据语言选择关键词
    keywords = LANGUAGE_KEYWORDS.get(language, LANGUAGE_KEYWORDS["en"])  # 默认英语

    # 词汇处理
    tokens = word_tokenize(all_text.lower())
    # 根据不同语言选择停用词
    stop_words = set(stopwords.words(language)) if language in stopwords.fileids() else set(stopwords.words('english'))

    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]

    # 计算创新关键词出现的次数
    keyword_count = sum([lemmatized_tokens.count(keyword) for keyword in keywords])
    total_word_count = len(lemmatized_tokens)

    # 计算创新得分
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
    csv_file_path = 'cold/cold_repositories.csv'
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
