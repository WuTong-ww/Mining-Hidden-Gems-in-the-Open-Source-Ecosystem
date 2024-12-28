import requests
import csv

# 读取CSV文件获取仓库名列表
repos = []
with open('github_repo_stars8.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # 假设CSV文件中有一个名为'repo_name'的列存储仓库名
        repos.append(row['仓库名'])

# 存储结果的列表
activity_results = []

# 遍历仓库列表获取活跃度数据
for repo in repos:
    owner, repo_name = repo.split('/')
    url = f"https://oss.open-digger.cn/github/{owner}/{repo_name}/activity.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        activity_data = response.json()
        # 提取最后四行数据
        last_four_lines = list(activity_data.items())[-4:]
        # 计算最后四行数据中值的总和
        total_activity = sum([line[1] for line in last_four_lines])
        activity_results.append({"仓库名": repo, "最后四行活跃度总和": total_activity})
    except requests.RequestException as e:
        print(f"获取仓库 {repo} 的活跃度数据失败: {e}")

# 将结果写入CSV文件
with open('repos_activity_new.csv', 'w', newline='', encoding='utf - 8') as csvfile:
    fieldnames = ['仓库名', '最后四行活跃度总和']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(activity_results)