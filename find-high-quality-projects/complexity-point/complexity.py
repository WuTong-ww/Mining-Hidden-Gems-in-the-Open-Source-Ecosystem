import requests
import time
import csv
import os
import concurrent.futures
from typing import Dict, List, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置常量
PAGE_SIZE = 50
TIMEOUT = 30  # 增加请求超时
RETRY_TIMES = 5  # 请求失败时的重试次数

# 你的 GitHub Token 和 Gitee Token
GITHUB_TOKEN = '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'
GITEE_TOKEN = '3fee73567ae04775e3e1ea4f122d394c'

# 设置请求头
GITHUB_HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

GITEE_HEADERS = {
    'Authorization': f'token {GITEE_TOKEN}',
    'Accept': 'application/vnd.gitee.v3+json',
}

# 设置重试策略
def create_session():
    session = requests.Session()
    retries = Retry(
        total=RETRY_TIMES,
        backoff_factor=1,  # 指数退避
        status_forcelist=[500, 502, 503, 504],  # 针对这些错误自动重试
        allowed_methods=["HEAD", "GET", "OPTIONS"],  # 仅对 GET 请求重试
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session

session = create_session()  # 创建带有重试策略的 session

# 估算复杂度函数
def estimate_complexity(extensions):
    complexity_score = 0
    for ext, count in extensions.items():
        if ext in ['.py', '.java', '.cpp', '.c']:
            complexity_score += count * 3
        elif ext in ['.properties', '.yaml', '.xml']:
            complexity_score += count * 1
        else:
            complexity_score += count * 2
    return complexity_score

def get_rate_limit(headers):
    """从响应头解析速率限制信息"""
    remaining = int(headers.get("X-RateLimit-Remaining", 0))
    reset_time = int(headers.get("X-RateLimit-Reset", time.time()))
    return remaining, reset_time

def fetch_data(url, headers, retries=RETRY_TIMES):
    """带重试和速率限制控制的请求函数"""
    for _ in range(retries):
        try:
            print(f"正在请求: {url}")
            response = session.get(url, headers=headers, timeout=TIMEOUT)
            if response.status_code == 403:
                # 处理速率限制
                remaining, reset_time = get_rate_limit(response.headers)
                if remaining == 0:
                    sleep_time = max(0, reset_time - time.time())
                    print(f"速率限制，等待 {sleep_time:.2f} 秒...")
                    time.sleep(sleep_time)
                else:
                    time.sleep(1)
                continue  # 继续重试
            elif response.status_code == 404:
                # 处理 404 错误
                print(f"仓库未找到 (404): {url}")
                return None  # 返回 None，表示不再重试
            response.raise_for_status()
            print(f"请求成功: {url}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            time.sleep(2 ** _)  # 指数退避重试
    return None

def get_github_file_extensions(owner, repo):
    """获取 GitHub 仓库文件扩展名"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    response = fetch_data(url, GITHUB_HEADERS)
    if response is None:
        return {}
    extensions = {}
    for item in response:
        if item['type'] == 'file':
            ext = os.path.splitext(item['name'])[1].lower()
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
        elif item['type'] == 'dir':
            sub_dir_url = item['url']
            sub_dir_response = fetch_data(sub_dir_url, GITHUB_HEADERS)
            if sub_dir_response:
                for sub_item in sub_dir_response:
                    if sub_item['type'] == 'file':
                        ext = os.path.splitext(sub_item['name'])[1].lower()
                        if ext:
                            extensions[ext] = extensions.get(ext, 0) + 1
    return extensions

def get_gitee_file_extensions(owner, repo):
    """获取 Gitee 仓库文件扩展名"""
    url = f"https://gitee.com/api/v5/repos/{owner}/{repo}/contents"
    response = fetch_data(url, GITEE_HEADERS)
    if response is None:
        return {}
    extensions = {}
    for item in response:
        if item['type'] == 'file':
            ext = os.path.splitext(item['name'])[1].lower()
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
        elif item['type'] == 'dir':
            sub_dir_url = item['_links']['self'] + "?ref=master"
            sub_dir_response = fetch_data(sub_dir_url, GITEE_HEADERS)
            if sub_dir_response:
                for sub_item in sub_dir_response:
                    if sub_item['type'] == 'file':
                        ext = os.path.splitext(sub_item['name'])[1].lower()
                        if ext:
                            extensions[ext] = extensions.get(ext, 0) + 1
    return extensions

def get_file_extensions(owner, repo, platform):
    """获取仓库文件扩展名"""
    if platform == "github":
        return get_github_file_extensions(owner, repo)
    elif platform == "gitee":
        return get_gitee_file_extensions(owner, repo)
    else:
        print(f"不支持的平台类型: {platform}")
        return {}

def process_repo(owner, repo, platform, counter):
    """处理仓库并计算复杂度"""
    try:
        print(f"开始处理第 {counter} 个仓库: {owner}/{repo}")
        extensions = get_file_extensions(owner, repo, platform)
        if not extensions:
            return {'repo_owner': owner, 'repo_name': repo, 'complexity_score': 0, 'success': False}
        complexity_score = estimate_complexity(extensions)
        print(f"成功处理仓库 {owner}/{repo}，复杂度得分: {complexity_score}")
        return {'repo_owner': owner, 'repo_name': repo, 'complexity_score': complexity_score, 'success': True}
    except Exception as e:
        print(f"计算仓库 {owner}/{repo} 复杂度时出错: {e}")
        return {'repo_owner': owner, 'repo_name': repo, 'complexity_score': 0, 'success': False}

def fetch_repos_from_csv(file_path):
    """从CSV文件读取仓库信息"""
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        return [(row['repo_name'].split('/')[0], row['repo_name'].split('/')[1], row.get('platform', 'github'))
                for row in csv.DictReader(csvfile)]

def analyze_repos_parallel(csv_file_path, max_workers=5):
    """并行分析多个仓库"""
    repos = fetch_repos_from_csv(csv_file_path)
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_repo, owner, repo, platform, idx + 1): (owner, repo, platform) for idx, (owner, repo, platform) in enumerate(repos)}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"处理仓库时发生错误: {e}")

    return results

def save_to_csv(results, filename='repo_complexity_analysis1.csv'):
    """保存分析结果到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['repo_owner', 'repo_name', 'complexity_score', 'success']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"结果已保存到 {filename}")

if __name__ == "__main__":
    csv_file_path = '../point/cold_repositories.csv'
    analysis_results = analyze_repos_parallel(csv_file_path, max_workers=5)
    save_to_csv(analysis_results, 'new_repo_complexity_analysis.csv')
