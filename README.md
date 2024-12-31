# Openrank参赛——开源生态系统中的“冷门宝藏”挖掘

![Static Badge](https://img.shields.io/badge/Data-OpenDigger-blue)

通过对开源项目的多维数据分析，挖掘那些质量高、创新性强但关注度较低的“冷门宝藏”项目，分析其受限原因，并提出提升曝光度的建议。

## :hand_with_index_finger_and_thumb_crossed: 项目成员

- 吴彤[@WuTong-ww](https://github.com/WuTong-ww)：

- 王惜冉[@irani0811](https://github.com/irani0811)：

## :open_file_folder: 项目文件目录结构

```
冷门宝藏挖掘/
│  app.py
│  README.md
│  开源系统中的“冷门宝藏”挖掘.pptx
│  
├─Cold_Rep
│      cold_rep.py
│      cold_repositories.csv
│      
├─Reason
│      all_repos_report.txt
│      find-reason.py
│      repo_readme_contents.csv
│      
├─Sample_Data
│      choose_sample.py
│      repo_metrics.csv
│      star_fork2.py
│      
├─Score
│  ├─activity-point
│  │      get-activity.py
│  │      github_repo_activity.csv
│  │      repos_activity.csv
│  │      sumup-data.py
│  │      
│  ├─complexity-point
│  │      complexity.py
│  │      new_repo_complexity_analysis.csv
│  │      
│  ├─inovation-point
│  │      cre6.py
│  │      repo_innovation_scores.csv
│  │      
│  ├─point
│  │      cold_repositories.csv
│  │      new_repo_complexity_analysis.csv
│  │      repo_innovation_scores.csv
│  │      total.csv
│  │      
│  └─popularity-score
│          popularity_score.py
│          popu_scores.csv
│          
└─templates
        index.html
        result.html

```
### 文件结构介绍
- [app.py](/app.py)：后端文件
- [开源系统中的“冷门宝藏”挖掘.pptx](/开源系统中的“冷门宝藏”挖掘.pptx)：初赛ppt
- [Cold_Rep](/Cold_Rep)：冷门仓库搜索
- [Reason](/Reason)：冷门原因分析
- [Sample_Data](/Sample_Data)：选取样本仓库
- [Score](/Score)：计算得分
    - [activity-point](/Score/activity-point)：活跃度得分
    - [complexity-point](/Score/complexity-point)：复杂度得分
    - [inovation-point](/Score/inovation-point)：创新性得分
    - [popularity-score](/Score/popularity-score)：流行度得分
- [templates](/templates)：展示网页


## :rocket: 运行

```python
python app.py
```
