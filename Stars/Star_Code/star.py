import requests
import random
import time

# GitHub API 基础 URL
API_URL = "https://api.github.com/search/repositories"

# GitHub API 访问令牌（可选，用于提高速率限制）
ACCESS_TOKEN = "xxx"  # 替换为实际令牌
HEADERS = {"Authorization": f"token {ACCESS_TOKEN}"} if ACCESS_TOKEN else {}

# 初始化结果列表
repos = []

# 查询分组范围
star_ranges = [(1, 50), (51, 100), (101, 150)]

# 每个范围爬取一定次数
for star_range in star_ranges:
    lower, upper = star_range
    for _ in range(3):  # 每个范围内随机爬取3次
        random_stars_limit = random.randint(lower, upper)
        QUERY = f"stars:<{random_stars_limit}"
        PARAMS = {
            "q": QUERY,
            "sort": "stars",
            "order": "desc",
            "per_page": 100,
        }

        print(f"Fetching repositories with stars less than {random_stars_limit}...")

        try:
            response = requests.get(API_URL, headers=HEADERS, params=PARAMS)
            response.raise_for_status()  # 检查请求是否成功

            data = response.json()
            items = data.get("items", [])

            # 提取仓库的全名并加入结果列表
            for item in items:
                repos.append(item["full_name"])

            # 添加随机延迟，避免触发次级速率限制
            time.sleep(random.uniform(3, 10))

        except requests.RequestException as e:
            print(f"请求失败: {e}")
            break

# 去重并格式化输出
repos = list(set(repos))  # 去重，避免重复的仓库
print("repos = [")
for repo in repos:
    print(f'    "{repo}",')
print("]")
