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
    - [popularity-score](/Score/popularity-score)：知名度得分
- [templates](/templates)：展示网页

## :100: 分析逻辑

### 知名度得分计算公式

知名度得分 = **(a * log(Stars + 1) + b * log(Forks + 1)) / (1 + c * (Stars + Forks))**

#### 参数说明：

- **a**: Star数的权重，决定Star对知名度得分的影响。
- **b**: Fork数的权重，决定Fork对知名度得分的影响。
- **c**: 总数（Star + Fork）的惩罚项系数，避免Star或Fork数过大导致得分过大。

#### 公式解释：

- **log(Stars + 1)** 和 **log(Forks + 1)**：对数变换有助于减轻较大值（例如Stars为几万或Forks为几千时）的影响，从而避免它们过度拉高最终得分。加1是为了避免对数计算时出现负数或者零的情况。
  
- **a * log(Stars + 1) + b * log(Forks + 1)**：这个部分是基础得分计算，Stars和Forks对得分的影响由a和b两个权重控制。如果Stars被认为比Forks重要，可以将a设为大于b的值，反之亦然。

- **(1 + c * (Stars + Forks))**：这是一个归一化的惩罚项，主要用于减少过度影响大的仓库（例如，Stars + Forks 非常大的仓库）对得分的影响。c值的设定会影响得分的平滑度，c值越大，过大的Stars和Fork数量对得分的影响越小。



## :rocket: 运行

```python
python app.py
```
