import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests

app = dash.Dash(__name__)
server = app.server

assets = ['WINFUT', 'WDOFUT']

def get_data(asset):
    try:
        r = requests.get(f"http://localhost:8000/realtime/{asset}")
        data = r.json() if r.text else []
    except Exception:
        data = []
    if data and isinstance(data, list) and len(data) > 0:
        df = pd.DataFrame(data)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
    else:
    n = 120  # Mais candles para ficar mais próximo
        if asset == 'WINFUT':
            base = 128000
        else:
            base = 5000
        open_ = np.random.uniform(base-200, base+200, n)
        close_ = open_ + np.random.uniform(-100, 100, n)
        high_ = np.maximum(open_, close_) + np.random.uniform(0, 80, n)
        low_ = np.minimum(open_, close_) - np.random.uniform(0, 80, n)
        df = pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=n, freq='min'),
            'open': open_,
            'high': high_,
            'low': low_,
            'close': close_,
            'volume': np.random.randint(1000, 50000, n)
        })
    return df

app.layout = html.Div(
    style={
        'backgroundColor': '#181A20',
        'height': '100vh',
        'width': '100vw',
        'padding': '0',
        'margin': '0',
        'display': 'flex',
        'flexDirection': 'column',
        'overflow': 'hidden'
    },
    children=[
        html.Div([
            html.H2("Radar de Ações - Tempo Real e Indicadores", style={'color': '#fff', 'margin': '10px 0 0 10px'}),
            dcc.Dropdown(
                id='asset-dropdown',
                options=[{'label': a, 'value': a} for a in assets],
                value=assets[0],
                style={'width': '300px', 'marginLeft': '10px', 'backgroundColor': '#23272F', 'color': '#fff'}
            ),
        ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', 'gap': '20px', 'marginBottom': '10px'}),
        html.Div([
            dcc.Graph(
                id='candlestick-graph',
                config={'displayModeBar': False},
                style={'height': '100vh', 'width': '100vw', 'padding': '0', 'margin': '0'}
            ),
            dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)
        ], style={'flex': '1', 'height': '100vh', 'width': '100vw', 'padding': '0', 'margin': '0', 'overflow': 'hidden'})
    ]
)

@app.callback(
    Output('candlestick-graph', 'figure'),
    [Input('asset-dropdown', 'value'), Input('interval-component', 'n_intervals')]
)
def update_graph(selected_asset, n):
    df = get_data(selected_asset)
    print('DataFrame recebido:', df.tail())
    required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    if df.empty or not all(col in df.columns for col in required_cols):
        fig = go.Figure()
        fig.add_annotation(text="Dados insuficientes ou ausentes.",
                           xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=20, color="red"))
        fig.update_layout(plot_bgcolor='#000', paper_bgcolor='#000', font=dict(color='#fff'))
        return fig
    df = df.sort_values('timestamp')
    # Indicadores
    if 'close' in df:
        df['ma7'] = df['close'].rolling(window=7).mean()
        df['ma21'] = df['close'].rolling(window=21).mean()
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.8, 0.2],
        vertical_spacing=0.02,
        subplot_titles=(None, None)
    )
    # Exibe todos os candles, mas só o último é atualizado
    candles = df.copy()
    candles['is_last'] = False
    candles.iloc[-1, candles.columns.get_loc('is_last')] = True
    fig.add_trace(go.Candlestick(
        x=candles['timestamp'],
        open=candles['open'],
        high=candles['high'],
        low=candles['low'],
        close=candles['close'],
        name='Candles',
        increasing_line_color='#00FF00',
        decreasing_line_color='#FF0000',
        showlegend=True,
        line_width=2,
        opacity=1,
        whiskerwidth=0.4
    ), row=1, col=1)
    # Médias móveis
    if 'ma7' in df:
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['ma7'],
            mode='lines',
            line=dict(color='yellow', width=1),
            name='MA 7',
            opacity=0.7,
            showlegend=True
        ), row=1, col=1)
    if 'ma21' in df:
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['ma21'],
            mode='lines',
            line=dict(color='orange', width=1),
            name='MA 21',
            opacity=0.7,
            showlegend=True
        ), row=1, col=1)
    # Painel inferior: volume
    fig.add_trace(go.Bar(
        x=df['timestamp'],
        y=df['volume'],
        marker_color='rgba(0,255,0,0.15)',
        marker_line_width=0,
        name='Volume',
        opacity=0.3
    ), row=2, col=1)
    fig.update_layout(
        xaxis=dict(showgrid=False, color='#fff', showline=True, showticklabels=True, zeroline=False, tickformat='%H:%M'),
        yaxis=dict(title='', showgrid=False, color='#fff', showline=True, showticklabels=True, zeroline=False, autorange=True),
        xaxis2=dict(showgrid=False, color='#fff', showline=True, showticklabels=True, zeroline=False, tickformat='%H:%M'),
        yaxis2=dict(title='Volume', showgrid=False, color='#fff', showline=True, showticklabels=True, zeroline=False, autorange=True),
        plot_bgcolor='#181A20',
        paper_bgcolor='#181A20',
        font=dict(color='#fff'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=12)),
        margin=dict(l=0, r=0, t=0, b=0),
        bargap=0.01,
        bargroupgap=0.005,
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
