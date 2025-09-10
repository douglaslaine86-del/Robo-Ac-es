import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import requests
import datetime

# Configuração da página para fullscreen e fundo escuroolha os 
st.set_page_config(
    page_title="Radar de Ações - Tempo Real e Indicadores",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📈"
)


# CSS customizado para fullscreen, sem caixa central, fundo escuro total
st.markdown(
    """
    <style>
    body, .main, .block-container {
        background-color: #181A20 !important;
    }
    .block-container {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        max-width: 100vw !important;
        width: 100vw !important;
        margin: 0 !important;
    }
    .stSelectbox > div > div {
        background-color: #23272F !important;
        color: #fff !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        width: 300px !important;
    }
    h1, h2, h3, h4, h5, h6, label, .stTextInput label {
        color: #fff !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título pequeno, alinhado à esquerda, sem espaço acima
st.markdown("<h2 style='color: #fff; margin-bottom: 0px; margin-top: 10px; font-size:2rem; text-align:left;'>Radar de Ações - Tempo Real e Indicadores</h2>", unsafe_allow_html=True)

# Dropdown alinhado à esquerda

import time
assets = ['AAPL', 'MSFT', 'BTC/USD', 'USD/BRL']
selected_asset = st.selectbox("Selecione o ativo", assets, index=0, key="asset_select")

# Atualização automática dos dados em tempo real
refresh_interval = st.sidebar.slider('Intervalo de atualização (segundos)', 2, 30, 5)


# Atualização automática dos dados em tempo real usando Streamlit
import time
df = get_data(selected_asset)
if 'close' in df:
    df['ma7'] = df['close'].rolling(window=7).mean()
    df['ma21'] = df['close'].rolling(window=21).mean()
signal = get_signal(df)
chart_placeholder = st.empty()
xticks = df.index.astype(str)
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=xticks,
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name='Candles',
    increasing_line_color='lime',
    decreasing_line_color='red',
    showlegend=True,
    line_width=2,
    opacity=1,
    whiskerwidth=0.4
))
fig.add_trace(go.Scatter(
    x=np.repeat(xticks, 2),
    y=np.column_stack((df['open'], df['close'])).flatten(),
    mode='lines',
    line=dict(color='gray', width=1, dash='dot'),
    name='Abertura-Fechamento',
    opacity=0.5,
    showlegend=True
))
fig.add_trace(go.Scatter(
    x=xticks, y=df['ma7'],
    mode='lines',
    line=dict(color='orange', width=2),
    name='MA 7',
    opacity=0.8
))
fig.add_trace(go.Scatter(
    x=xticks, y=df['ma21'],
    mode='lines',
    line=dict(color='yellow', width=2),
    name='MA 21',
    opacity=0.8
))
fig.add_trace(go.Bar(
    x=xticks, y=df['volume'],
    marker_color='rgba(0,255,0,0.15)',
    yaxis='y2',
    name='Volume',
    opacity=0.3
))
fig.update_layout(
    xaxis=dict(showgrid=False, color='#fff', type='category', tickmode='auto'),
    yaxis=dict(title='Preço', showgrid=False, color='#fff', autorange=True),
    yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, color='#fff', autorange=True),
    plot_bgcolor='#181A20',
    paper_bgcolor='#181A20',
    font=dict(color='#fff'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=14)),
    margin=dict(l=10, r=10, t=10, b=10),
    height=700,
    bargap=0,
    bargroupgap=0,
)
chart_placeholder.plotly_chart(fig, use_container_width=True)
st.markdown(f"<h3 style='color: #fff; margin-top: 10px;'>Análise: {signal}</h3>", unsafe_allow_html=True)
fig_toro = go.Figure(data=[go.Candlestick(
    x=df['timestamp'].dt.strftime('%H:%M'),
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    increasing_line_color='lime',
    decreasing_line_color='red',
    whiskerwidth=0.4,
    name='Candles',
    showlegend=False,
    line_width=6,
    opacity=1
)])
fig_toro.add_trace(go.Scatter(
    x=np.repeat(df['timestamp'].dt.strftime('%H:%M'), 2),
    y=np.column_stack((df['open'], df['close'])).flatten(),
    mode='lines',
    line=dict(color='gray', width=1, dash='dot'),
    name='Abertura-Fechamento',
    opacity=0.5,
    showlegend=False
))
fig_toro.update_layout(
    xaxis_title='Horário',
    yaxis_title='Preço',
    template='plotly_dark',
    showlegend=False,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(showgrid=False, type='category', tickmode='auto', nticks=5, tickfont=dict(size=8), tickangle=0),
    yaxis=dict(showgrid=False),
    height=350
)
st.plotly_chart(fig_toro, use_container_width=True)

# Função para buscar candles reais da Twelve Data
# Você precisa de uma API Key gratuita: https://twelvedata.com
TWELVE_DATA_API_KEY = "d8aa993b9ae14784b7a833406cc52c88"  # Troque pela sua chave

def get_real_data(asset, interval="1min", outputsize=180):
    # Para ativos internacionais, o próprio nome já é o símbolo
    symbol = asset
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={TWELVE_DATA_API_KEY}"
    try:
        r = requests.get(url)
        data = r.json()
        if "values" in data:
            df = pd.DataFrame(data["values"])
            df["timestamp"] = pd.to_datetime(df["datetime"])
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            df = df.sort_values("timestamp")
            return df
        else:
            # Retorna o erro para debug
            return {"error": data}
    except Exception as e:
        return {"error": str(e)}

# Simulação de dados
def get_data(asset):
    # Prioridade absoluta: apenas dados da Twelve Data
    df = get_real_data(asset)
    if isinstance(df, dict) and "error" in df:
        return df
    if df is not None:
        return df
    return None


# Obter dados reais da Twelve Data


import pandas as pd
df = get_data(selected_asset)

if isinstance(df, dict) and "error" in df:
    st.error('Erro ao obter dados da Twelve Data:')
    st.json(df["error"])
elif df is None:
    st.error('Não foi possível obter dados do Twelve Data para o ativo selecionado. Verifique sua API Key ou o símbolo do ativo.')
elif isinstance(df, pd.DataFrame) and not df.empty:
    # Médias móveis
    if 'close' in df:
        df['ma7'] = df['close'].rolling(window=7).mean()
        df['ma21'] = df['close'].rolling(window=21).mean()

    # Sinal de compra/venda
    def get_signal(df):
        if len(df) < 21:
            return "Aguardando dados suficientes para análise."
        if df['ma7'].iloc[-2] < df['ma21'].iloc[-2] and df['ma7'].iloc[-1] > df['ma21'].iloc[-1]:
            return "🔼 Sinal de COMPRA: MA7 cruzou acima da MA21."
        elif df['ma7'].iloc[-2] > df['ma21'].iloc[-2] and df['ma7'].iloc[-1] < df['ma21'].iloc[-1]:
            return "🔽 Sinal de VENDA: MA7 cruzou abaixo da MA21."
        else:
            return "Sem sinal claro de compra ou venda."

    signal = get_signal(df)

    # Layout lado a lado
    col1, col2 = st.columns(2)

    # Gráfico estilo Binance
    with col1:
        xticks = df.index.astype(str)
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=xticks,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Candles',
            increasing_line_color='lime',
            decreasing_line_color='red',
            showlegend=True,
            line_width=2,
            opacity=1,
            whiskerwidth=0.4
        ))
        fig.add_trace(go.Scatter(
            x=np.repeat(xticks, 2),
            y=np.column_stack((df['open'], df['close'])).flatten(),
            mode='lines',
            line=dict(color='gray', width=1, dash='dot'),
            name='Abertura-Fechamento',
            opacity=0.5,
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=xticks, y=df['ma7'],
            mode='lines',
            line=dict(color='orange', width=2),
            name='MA 7',
            opacity=0.8
        ))
        fig.add_trace(go.Scatter(
            x=xticks, y=df['ma21'],
            mode='lines',
            line=dict(color='yellow', width=2),
            name='MA 21',
            opacity=0.8
        ))
        fig.add_trace(go.Bar(
            x=xticks, y=df['volume'],
            marker_color='rgba(0,255,0,0.15)',
            yaxis='y2',
            name='Volume',
            opacity=0.3
        ))
        fig.update_layout(
            xaxis=dict(showgrid=False, color='#fff', type='category', tickmode='auto'),
            yaxis=dict(title='Preço', showgrid=False, color='#fff', autorange=True),
            yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, color='#fff', autorange=True),
            plot_bgcolor='#181A20',
            paper_bgcolor='#181A20',
            font=dict(color='#fff'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=14)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=700,
            bargap=0,
            bargroupgap=0,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h3 style='color: #fff; margin-top: 10px;'>Análise: {signal}</h3>", unsafe_allow_html=True)

    # Gráfico estilo Toro Trader
    with col2:
        fig_toro = go.Figure(data=[go.Candlestick(
            x=df['timestamp'].dt.strftime('%H:%M'),
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color='lime',
            decreasing_line_color='red',
            whiskerwidth=0.4,
            name='Candles',
            showlegend=False,
            line_width=6,
            opacity=1
        )])
        fig_toro.add_trace(go.Scatter(
            x=np.repeat(df['timestamp'].dt.strftime('%H:%M'), 2),
            y=np.column_stack((df['open'], df['close'])).flatten(),
            mode='lines',
            line=dict(color='gray', width=1, dash='dot'),
            name='Abertura-Fechamento',
            opacity=0.5,
            showlegend=False
        ))
        fig_toro.update_layout(
            xaxis_title='Horário',
            yaxis_title='Preço',
            template='plotly_dark',
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, type='category', tickmode='auto', nticks=5, tickfont=dict(size=8), tickangle=0),
            yaxis=dict(showgrid=False),
            height=700
        )
        st.plotly_chart(fig_toro, use_container_width=True)
