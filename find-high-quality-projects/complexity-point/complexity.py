import requests
import os
import csv


def get_file_extensions(owner, repo, token):
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    response = requests.get(url, headers = headers)
    extensions = {}
    if response.status_code == 200:
        contents = response.json()
        for item in contents:
            if item['type'] == 'file':
                file_extension = os.path.splitext(item['name'])[1].lower()
                if file_extension:
                    extensions[file_extension] = extensions.get(file_extension, 0) + 1
            elif item['type'] == 'dir':
                sub_dir_url = item['url']
                sub_dir_response = requests.get(sub_dir_url, headers = headers)
                if sub_dir_response.status_code == 200:
                    sub_dir_contents = sub_dir_response.json()
                    for sub_item in sub_dir_contents:
                        if sub_item['type'] == 'file':
                            file_extension = os.path.splitext(sub_item['name'])[1].lower()
                            if file_extension:
                                extensions[file_extension] = extensions.get(file_extension, 0) + 1
    else:
        print(f"请求 {owner}/{repo} 失败，状态码: {response.status_code}")
    return extensions


def estimate_complexity(extensions):
    complexity_score = 0
    source_file_extensions = ['.py', '.java', '.cpp', '.c']
    config_file_extensions = ['.properties', '.yaml', '.xml']
    for ext, count in extensions.items():
        if ext in source_file_extensions:
            complexity_score += count * 3
        elif ext in config_file_extensions:
            complexity_score += count * 1
        else:
            complexity_score += count * 2
    return complexity_score


def analyze_repos(repos, token):
    results = []
    for owner, repo in repos:
        extensions = get_file_extensions(owner, repo, token)
        complexity_score = estimate_complexity(extensions)
        result = {
           'repo_owner': owner,
           'repo_name': repo,
            'complexity_score': complexity_score
        }
        results.append(result)
    return results


def save_to_csv(results, filename='repo_complexity_analysis.csv'):
    with open(filename, 'w', newline='', encoding='utf - 8') as csvfile:
        fieldnames = ['repo_owner','repo_name', 'complexity_score']
        writer = csv.DictWriter(csvfile, fieldnames = fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)


token = "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"
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

analysis_results = analyze_repos(repos, token)
save_to_csv(analysis_results)
