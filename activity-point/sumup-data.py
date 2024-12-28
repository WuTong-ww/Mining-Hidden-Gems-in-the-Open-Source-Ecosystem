import csv

# 定义一个字典来存储每列的求和结果
column_sums = {}

# 存储新数据结构的列表
new_data = []

# 读取csv文件
with open('github_repo_stars3.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)

    # 读取第一行作为标题行
    header = next(reader)

    # 遍历每一行
    for row in reader:
        new_row = []
        for index, value in enumerate(row):
            if index == 0:
                new_row.append(value)
            else:
                parts = value.split(':')
                if len(parts) > 1:
                    sub_parts = parts[1].split(',')
                    try:
                        number = int(sub_parts[0])
                        if index not in column_sums:
                            column_sums[index] = 0
                        column_sums[index] += number
                    except ValueError:
                        print(f"无法转换为整数: {value}")
        new_data.append([new_row[0], column_sums[index]])

# 写入新的csv文件
new_csv_file_path = 'github_repo_stars_sum2.csv'
with open(new_csv_file_path, mode='w', encoding='utf-8', newline='') as new_file:
    writer = csv.writer(new_file)
    writer.writerow(['仓库名', '总和'])  # 写入标题行
    writer.writerows(new_data)