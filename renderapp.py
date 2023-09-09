#Importing Libraries
import dash
from dash import dcc
from dash import html
import plotly.express as px
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pytz
from datetime import datetime, timedelta
import io, json, boto3
import pandas as pd
import mysql.connector


#Image Links
chatstat_logo = "https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/chatstatlogo.png"
clock = "https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/clock.png"
platform = "https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/loudspeaker.jpg"
alert = "https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/alert.jpg"
backward_button_image = "https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/backward-arrow.png"
forward_button_image = "https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/forward-arrow.png"
user_logo = "https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/user.jpg"


df = pd.read_csv(/Data/final_data.csv")

#User Table
alert_table_df = df[(df["alert_contents"].str.lower() != "no") & (df["alert_contents"].str.lower() != "")]
alert_table_df = alert_table_df.groupby(by = ["user_childrens", "name_childrens"], as_index = False)["id_contents"].nunique()
alert_table_df = alert_table_df.sort_values(by = ["id_contents"], ascending = False)
alert_table_df = alert_table_df.reset_index(drop = True)
alert_table_df.columns = ["user", "name", "count"]
user_list = alert_table_df["name"].unique()


# Creating a Dash app for Dashboard
dashboard = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = dashboard.server

# Define the layout of the app
dashboard.layout = html.Div([
    html.Hr(style={"color": "rgb(255,255,255)", "margin": "2.5px"}),
    dbc.Row([
        dbc.Col(html.Img(src=chatstat_logo, alt="ChatStat Logo", style={"width": "200px", "margin": "10px"}), width = 2),
        dbc.Col([
            dbc.Row(html.P("ChatStat Analytics", style={'font-size': '20px', 'font-weight': 'bold'})),
            dbc.Row(
                html.Div(style={'flex': '1'}, children=[
                    html.P(id='current-time', style={'font-size': '20px', 'font-weight': 'bold'}),
                    dcc.Interval(id="Time", interval=1000, n_intervals=0)
                ])
                )
        ], width = 7),

        dbc.Col([
            dbc.Row([
                dbc.Col(html.P("Difference in Alerts generated", style={"font-weight": "bold"}), width = 8),
                dbc.Col(
                    dcc.Dropdown(
                        id="kpi_dropdown",
                        options=[
                            {'label': 'Day', 'value': 'D'},
                            {'label': 'Week', 'value': 'W'},
                            {'label': 'Month', 'value': 'M'},
                            {'label': 'Quarter', 'value': '3M'}],
                        value="W", clearable = False, searchable = False, style = {'width': '100px', 'height': '30px'})
                , width = 3),
                dbc.Col(html.P(""), width = 1)
            ]),
            dbc.Row(id="kpi_metric")
        ], width = 3)
    ]),

    html.Div(style={'height': '5px'}),

    dcc.Tabs(id="dashboard_view", value="analytics", children=[
        dcc.Tab(label="Analytical View 🔍", value="analytics", style={"textAlign": "center", "border": "2px solid #117200", "backgroundColor": "rgb(198,240,215)", "color": "black"},
                selected_style={"borderTop": "3px solid #0f6800", "backgroundColor": "rgb(160, 225, 195)"},
                children=[
                    html.Div([

                    html.Hr(style={"height": "2px", "width": "100%", "backgroundColor": "#000000", "opacity": "unset", "opacity":"1", "margin": "0px"}),

                    dbc.Button(
                        [html.Span("Dashboard Filters", style={"float": "left"}), html.Span("▼", style={"float": "right"})],
                        id="dashboard_filters", n_clicks=0,
                        style={"width": "100%", "justify-content": "left",
                               "align-items": "center", 'border-radius': '0', "margin": "auto",
                               "white-space": "nowrap", "padding-right": "20px"},
                        color="success"),

                    html.Div(id="dashboard_filters_container", style={"display": "none"}, children=[
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Img(src=clock, alt="Clock", style={"width": "20px"}),
                                    html.Label("Time View", style={"font-size": "16px", "font-weight": "bold", "margin-left": "10px"})
                                    ],
                                style={"margin-top": "5px", "margin-bottom": "15px", "display": "flex", "flex-direction": "row", "justify-content": "center", "align-items": "center"}
                                ),
                                dbc.Row(
                                    dcc.Dropdown(
                                        id='time_view',
                                        options=[
                                            {'label': 'Day', 'value': 1},
                                            {'label': 'Week', 'value': 7},
                                            {'label': 'Month', 'value': 30},
                                            {'label': 'Quarter', 'value': 90},
                                            {'label': 'Year', 'value': 365}],
                                        value=365, clearable = False, searchable = False)
                                )
                            ], width = 4),
                            dbc.Col([
                                html.Div([
                                    html.Img(src=platform, alt="Clock", style={"width": "20px"}),
                                    html.Label("Platform", style={"font-size": "16px", "font-weight": "bold", "margin-left": "10px"})
                                    ],
                                style={"margin-top": "5px", "margin-bottom": "15px", "display": "flex", "flex-direction": "row", "justify-content": "center", "align-items": "center"}
                                ),
                                dbc.Row(
                                    dcc.Dropdown(id="platform_dropdown",
                                                 options=[{"label": "Select All", "value": "all"}] + [{"label": i.title(), "value": i} for i in df["platform_contents"].unique()],
                                                 value="all", placeholder="Select Content Platform", clearable = False, searchable = False)
                                )
                            ], width = 4),
                            dbc.Col([
                                html.Div([
                                    html.Img(src=alert, alt="Clock", style={"width": "20px"}),
                                    html.Label("Alert", style={"font-size": "16px", "font-weight": "bold", "margin-left": "10px"})
                                    ],
                                style={"margin-top": "5px", "margin-bottom": "15px", "display": "flex", "flex-direction": "row", "justify-content": "center", "align-items": "center"}
                                ),
                                dbc.Row(
                                    dcc.Dropdown(id="alert_dropdown",
                                                 options=[{"label": "Select All", "value": "all"}] + [{"label": i, "value": i} for i in df["alert_contents"].unique() if ((str(i).lower() != "nan") and (str(i).lower() != "no"))],
                                                 value="all", placeholder="Select Alert", clearable = False, searchable = False)
                                )
                            ], width = 4)
                        ], style={'margin': '20px'}),
                        html.Hr(style={"height": "3px", "width": "100%", "backgroundColor": "#000000", "opacity": "unset", "opacity":"1"})
                    ]),

                    html.Div(style={'height': '20px'}),

                    html.Div(
                        dmc.SegmentedControl(
                            id="user_control", value=user_list[0],
                            data = [{"value": i, "label": i.title()} for i in user_list],
                            color="green", radius="md", size="md"
                        ), style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}
                    ),

                    html.Div(style={'height': '30px'}),

                    dbc.Row([
                        dbc.Col([
                            html.Div(children=[
                                dmc.Avatar(size="lg", radius="xl"),
                                dmc.Text(user_list[0], id="user", weight=500),

                                html.Div(style={"height": "100px"}),
                                html.Div(id="user_platform_kpi"),

                                html.Div(style={"height": "30px"}),
                                html.Div(id="user_alert_kpi")
                            ], style={"margin": "20px"})
                        ], width=4),
                        dbc.Col([
                            html.H4("User Content Classification", style={"textAlign": "center"}),
                            dcc.Graph(id = "content_classification_pie_chart", config=dict(displayModeBar=False))
                        ], width=4),
                        dbc.Col([
                            html.H4("Content Alert", style={"textAlign": "center"}),
                            dcc.Graph(id = "content_alert_bar_chart", config=dict(displayModeBar=False))
                        ], width=4)
                    ]),

                    html.Div(style={'height': '20px'}),

                    dbc.Row([
                        dbc.Col([
                            html.Div(style={'position': 'relative'}, children=[
                                dcc.Graph(id="comment_alert_line_chart", config=dict(displayModeBar=False)),
                                html.Div([
                                    dmc.RadioGroup(children=[dmc.Radio("All", value="all", color="orange")],
                                                   id="comment_alert_line_chart_filter", value="all", size="sm")
                                ], style={'position': 'absolute', 'top': '20px', 'right': '10px', 'background-color': 'white', 'z-index': '1'})
                            ])
                        ], width=8),
                        dbc.Col([
                            html.H4("Comment Received Classification", style={"textAlign": "center"}),
                            dcc.Graph(id = "comment_classification_sunburst_chart", config=dict(displayModeBar=False))
                        ], width=4)
                    ])
                ])
            ]
        ),
        dcc.Tab(label="Generate Report 📋", value="report", style={"textAlign": "center", "border": "2px solid #117200", "backgroundColor": "rgb(198,240,215)", "color": "black"},
                selected_style={"borderTop": "3px solid #0f6800", "backgroundColor": "rgb(160, 225, 195)"},
                children=[])
    ], style={"width": "100%"})
])
#Dashboard Clock
@dashboard.callback(
    Output('current-time', 'children'),
    Input('Time', 'n_intervals')
)
def update_time(n):
    australia_timezone = pytz.timezone("Australia/Sydney")
    current_datetime = str(datetime.now(australia_timezone).strftime("%d-%b-%Y %I:%M:%S %p"))
    return f"Date & Time: {current_datetime}"


#KPI Metric
@dashboard.callback(
    Output("kpi_metric", "children"),
    [Input("kpi_dropdown", "value")]
)
def update_kpi(interval):
    kpi_df = df[(df["alert_contents"].str.lower() != "no") & (df["alert_contents"].str.lower() != "")]
    kpi_df["createTime_contents"] = pd.to_datetime(kpi_df["createTime_contents"])
    kpi_df = kpi_df.groupby(pd.Grouper(key = "createTime_contents", freq = interval))["id_contents"].nunique()
    kpi_df = kpi_df.reset_index()
    kpi_df = kpi_df.sort_values(by = ["createTime_contents"], ascending = False)
    kpi_df = kpi_df.reset_index()

    difference = int(kpi_df["id_contents"][0]) - int(kpi_df["id_contents"][1])
    color = "red" if difference > 0 else "green"
    arrow = "↑" if difference > 0 else "↓"

    return [
        dbc.Col(html.P(str(kpi_df["createTime_contents"][0].strftime("%d %b %y")), style={"float": "left"}), width = 4),
        dbc.Col(html.H1(str(difference) + arrow, style={"color": color, "textAlign": "center"}), width = 4),
        dbc.Col(html.P(str(kpi_df["createTime_contents"][1].strftime("%d %b %y")), style={"float": "right"}), width = 4)
    ]


#Visibility of the filters
@dashboard.callback(
    Output("dashboard_filters_container", "style"),
    Output("dashboard_filters", "children"),
    Input("dashboard_filters", "n_clicks"),
    prevent_initial_call=True
)
def toggle_filters_container(n_clicks):
    if(n_clicks % 2 == 1):
        return {"display": "block"}, [html.Span("Dashboard Filters", style={"float": "left"}), html.Span("▲", style={"float": "right"})]
    return {"display": "none"}, [html.Span("Dashboard Filters", style={"float": "left"}), html.Span("▼", style={"float": "right"})]


#Child List Select
@dashboard.callback(
    Output('user', 'children'),
    Input('user_control', 'value')
)
def update_display(child_name):
    return child_name


#User Platform KPI
@dashboard.callback(
    Output("user_platform_kpi", "children"),
    [Input("time_view", "value"), Input('user_control', 'value')]
)
def update_card_platform_kpi(interval, user_child):
    card_platform_df = df.copy()

    card_platform_df = card_platform_df[card_platform_df["name_childrens"] == user_child]
    card_platform_df["createTime_contents"] = pd.to_datetime(card_platform_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
    card_platform_df = card_platform_df[(card_platform_df["createTime_contents"] >= datetime.today() - timedelta(days=interval))]
    card_platform_df = card_platform_df[(card_platform_df["alert_contents"].str.lower() != "no") & (card_platform_df["alert_contents"].str.lower() != "")]
    card_platform_df = card_platform_df.groupby(by=["name_childrens", "platform_contents"], as_index = False)["id_contents"].nunique()
    card_platform_df.columns = ["name", "platform", "count"]

    kpi_elements = [html.Div([
        html.Div(
            html.P(row["platform"], style={"text-align": "center", "font-size": "14px", "margin": "0px", "width": "50px"}),
            style={"display": "flex", "justify-content": "center"}
        ),
        html.Div(
            html.P(row["count"], style={"text-align": "center", "font-weight": "bold", "font-size": "18px", "margin": "auto"}),
            style={"background-color": "lightblue", "width": "50px", "height": "50px", "border-radius": "10px", "display": "flex", "flex-direction": "column", "align-items": "center", "justify-content": "center"}
        )
    ], style={"display": "flex", "flex-direction": "column", "align-items": "center", "margin-right": "20px"}) for index, row in card_platform_df.iterrows()]

    return html.Div(kpi_elements, style={"margin-left": "0px", "display": "flex", "flex-direction": "row"})


#User Alert KPI
@dashboard.callback(
    Output("user_alert_kpi", "children"),
    [Input("time_view", "value"), Input('user_control', 'value')]
)
def update_card_alert_kpi(interval, user_child):
    card_alert_df = df.copy()

    card_alert_df = card_alert_df[card_alert_df["name_childrens"] == user_child]
    card_alert_df["createTime_contents"] = pd.to_datetime(card_alert_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
    card_alert_df = card_alert_df[(card_alert_df["createTime_contents"] >= datetime.today() - timedelta(days=interval))]
    card_alert_df = card_alert_df[card_alert_df["result_contents"].str.lower() != "no"]
    card_alert_df = card_alert_df.groupby(by = ["result_contents"], as_index = False)["id_contents"].nunique()
    card_alert_df.columns = ["classification", "count"]

    kpi_elements = [
        html.Div([
            html.P(row["count"], style={"text-align": "left", "font-size": "14px", "font-weight": "bold", "margin": "0"}),
            html.P(row["classification"], style={"text-align": "left", "font-size": "15px", "margin": "auto"})
            ], style={"width": "50%"}) for index, row in card_alert_df.iterrows()
    ]

    kpi_elements = [html.Div(kpi_elements[i:i+2], style={"display": "flex", "flex-direction": "row", "margin": "10px"}) for i in range(0, len(kpi_elements), 2)]
    return html.Div(kpi_elements)


#Content Classification Pie Chart
@dashboard.callback(
    Output('content_classification_pie_chart', 'figure'),
    [Input("time_view", "value"), Input('user_control', 'value'), Input("platform_dropdown", "value"), Input("alert_dropdown", "value")]
)
def update_pie_chart(interval, user_child, platform, alert):
    result_contents_df = df.copy()

    result_contents_df["createTime_contents"] = pd.to_datetime(result_contents_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
    result_contents_df = result_contents_df[(result_contents_df["createTime_contents"] >= datetime.today() - timedelta(days=interval))]
    result_contents_df = result_contents_df[result_contents_df["name_childrens"] == user_child]
    if(platform != "all"):
        result_contents_df = result_contents_df[result_contents_df["platform_contents"] == platform]
    if(alert != "all"):
        result_contents_df = result_contents_df[result_contents_df["alert_contents"] == alert]

    result_contents_df = result_contents_df[result_contents_df["result_contents"].str.lower() != "no"]
    result_contents_df = result_contents_df.groupby(by = ["result_contents"], as_index = False)["id_contents"].nunique()
    result_contents_df.columns = ["classification", "count"]

    content_classification = px.pie(result_contents_df, values = "count", names = "classification")
    content_classification.update_traces(marker=dict(line=dict(color='black', width=1)), hole = 0.6)
    content_classification.update_layout(title={"text": "Highest Classification", "x": 0.5, "xanchor": "center"})
    content_classification.update_layout(margin=dict(l=50, r=50, t=50, b=50), legend={"orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.08, "font": {"size": 10}})

    try:
        highest_value = result_contents_df.loc[result_contents_df["count"].idxmax(), "classification"]
        content_classification.add_annotation(text="<b>" + "<br>".join(highest_value.split(" ")) + "</b>", x=0.5, y=0.5, showarrow=False, font=dict(size=18))
    except Exception as e:
        highest_value = "No Data Found"
        content_classification.add_annotation(text="<b>" + "<br>".join(highest_value.split(" ")) + "</b>", x=0.5, y=0.5, showarrow=False, font=dict(size=18))

    return content_classification


#Content Alert Bar Chart
@dashboard.callback(
    Output('content_alert_bar_chart', 'figure'),
    [Input("time_view", "value"), Input('user_control', 'value'), Input("platform_dropdown", "value"), Input("alert_dropdown", "value")]
)
def update_bar_chart(interval, user_child, platform, alert):
    alert_contents_df = df.copy()

    alert_contents_df["createTime_contents"] = pd.to_datetime(alert_contents_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
    alert_contents_df = alert_contents_df[(alert_contents_df["createTime_contents"] >= datetime.today() - timedelta(days=interval))]
    alert_contents_df = alert_contents_df[alert_contents_df["name_childrens"] == user_child]
    if(platform != "all"):
        alert_contents_df = alert_contents_df[alert_contents_df["platform_contents"] == platform]
    if(alert != "all"):
        alert_contents_df = alert_contents_df[alert_contents_df["alert_contents"] == alert]

    alert_contents_df = alert_contents_df[(alert_contents_df["alert_contents"].str.lower() != "no") & (df["alert_contents"].str.lower() != "")]
    alert_contents_df = alert_contents_df.groupby(by = ["alert_contents", "platform_contents"], as_index = False)["id_contents"].nunique()
    alert_contents_df.columns = ["alert", "platform", "count"]
    alert_contents_df["alert"] = pd.Categorical(alert_contents_df["alert"], categories = ["High", "Medium", "Low"], ordered = True)
    alert_contents_df = alert_contents_df.sort_values(by="alert")

    content_alert = px.bar(alert_contents_df, x = "alert", y = "count", color = "platform", text_auto=True)
    content_alert.update_traces(width = 0.4, marker_line=dict(color='black', width=1))
    content_alert.update_layout(xaxis_title = "Alert", yaxis_title = "Count", legend_title_text = "", xaxis_showgrid = False, yaxis_showgrid = False)
    content_alert.update_layout(legend=dict(orientation="h", y=1.15, traceorder="grouped"), legend_xanchor="left")
    return content_alert


#Comment Classification Sunburst Chart
@dashboard.callback(
    Output('comment_classification_sunburst_chart', 'figure'),
    [Input("time_view", "value"), Input('user_control', 'value'), Input("platform_dropdown", "value"), Input("alert_dropdown", "value")]
)
def update_sunburst_chart(interval, user_child, platform, alert):
    result_comments_df = df.copy()

    result_comments_df["createTime_contents"] = pd.to_datetime(result_comments_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
    result_comments_df = result_comments_df[(result_comments_df["createTime_contents"] >= datetime.today() - timedelta(days=interval))]
    result_comments_df = result_comments_df[result_comments_df["name_childrens"] == user_child]
    if(platform != "all"):
        result_comments_df = result_comments_df[result_comments_df["platform_contents"] == platform]
    if(alert != "all"):
        result_comments_df = result_comments_df[result_comments_df["alert_contents"] == alert]

    result_comments_df = result_comments_df[(result_comments_df["result_comments"].str.lower() != "no") & (df["result_comments"].str.lower() != "")]
    result_comments_df = result_comments_df.groupby(by = ["result_comments", "platform_comments"], as_index = False)["id_contents"].nunique()
    result_comments_df.columns = ["classification", "platform", "count"]

    comment_classification = px.sunburst(result_comments_df, path=['classification', 'platform'], values='count')
    comment_classification.update_traces(marker=dict(line=dict(color='black', width=1)))
    comment_classification.update_layout(title={"text": "Select to see platform", "x": 0.5, "xanchor": "center"})
    return comment_classification


#Comment Alert Line Chart Filter
@dashboard.callback(
    [Output('comment_alert_line_chart_filter', 'children'), Output('comment_alert_line_chart_filter', 'value')],
    [Input("time_view", "value"), Input('user_control', 'value')]
)
def update_line_filter(interval, user_child):
    alert_comments_filter_df = df.copy()

    alert_comments_filter_df["createTime_contents"] = pd.to_datetime(alert_comments_filter_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
    alert_comments_filter_df = alert_comments_filter_df[(alert_comments_filter_df["createTime_contents"] >= datetime.today() - timedelta(days=interval))]
    alert_comments_filter_df = alert_comments_filter_df[alert_comments_filter_df["name_childrens"] == user_child]
    alert_comments_filter_df = alert_comments_filter_df[(alert_comments_filter_df["alert_comments"].str.lower() != "no") & (alert_comments_filter_df["alert_comments"].str.lower() != "")]

    if len([i for i in alert_comments_filter_df["platform_comments"].unique() if str(i) != "nan"]) > 1:
        return [dmc.Radio("All", value="all", color="orange")] + [dmc.Radio(i.title(), value=i, color="orange") for i in alert_comments_filter_df["platform_comments"].unique() if str(i) != "nan"], "all"
    else:
        return [dmc.Radio("All", value="all", color="orange")], "all"


#Comment Alert Line Chart
@dashboard.callback(
    Output('comment_alert_line_chart', 'figure'),
    [Input("time_view", "value"), Input('user_control', 'value'), Input('comment_alert_line_chart_filter', 'value')]
)
def update_line_chart(interval, user_child, comment_platform):
    alert_comments_df = df.copy()

    alert_comments_df["createTime_contents"] = pd.to_datetime(alert_comments_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
    alert_comments_df = alert_comments_df[(alert_comments_df["createTime_contents"] >= datetime.today() - timedelta(days=interval))]
    alert_comments_df = alert_comments_df[alert_comments_df["name_childrens"] == user_child]
    alert_comments_df = alert_comments_df[(alert_comments_df["alert_comments"].str.lower() != "no") & (alert_comments_df["alert_comments"].str.lower() != "")]
    alert_comments_df["commentTime_comments"] = pd.to_datetime(alert_comments_df["commentTime_comments"]).dt.date
    alert_comments_df = alert_comments_df.groupby(by = ["commentTime_comments", "platform_comments"], as_index = False)["id_contents"].nunique()
    alert_comments_df.columns = ["commentTime", "platform", "count"]

    if(comment_platform == "all"):
        comment_alert = px.area(alert_comments_df, x="commentTime", y="count", color="platform")
        comment_alert.update_layout(legend=dict(orientation='h', x=0.01, y=0.95, xanchor='left', yanchor='top'))
    else:
        alert_comments_df = alert_comments_df[alert_comments_df["platform"] == comment_platform]
        comment_alert = px.area(alert_comments_df, x="commentTime", y="count")

    comment_alert.update_layout(title = "<b>Trend of Alerts based on Comments Received</b>", xaxis_title = "Time Period", yaxis_title = "Count")
    comment_alert.update_layout(xaxis_showgrid = False, yaxis_showgrid = True, margin=dict(r=0))
    comment_alert.update_traces(mode = "lines", line=dict(width=3))
    return comment_alert


#Running Application
if __name__ == '__main__':
    dashboard.run_server(debug=False)
