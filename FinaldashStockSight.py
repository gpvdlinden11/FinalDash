#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import statsmodels.api as sm
import dash_table
from jupyter_dash import JupyterDash


# In[2]:


file_path = 'sample_final.pkl'
df = pd.read_pickle(file_path)


# In[3]:


df['event_time'] = pd.to_datetime(df['event_time'])


# In[4]:


df['main_category'] = df['category_code'].apply(lambda x: x.split('.')[0] if pd.notnull(x) else None)
unique_categories = df['main_category'].dropna().unique()


# In[5]:


category_options = [{'label': cat, 'value': cat} for cat in df['category_code'].str.split('.').str[0].unique() if cat]


# In[6]:


category_options = [{'label': category, 'value': category} for category in unique_categories if category is not None]


# In[7]:


df['event_time'] = pd.to_datetime(df['event_time'])


# In[8]:


df['year_month'] = df['event_time'].dt.to_period('M').astype(str)


# In[9]:


monthly_data = df.groupby('year_month').agg({'view': 'sum', 'purchase': 'sum'}).reset_index()


# In[10]:


product_stats = df.groupby('product_id').agg(
    total_views=('view', 'sum'),
    total_purchases=('purchase', 'sum')
).reset_index()


# In[11]:


product_stats['view_to_purchase_ratio'] = product_stats['total_views'] / (product_stats['total_purchases'] + 1)


# In[12]:


at_risk_products = product_stats[product_stats['view_to_purchase_ratio'] > 10]


# In[13]:


total_products = df['product_id'].nunique()
total_views = df['view'].sum()
total_purchases = df['purchase'].sum()
total_brands = df['brand'].nunique()
total_categories = df['category_code'].str.split('.').str[0].nunique()
total_subcategories = df['category_code'].nunique()


# In[14]:


app = JupyterDash(__name__)


# In[15]:


theme = {
    "accent": "#232323",
    "accent_negative": "#ff2c6d",
    "accent_positive": "#33ffe6",
    "background_content": "#F2E9DD",
    "background_page": "#E8DAC5",
    "border": "#d3bd98",
    "border_style": {
        "name": "underlined",
        "borderTopWidth": 0,
        "borderRightWidth": 0,
        "borderLeftWidth": 0,
        "borderBottomWidth": "1px",
        "borderBottomStyle": "solid",
        "borderRadius": 0,
        "inputFocus": {
            "outline": "transparent"
        }
    },
    "breakpoint_font": "1200px",
    "breakpoint_stack_blocks": "700px",
    "colorway": [
        "#232323",
        "#d95f02",
        "#1b9e77",
        "#7570b3",
        "#e7298a",
        "#66a61e",
        "#e6ab02",
        "#a6761d"
    ],
    "colorscale": [
        "#232323",
        "#363636",
        "#4b4b4b",
        "#606060",
        "#777777",
        "#8e8e8e",
        "#a6a6a6",
        "#bebebe",
        "#d7d7d7",
        "#f1f1f1"
    ],
    "font_family": "Abel",
    "font_size": "17px",
    "font_size_smaller_screen": "15px",
    "font_family_header": "PT Serif",
    "font_size_header": "24px",
    "font_family_headings": "PT Serif",
    "text": "#493D32",
    "report_font_family": "Computer Modern",
    "report_font_size": "12px",
    "report_background_page": "white",
    "report_background_content": "#FAFBFC",
    "report_text": "black"
}


# In[16]:


app.layout = html.Div([
    html.H1("Group 5", style={"textAlign": "center", "color": theme["accent"], "backgroundColor": theme["background_page"]}),
    
    html.Div([
        html.Div([
            html.H3("Total Products"),
            html.P(f"{total_products}")
        ], className="box", style={"width": "20%", "display": "inline-block", "padding": "20px", "backgroundColor": theme["background_content"], "margin": "10px", "border": "1px solid #ccc"}),

        html.Div([
            html.H3("Total Views"),
            html.P(f"{total_views}")
        ], className="box", style={"width": "20%", "display": "inline-block", "padding": "20px", "backgroundColor": theme["background_content"], "margin": "10px", "border": "1px solid #ccc"}),

        html.Div([
            html.H3("Total Purchases"),
            html.P(f"{total_purchases}")
        ], className="box", style={"width": "20%", "display": "inline-block", "padding": "20px", "backgroundColor": theme["background_content"], "margin": "10px", "border": "1px solid #ccc"}),

        html.Div([
            html.H3("Total Brands"),
            html.P(f"{total_brands}")
        ], className="box", style={"width": "20%", "display": "inline-block", "padding": "20px", "backgroundColor": theme["background_content"], "margin": "10px", "border": "1px solid #ccc"}),

        html.Div([
            html.H3("Total Categories"),
            html.P(f"{total_categories} Categories / {total_subcategories} Subcategories")
        ], className="box", style={"width": "20%", "display": "inline-block", "padding": "20px", "backgroundColor": theme["background_content"], "margin": "10px", "border": "1px solid #ccc"}),
    ], style={"width": "100%", "display": "flex", "flexDirection": "row"}),

    dcc.Tabs([
        dcc.Tab(label='Monthly Totals', children=[
            html.Div([
                html.H2("Monthly Totals"),
                html.Div([
                    html.Div(dcc.Graph(id='monthly-views'), style={"width": "50%", "display": "inline-block"}),
                    html.Div(dcc.Graph(id='monthly-purchases'), style={"width": "50%", "display": "inline-block"})
                ], style={"width": "100%", "display": "flex", "flexDirection": "row", "padding": "10px"}),
            ])
        ]),
        dcc.Tab(label='Top Categories', children=[
            html.Div([
                html.Div(dcc.Graph(id='bubble-chart-purchases'), style={"width": "50%", "display": "inline-block"}),
                html.Div(dcc.Graph(id='bubble-chart-views'), style={"width": "50%", "display": "inline-block"})
            ], style={"width": "100%", "display": "flex", "flexDirection": "row"}),
        ]),
        dcc.Tab(label='Purchase Analysis', children=[
            html.Div([
                html.Div(dcc.Graph(id='bar-chart'), style={"width": "50%", "display": "inline-block"}),
                html.Div(dcc.Graph(id='purchase-frequency'), style={"width": "50%", "display": "inline-block"})
            ], style={"width": "100%", "display": "flex", "flexDirection": "row"})
        ]),
        dcc.Tab(label='At Risk Products', children=[
            html.Div([
                html.H2("At Risk Products"),
                dash_table.DataTable(
                    id='at-risk-products-table',
                    columns=[{"name": i, "id": i} for i in at_risk_products.columns],
                    data=at_risk_products.to_dict('records'),
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'height': 'auto',
                        'minWidth': '150px', 'width': '150px', 'maxWidth': '150px',
                        'whiteSpace': 'normal'
                    },
                )
            ])
        ])
    ]),

    html.Div([
        html.Label("Date Range"),
        dcc.DatePickerRange(
            id='date-picker-range',
            min_date_allowed=df['event_time'].min(),
            max_date_allowed=df['event_time'].max(),
            start_date=df['event_time'].min(),
            end_date=df['event_time'].max()
        ),
        html.Label("Category"),
        dcc.Dropdown(
            id='category-dropdown',
            options=category_options,
            multi=True
        ),
        html.Label("Choose to Display"),
        dcc.RadioItems(
            id='display-options',
            options=[
                {'label': 'Purchases', 'value': 'purchase'},
                {'label': 'Views', 'value': 'view'}
            ],
            value='purchase',
            labelStyle={'display': 'inline-block', 'margin-right': '20px'}
        ),
    ], style={"width": "100%", "display": "inline-block", "padding": "10px"}),

    html.Div([
        html.H2("Purchases and Views overview"),
        dcc.Graph(id='category-graph'),
    ], style={"width": "100%", "display": "inline-block", "padding": "10px"}),
], style={"backgroundColor": theme["background_page"], "padding": "20px"})



# In[17]:


@app.callback(
    Output('monthly-views', 'figure'),
    Input('monthly-views', 'id')
)
def update_monthly_views_chart(_):
    fig = px.line(monthly_data, x='year_month', y='view', title='Total Views per Month')
    fig.update_layout(paper_bgcolor=theme['background_page'], plot_bgcolor=theme['background_content'])
    return fig


# In[18]:


@app.callback(
    Output('monthly-purchases', 'figure'),
    Input('monthly-purchases', 'id')
)
def update_monthly_purchases_chart(_):
    fig = px.line(monthly_data, x='year_month', y='purchase', title='Total Purchases per Month')
    fig.update_layout(paper_bgcolor=theme['background_page'], plot_bgcolor=theme['background_content'])
    return fig


# In[19]:


@app.callback(
    Output('bubble-chart-purchases', 'figure'),
    Input('bubble-chart-purchases', 'id')
)
def update_bubble_chart_purchases(_):
    top_5_purchases = df.groupby('category_code')['purchase'].sum().nlargest(5).reset_index()
    fig = px.scatter(top_5_purchases, x='category_code', y='purchase', size='purchase', color='category_code',
                     title='Top 5 Categories with Most Purchases')
    fig.update_layout(paper_bgcolor=theme['background_page'], plot_bgcolor=theme['background_content'])
    return fig


# In[20]:


@app.callback(
    Output('bubble-chart-views', 'figure'),
    Input('bubble-chart-views', 'id')
)
def update_bubble_chart_views(_):
    top_5_views = df.groupby('category_code')['view'].sum().nlargest(5).reset_index()
    fig = px.scatter(top_5_views, x='category_code', y='view', size='view', color='category_code',
                     title='Top 5 Categories with Most Views')
    fig.update_layout(paper_bgcolor=theme['background_page'], plot_bgcolor=theme['background_content'])
    return fig


# In[21]:


@app.callback(
    Output('bar-chart', 'figure'),
    Input('bar-chart', 'id')
)
def update_bar_chart(_):
    daily_purchases = df.groupby('day')['purchase'].sum().reset_index()
    fig = px.bar(daily_purchases, x='day', y='purchase', title='Total Purchases per Day')
    fig.update_layout(paper_bgcolor=theme['background_page'], plot_bgcolor=theme['background_content'])
    return fig


# In[22]:


@app.callback(
    Output('purchase-frequency', 'figure'),
    Input('purchase-frequency', 'id')
)
def update_purchase_frequency(_):
    user_id = 568782581
    user_data = df[df['user_id'] == user_id]
    purchase_frequency = user_data[['event_time', 'purchase']].set_index('event_time').resample('D').sum().reset_index()
    fig = px.line(purchase_frequency, x='event_time', y='purchase', title=f'Purchase Frequency for User ID: {user_id}')
    fig.update_layout(paper_bgcolor=theme['background_page'], plot_bgcolor=theme['background_content'])
    return fig


# In[23]:


@app.callback(
    Output('at-risk-products-table', 'data'),
    Input('at-risk-products-table', 'id')
)
def update_at_risk_products(_):
    product_stats = df.groupby('product_id').agg(
        total_views=('view', 'sum'),
        total_purchases=('purchase', 'sum')
    ).reset_index()
    product_stats['view_to_purchase_ratio'] = product_stats['total_views'] / (product_stats['total_purchases'] + 1)
    at_risk_products = product_stats[product_stats['view_to_purchase_ratio'] > 10]
    
    return at_risk_products.to_dict('records')


# In[24]:


@app.callback(
    Output('category-graph', 'figure'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('category-dropdown', 'value'),
     Input('display-options', 'value')]
)
def update_graph(start_date, end_date, categories, display_option):
    filtered_df = df[(df['event_time'] >= start_date) & (df['event_time'] <= end_date)]
    if categories:
        filtered_df = filtered_df[filtered_df['main_category'].isin(categories)]
    
    if 'purchase' in display_option:
        category_purchases = filtered_df.groupby('category_code')['purchase'].sum().reset_index()
        category_purchases['purchase'] = category_purchases['purchase'].apply(lambda x: 1 if x > 0 else 0)
        filtered_df = filtered_df.drop(columns='purchase').merge(category_purchases, on='category_code', how='left')

    grouped_data = filtered_df.groupby(['category_code', 'brand', 'price'])[display_option].sum().reset_index()
    
    grouped_data = grouped_data.sort_values(by=display_option, ascending=False)

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(grouped_data.columns),
                    fill_color='lightgrey',
                    align='left'),
        cells=dict(values=[grouped_data[col] for col in grouped_data.columns],
                   fill_color='lightsteelblue',
                   align='left'))
    ])
    fig.update_layout(paper_bgcolor=theme['background_page'], plot_bgcolor=theme['background_content'])
    return fig


# In[25]:


app.run_server(mode='inline', port=8120, debug=True)


# In[ ]:




