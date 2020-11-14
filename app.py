#!/usr/bin/python

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly

import pandas as pd
import numpy as np
from funcs import zsl

# ==============================================================================

colors = {
    "background": "#4d5166",
    "white": "#ffffff",
    "black": "#000000",
    "red": "#fc4e03",
    "green": "#20bd67",
    "light_bg": "#676b82",
    "blue": "#3477eb",
    "light_gray": "#b8b8b8"
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "background-color": colors["light_bg"]
}

CONTENT_STYLE = {
    "margin-left": "16rem",
    "background-color": colors["light_bg"]
}

# ==============================================================================

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

sidebar = dbc.Container(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "This is a test!", className="lead"
        ),
        dbc.Nav(
            [
                dbc.Container([
                    dbc.Card([
                        dbc.CardHeader("Period"),
                        dbc.CardBody(id="ind-period", children=[
                            dbc.Input(id="period-input", min=1, max=48, step=1,
                                      type="number", value=48, style={"textAlign": "center"})
                        ])
                    ])
                ], style={"textAlign": "center"}),
                dbc.Container([
                    dbc.Card([
                        dbc.CardHeader("Time Frame"),
                        dbc.CardBody(id="tf-cardbody", children=[
                            dcc.Dropdown(id="tf-dropdown", options=[
                                {"label": "1M", "value": 1},
                                {"label": "5M", "value": 5},
                                {"label": "15M", "value": 15},
                                {"label": "30M", "value": 30}],
                                value=15, clearable=False, searchable=False)
                        ])
                    ])
                ], style={"textAlign": "center"}),
                dbc.Container([
                    dbc.Card([
                        dbc.CardHeader("St Dev"),
                        dbc.CardBody(id="card-body", children=[
                            html.H2(id="stdev")
                        ])
                    ])
                ], style={"textAlign": "center"})
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE
)

content = html.Div(id="page-content", children=[
    dcc.Graph(id="live-chart-update", responsive=True, style={"height": "100vh"}, config={"displayModeBar": False})
], style=CONTENT_STYLE)

interval = dcc.Interval(id="interval-component", interval=10000, n_intervals=0)

app.layout = dbc.Container([sidebar, content, interval], fluid=True)

# === === === === === === === === === CALLBACKS === === === === === === === ===

@app.callback(
    Output("stdev", "children"),
    Output("live-chart-update", "figure"),
    [Input("interval-component", "n_intervals"),
    Input("tf-dropdown", "value"),
    Input("period-input", "value")]
    )
def update_graph_live(n, dropdown_selection, period):

    # get data -----------------------------------------------------------------
    N = 96
    x = np.arange(N)
    e, s, d, m = zsl(M=period, interval=dropdown_selection)

    df = d

    trace1 = go.Candlestick(x=x, open=df.open, high=df.high, low=df.low, close=df.close,
                        decreasing={"fillcolor": colors["red"],
                                    "line": {"color": colors["red"], "width": 1}},
                        increasing={"fillcolor": colors["green"],
                                    "line": {"color": colors["green"], "width": 1}}, name="BTCUSD")
    trace2 = go.Scatter(x=x, y=m, line=dict(color=colors["blue"], width=2), name="EMA")
    trace3 = go.Scatter(x=x, y=e, name="ZSL")

    fig = make_subplots(rows=2, cols=1, row_heights=[0.75, 0.25], vertical_spacing=0.005,
                        shared_xaxes=True, print_grid=False)

    fig.add_trace(trace1, 1, 1)
    fig.add_trace(trace2, 1, 1)
    fig.add_trace(trace3, 2, 1)

    fig.update(layout_xaxis_rangeslider_visible=False)

    fig.update_layout(yaxis={"side": "right", "dtick": 50},
                      yaxis2={"side": "right", "dtick": 0.5, "range": [-1,1]},
                      plot_bgcolor=colors["background"], paper_bgcolor=colors["light_bg"],
                      legend_orientation="h", legend={"y": 1, "x": 0},
                      font={"color": colors["white"]}, dragmode="pan", hovermode="x unified",
                      margin={"b": 20, "t": 0, "l": 0, "r": 20}, hoverdistance=0,
                      xaxis_range=[-1, N+10])

    fig.update_xaxes(zeroline=False, fixedrange=True, showticklabels=False,
                     showspikes=True, spikethickness=1, spikecolor=colors["light_gray"],
                     spikemode="across", spikesnap="cursor", spikedash="dot",
                     gridcolor=colors["light_bg"])
    fig.update_yaxes(zeroline=False, fixedrange=True,
                     showspikes=True, spikethickness=1, spikecolor=colors["light_gray"],
                     spikemode="across", spikesnap="cursor", spikedash="dot",
                     gridcolor=colors["light_bg"])

    fig.update_traces(xaxis="x", hoverinfo="none")

    return "%.0f" % s.mean(), fig

if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
