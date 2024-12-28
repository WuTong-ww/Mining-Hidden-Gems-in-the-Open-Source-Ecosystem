import dash
from dash import Dash, dcc, html
import pandas as pd
import plotly.graph_objs as go

# 读取CSV文件
try:
    df = pd.read_csv('new_total_score.csv')
    # 数据验证
    if df.isnull().values.any():
        print("数据中存在缺失值，请检查数据。")
        raise ValueError("数据存在缺失值")
except FileNotFoundError:
    print("文件未找到。请检查以下几点：")
    print("1. 文件路径是否正确，当前路径为 new_total_score.csv")
    print("2. 文件是否存在于指定路径。")
    raise
except ValueError as e:
    print(e)
    raise

# 找到综合评分最高的仓库
top_repo = df.loc[df['total_score'].idxmax()]

# 创建Dash应用
app = Dash(__name__)

# 定义布局，添加更多的样式调整以模仿科技感
app.layout = html.Div([
    html.Div([
        html.H1("仓库综合评分展示", style={
                'text-align': 'center', 'color': '#00FFFF', 'padding': '30px', 'text-shadow': '0 0 10px #00FFFF'}),
        html.H2("以下是综合评分最高的仓库", style={
                'text-align': 'center', 'color': '#00FFFF', 'padding': '20px', 'text-shadow': '0 0 10px #00FFFF'})
    ], style={'background-color': 'black', 'border-radius': '10px', 'padding': '20px', 'box-shadow': '0 0 10px rgba(0, 255, 255, 0.5)'}),
    html.Div([
        html.H3(f"{top_repo['repo_owner']}/{top_repo['repo_name']}", style={
                'text-align': 'center', 'color': '#00FFFF', 'padding': '20px', 'text-shadow': '0 0 10px #00FFFF'})
    ], style={'background-color': 'black', 'border-radius': '10px', 'padding': '20px', 'box-shadow': '0 0 10px rgba(0, 255, 255, 0.5)'}),
    html.Div([
        html.Div([
            html.Table([
                html.Thead(html.Tr([html.Th(col, style={
                    'text-align': 'center', 'padding': '8px', 'background-color': '#001F3F', 'color': '#00FFFF'}) for col in df.columns])),
                html.Tbody([
                    html.Tr([html.Td(top_repo[col], style={
                        'text-align': 'center', 'padding': '8px', 'color': '#00FFFF'}) for col in df.columns])
                ])
            ], style={'width': '100%', 'border-collapse': 'collapse'})
        ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top', 'padding': '30px', 'background-color': 'black', 'border-radius': '10px', 'box-shadow': '0 0 10px rgba(0, 255, 255, 0.5)'}),
        html.Div([
            dcc.Graph(
                id='score-bar-chart',
                figure={
                    'data': [
                        go.Bar(
                            x=['活跃度', '创新度', '技术复杂度'],
                            y=[top_repo['activity_score'], top_repo['inovation_score'], top_repo['complexity_score']],
                            marker=dict(
                                color='#00FFFF'
                            ),
                            name='评分指标'
                        )
                    ],
                    'layout': go.Layout(
                        title='综合评分最高仓库的评分指标柱状图',
                        xaxis=dict(title='评分指标', tickfont=dict(
                            color='#00FFFF'), zerolinecolor='#00FFFF'),
                        yaxis=dict(title='得分', tickfont=dict(
                            color='#00FFFF'), zerolinecolor='#00FFFF'),
                        legend=dict(x=0, y=1, font=dict(
                            color='#00FFFF'), bgcolor='rgba(0,0,0,0.5)'),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#00FFFF')
                    )
                }
            ),
            html.Div([
                html.Div([
                    html.Span(f"{col}: {top_repo[col]}", style={
                        'color': '#00FFFF', 'padding': '5px'})
                    for col in ['activity_score', 'inovation_score', 'complexity_score', 'total_score']
                ], style={'display': 'flex', 'flex - direction': 'column'})
            ], style={'width': '50%', 'display': 'inline - block', 'vertical - align': 'top', 'padding': '30px', 'background - color': 'black', 'border - radius': '10px', 'box - shadow': '0 0 10px rgba(0, 255, 255, 0.5)'})
        ], style={'width': '50%', 'display': 'inline - block', 'vertical - align': 'top', 'padding': '30px', 'background - color': 'black', 'border - radius': '10px', 'box - shadow': '0 0 10px rgba(0, 255, 255, 0.5)'}),
    ], style={'background-color': 'black', 'padding': '20px'}),
    # 增加交互性：添加一个下拉菜单来选择不同仓库
    html.Div([
        html.Label("选择仓库：", style={
            'padding': '20px', 'color': '#00FFFF', 'text-shadow': '0 0 10px #00FFFF'}),
        dcc.Dropdown(
            id='repo-dropdown',
            options=[{'label': f"{row['repo_owner']}/{row['repo_name']}", 'value': f"{row['repo_owner']}/{row['repo_name']}"} for _, row in df.iterrows()],
            value=top_repo['repo_owner'] + '/' + top_repo['repo_name']
        )
    ], style={'text-align': 'center', 'padding': '20px', 'background-color': 'black', 'border-radius': '10px', 'box-shadow': '0 0 10px rgba(0, 255, 255, 0.5)'}),
])


# 回调函数，根据下拉菜单选择更新图表和表格
@app.callback(
    dash.dependencies.Output('score-bar-chart', 'figure'),
    [dash.dependencies.Input('repo-dropdown', 'value')]
)
def update_chart(selected_repo):
    selected_row = df[df['repo_owner'] + '/' + df['repo_name'] == selected_repo]
    return {
        'data': [
            go.Bar(
                x=['活跃度', '创新度', '技术复杂度'],
                y=[selected_row['activity_score'].values[0], selected_row['inovation_score'].values[0], selected_row['complexity_score'].values[0]],
                marker=dict(
                    color='#00FFFF'
                ),
                name='评分指标'
            )
        ],
        'layout': go.Layout(
            title='综合评分最高仓库的评分指标柱状图',
            xaxis=dict(title='评分指标', tickfont=dict(
                color='#00FFFF'), zerolinecolor='#00FFFF'),
            yaxis=dict(title='得分', tickfont=dict(
                color='#00FFFF'), zerolinecolor='#00FFFF'),
            legend=dict(x=0, y=1, font=dict(
                color='#00FFFF'), bgcolor='rgba(0,0,0,0.5)'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#00FFFF')
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)