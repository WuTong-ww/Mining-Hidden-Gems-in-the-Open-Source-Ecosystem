import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# GitHub 配置
GITHUB_ACCESS_TOKEN = "xxx"  # 替换为您的 GitHub Token，或者留空
GITHUB_HEADERS = {"Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}"} if GITHUB_ACCESS_TOKEN else {}

# Gitee 配置
GITEE_ACCESS_TOKEN = "xxx"  # 替换为您的 Gitee Token
GITEE_HEADERS = {"Authorization": f"Bearer {GITEE_ACCESS_TOKEN}"} if GITEE_ACCESS_TOKEN else {}

def get_rate_limit(headers):
    """从响应头解析速率限制信息"""
    remaining = int(headers.get("X-RateLimit-Remaining", 0))
    reset_time = int(headers.get("X-RateLimit-Reset", time.time()))
    return remaining, reset_time

def adjust_delay(response, default_delay=1):
    """根据速率限制调整延迟"""
    remaining, reset_time = get_rate_limit(response.headers)
    if remaining == 0:  # 达到限制
        sleep_time = max(0, reset_time - time.time())
        print(f"速率限制，等待 {sleep_time} 秒...")
        time.sleep(sleep_time)
    else:
        time.sleep(default_delay)  # 正常延迟

def get_repo_data(url, headers, key, default_delay=1):
    """通用函数，用于获取 GitHub/Gitee 仓库数据，带动态延迟控制"""
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 403:
            print("403 错误，可能触发速率限制...")
            adjust_delay(response, default_delay)  # 动态调整延迟后重试
            return get_repo_data(url, headers, key, default_delay)
        response.raise_for_status()
        adjust_delay(response, default_delay)  # 正常调整延迟
        data = response.json()
        return data.get(key, 0)
    except requests.HTTPError as e:
        print(f"HTTP 错误: {e}")
        return None
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

# GitHub API 调用函数
def get_repo_stars_github(org, repo, default_delay=1):
    url = f"https://api.github.com/repos/{org}/{repo}"
    return get_repo_data(url, GITHUB_HEADERS, "stargazers_count", default_delay)

def get_repo_forks_github(org, repo, default_delay=1):
    url = f"https://api.github.com/repos/{org}/{repo}"
    return get_repo_data(url, GITHUB_HEADERS, "forks_count", default_delay=1)

# Gitee API 调用函数
def get_repo_stars_gitee(org, repo, default_delay=1):
    url = f"https://gitee.com/api/v5/repos/{org}/{repo}"
    return get_repo_data(url, GITEE_HEADERS, "stargazers_count", default_delay=1)

def get_repo_forks_gitee(org, repo, default_delay=1):
    url = f"https://gitee.com/api/v5/repos/{org}/{repo}"
    return get_repo_data(url, GITEE_HEADERS, "forks_count", default_delay=1)

# 并发处理单个仓库
def process_single_repo(row):
    platform = row['platform'].lower()
    repo_name = row['repo_name']
    org, repo = repo_name.split('/')  # 假设格式是 org/repo

    if platform == "github":
        stars = get_repo_stars_github(org, repo)
        forks = get_repo_forks_github(org, repo)
    elif platform == "gitee":
        stars = get_repo_stars_gitee(org, repo)
        forks = get_repo_forks_gitee(org, repo)
    else:
        print(f"不支持的平台 {platform}，跳过仓库 {repo_name}")
        return None

    # 如果 API 请求失败，返回 None
    if stars is None or forks is None:
        print(f"获取数据失败，跳过仓库 {repo_name}")
        return None

    # 返回结果字典
    return {
        'id': row['id'],
        'platform': platform,
        'repo_name': repo_name,
        'stargazers_count': stars,
        'forks_count': forks
    }

# 读取仓库列表文件并处理
def process_repo_list(input_file, output_file, max_workers=5):
    try:
        # 读取仓库列表
        repo_df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"文件 {input_file} 未找到，请检查文件路径。")
        return
    except pd.errors.EmptyDataError:
        print(f"文件 {input_file} 为空，请检查内容。")
        return

    # 用于存储结果的列表
    result_data = []

    # 使用 ThreadPoolExecutor 进行并发处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_row = {executor.submit(process_single_repo, row): row for _, row in repo_df.iterrows()}

        for future in as_completed(future_to_row):
            try:
                result = future.result()
                if result:
                    result_data.append(result)
            except Exception as e:
                print(f"处理仓库时发生错误: {e}")

    # 将结果转换为 DataFrame 并保存
    try:
        result_df = pd.DataFrame(result_data)
        result_df.to_csv(output_file, index=False)
        print(f"数据已保存到 {output_file}")
    except Exception as e:
        print(f"保存结果时出错: {e}")

# 主程序入口
if __name__ == "__main__":
    input_file = "sampled_dataset.csv"  # 仓库列表文件路径
    output_file = "repo_metrics.csv"  # 输出文件路径
    process_repo_list(input_file, output_file, max_workers=10)  # 设置最大线程数为 10
