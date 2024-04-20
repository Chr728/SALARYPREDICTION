import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.io import output_notebook, show
from bokeh.models import HoverTool, Slider, ColumnDataSource
from bokeh.layouts import layout
from bokeh.transform import factor_cmap
from bokeh.palettes import Category10_5
import ipywidgets as widgets
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import boto3
from io import BytesIO
import io
import plotly.figure_factory as ff
import plotly.graph_objs as go


aws_access_key_id = 'AKIAZQ3DOOYC7J5PI25Z'
aws_secret_access_key = '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'

bucket_name = 'comp333bucket'

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

file_key = 'merged_dataset.csv'
obj = s3.get_object(Bucket=bucket_name, Key=file_key)
content = obj['Body'].read()
merged_df = pd.read_csv(BytesIO(content), engine='python')
# Create the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.Div([
        html.Label('Salary Distribution Histogram', style={'font-weight': 'bold', 'margin-bottom': '10px'}),
        html.Div([
            dcc.Graph(id='histogram', style={'width': '80%', 'margin': 'auto'}),
        ]),
        html.Label('Number of Bins'),
        html.Div(
        dcc.Slider(
            id='bin-slider',
            min=1,
            max=20,
            step=1,
            value=10,
            marks={i: str(i) for i in range(1, 21)},
        ),
        style={'width': '80%', 'margin': 'auto', 'padding': '10px'}
        ),
      html.Div([
            html.Label('Salary vs State Boxplot', style={'font-weight': 'bold', 'margin-bottom': '10px'}),
            dcc.Graph(id='boxplot', style={'width': '80%', 'margin': 'auto'})
        ]),
      html.Div([
            html.Label('Top 5 States with Highest Median Salaries - Boxplot', style={'font-weight': 'bold', 'margin-bottom': '10px'}),
            dcc.Graph(id='top-states-boxplot', style={'width': '80%', 'margin': 'auto'})
        ]),
      html.Div([
            html.Label('Salary vs Month Boxplot', style={'font-weight': 'bold', 'margin-bottom': '10px'}),
            dcc.Graph(id='salary-vs-month-boxplot', style={'width': '80%', 'margin': 'auto'})
        ]),
      html.Div([
        html.Label('Top 5 States with Highest Median Salaries', style={'font-weight': 'bold', 'margin-bottom': '10px'}),
        dcc.Graph(id='bar-chart', style={'width': '80%', 'margin': 'auto'}),
    ])
    ])
])

# Define the callback to update the histogram based on the slider value
@app.callback(
    Output('histogram', 'figure'),
    [Input('bin-slider', 'value')]
)
def update_histogram(num_bins):
    fig = px.histogram(merged_df, x='Salary', nbins=num_bins)
    return fig


@app.callback(
    Output('boxplot', 'figure'),
    [Input('bin-slider', 'value')]
)
def update_boxplot(num_bins):
    boxplot_data = []
    for state, data in merged_df.groupby('State'):
        boxplot_data.append(go.Box(y=data['Salary'], name=state))
    layout = go.Layout(
        title='Salary vs State',
        xaxis=dict(title='State'),
        yaxis=dict(title='Salary'),
        boxmode='group'
    )
    fig = go.Figure(data=boxplot_data, layout=layout)
    return fig


@app.callback(
    Output('top-states-boxplot', 'figure'),
    [Input('bin-slider', 'value')]
)
def update_top_states_boxplot(num_bins):
    median_salaries = merged_df.groupby('State')['Salary'].median().sort_values(ascending=False)
    top_states = median_salaries.head(5).index
    top_states_df = merged_df[merged_df['State'].isin(top_states)]
    boxplot_data = []
    for state in top_states:
        data = top_states_df[top_states_df['State'] == state]
        boxplot_data.append(go.Box(y=data['Salary'], name=state))
    layout = go.Layout(
        title='Top 5 States with Highest Median Salaries - Boxplot',
        xaxis=dict(title='State'),
        yaxis=dict(title='Salary'),
        boxmode='group'
    )
    fig = go.Figure(data=boxplot_data, layout=layout)
    return fig


# Define the callback to update the box plot based on salary vs month
@app.callback(
    Output('salary-vs-month-boxplot', 'figure'),
    [Input('bin-slider', 'value')]
)
def update_salary_vs_month_boxplot(num_bins):
    print("Callback triggered with num_bins:", num_bins)
    # Create a list to store box plots for each month
    boxplot_data = []
    
    # Group the data by month
    grouped_df = merged_df.groupby('Month')
    
    # Iterate over each group (month) and create a box plot
    for month, data in grouped_df:
        boxplot_data.append(go.Box(y=data['Salary'], name=month))
    
    # Define the layout
    layout = go.Layout(
        title='Salary vs Month - Boxplot',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Salary'),
        boxmode='group'
    )
    
    # Create the figure
    fig = go.Figure(data=boxplot_data, layout=layout)
    return fig


# Define the callback to update the bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('bar-chart', 'children')]  # This input will not be used, it's just to trigger the callback
)
def update_bar_chart(_):
    # Calculate median salaries
    median_salaries = merged_df.groupby('State')['Salary'].median().sort_values(ascending=False)
    top_states = median_salaries.head(5)

    # Create Plotly bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=top_states.index, y=top_states.values, marker_color='skyblue'))

    # Update layout
    fig.update_layout(title='Top 5 States with Highest Median Salaries', xaxis_title='State', yaxis_title='Median Salary', xaxis_tickangle=-45)

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
