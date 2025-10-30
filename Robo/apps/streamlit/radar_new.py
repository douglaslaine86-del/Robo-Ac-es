import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import requests
import datetime
import time
import os
from dotenv import load_dotenv
from datetime import date

# Carregar variáveis de ambiente
load_dotenv()

# API Keys
TWELVE_DATA_API_KEY = os.getenv('TWELVE_DATA_API_KEY', 'd8aa993b9ae14784b7a833406cc52c88')
FOOTBALL_DATA_API_KEY = os.getenv('FOOTBALL_DATA_API_KEY', 'cd267ac93b09491ca93184b7603432f3')

# ==================== FUNÇÕES DE FUTEBOL ====================

def pegar_jogos_hoje():
    """Busca jogos do dia atual"""
    hoje = date.today().isoformat()
    url = f"https://api.football-data.org/v4/matches?dateFrom={hoje}&dateTo={hoje}"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("matches", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar jogos: {e}")
        return []

def media_gols_time(time_id):
    """Calcula média de gols dos últimos 5 jogos de um time"""
    url = f"https://api.football-data.org/v4/teams/{time_id}/matches?limit=5"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        jogos = response.json().get("matches", [])
        
        gols_marcados = 0
        gols_sofridos = 0
        
        for jogo in jogos:
            if jogo['status'] == 'FINISHED':
                if jogo['homeTeam']['id'] == time_id:
                    gols_marcados += jogo['score']['fullTime']['home']
                    gols_sofridos += jogo['score']['fullTime']['away']
                else:
                    gols_marcados += jogo['score']['fullTime']['away']
                    gols_sofridos += jogo['score']['fullTime']['home']
        
        n = len(jogos) if len(jogos) > 0 else 1
        return gols_marcados/n, gols_sofridos/n
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar estatísticas do time: {e}")
        return 0, 0

def confronto_direto(id1, id2):
    """Analisa confronto direto entre dois times"""
    url = f"https://api.football-data.org/v4/matches?teamIds={id1},{id2}&limit=5"
    headers = {"X-Auth-Token": FOOTBALL_DATA_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        jogos = response.json().get("matches", [])
        
        v1 = 0
        v2 = 0
        
        for jogo in jogos:
            if jogo['status'] == 'FINISHED':
                if jogo['homeTeam']['id'] == id1:
                    if jogo['score']['fullTime']['home'] > jogo['score']['fullTime']['away']:
                        v1 += 1
                    elif jogo['score']['fullTime']['away'] > jogo['score']['fullTime']['home']:
                        v2 += 1
                else:
                    if jogo['score']['fullTime']['away'] > jogo['score']['fullTime']['home']:
                        v1 += 1
                    elif jogo['score']['fullTime']['home'] > jogo['score']['fullTime']['away']:
                        v2 += 1
        
        return v1, v2
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar confronto direto: {e}")
        return 0, 0

def calcular_probabilidade(gols_casa, gols_fora, v_confronto_casa, v_confronto_fora, peso_casa=1.1):
    """Calcula probabilidades de resultado"""
    score_casa = gols_casa * peso_casa + v_confronto_casa
    score_fora = gols_fora + v_confronto_fora
    total = score_casa + score_fora
    
    if total == 0:
        return 33.33, 33.33, 33.33
    
    prob_casa = round((score_casa/total)*100, 2)
    prob_fora = round((score_fora/total)*100, 2)
    prob_empate = round(100 - prob_casa - prob_fora, 2)
    
    return prob_casa, prob_empate, prob_fora

# ==================== FUNÇÕES DE AÇÕES ====================

def get_real_data(asset, interval="1min", outputsize=180):
    # Para ativos internacionais, o próprio nome já é o símbolo
    symbol = asset
    
    # Mapear símbolos para formato correto da API
    if asset == "BTC":
        symbol = "BTC/USD"
    
    url = f"https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": TWELVE_DATA_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "values" not in data:
            return {"error": f"Dados não encontrados para {asset}"}
        
        df = pd.DataFrame(data["values"])
        df = df.iloc[::-1].reset_index(drop=True)  # Inverter ordem
        
        # Converter colunas para float
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        
        # Volume é opcional (pode não existir para forex)
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'])
        else:
            # Gerar volume simulado para forex
            df['volume'] = np.random.randint(1000, 10000, len(df))
        
        return df
        
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro na API: {str(e)}"}
    except Exception as e:
        return {"error": f"Erro ao processar dados: {str(e)}"}

def get_data(asset):
    """Função principal para obter dados"""
    return get_real_data(asset)

def get_signal(df):
    """Gera sinal de compra/venda baseado em análise técnica"""
    if df.empty or 'close' not in df.columns:
        return "❌ Dados insuficientes para análise"
    
    # Calcular médias móveis
    df['ma7'] = df['close'].rolling(window=7).mean()
    df['ma21'] = df['close'].rolling(window=21).mean()
    
    # Verificar se há dados suficientes
    if len(df) < 21:
        return "❌ Dados insuficientes para análise técnica"
    
    # Obter últimos valores
    current_price = df['close'].iloc[-1]
    ma7_current = df['ma7'].iloc[-1]
    ma21_current = df['ma21'].iloc[-1]
    
    # Calcular variação de preço
    price_change_1d = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
    
    # Verificar cruzamento das médias móveis
    ma7_above_ma21 = ma7_current > ma21_current
    
    # Lógica de sinal mais detalhada
    if ma7_above_ma21 and df['ma7'].iloc[-2] <= df['ma21'].iloc[-2]:
        return f"🔼 Sinal de COMPRA: MA7 cruzou acima da MA21. ({price_change_1d:+.2f}%)"
    elif not ma7_above_ma21 and df['ma7'].iloc[-2] >= df['ma21'].iloc[-2]:
        return f"🔽 Sinal de VENDA: MA7 cruzou abaixo da MA21. ({price_change_1d:+.2f}%)"
    elif ma7_above_ma21 and current_price > ma7_current:
        return f"📊 Tendência lateral ALTA: MA7 > MA21. ({price_change_1d:+.2f}%)"
    elif not ma7_above_ma21 and current_price < ma7_current:
        return f"📊 Tendência lateral BAIXA: MA7 < MA21. ({price_change_1d:+.2f}%)"
    else:
        return f"📊 Sem sinal claro. Variação: {price_change_1d:+.2f}%"

# ==================== INTERFACE PRINCIPAL ====================

# Sistema de abas
tab1, tab2 = st.tabs(["📈 Radar de Ações", "⚽ Análise de Futebol"])

with tab1:
    # Título da aba de ações
    st.markdown("<h2 style='color: #fff; margin-bottom: 0px; margin-top: 10px; font-size:2rem; text-align:left;'>Radar de Ações - Tempo Real e Indicadores</h2>", unsafe_allow_html=True)

    # Dropdown para seleção de ativo
    assets = ['AAPL', 'MSFT', 'BTC', 'USD/BRL']
    selected_asset = st.selectbox("Selecione o ativo", assets, index=0, key="asset_select")

    # Atualização automática dos dados em tempo real
    refresh_interval = st.sidebar.slider('Intervalo de atualização (segundos)', 2, 30, 5)

    # Obter dados reais da Twelve Data
    df = get_data(selected_asset)

    # Definir signal com valor padrão
    signal = "❌ Não foi possível analisar os dados"

    # Sempre mostrar análise, mesmo se houver erro
    st.markdown("---")
    st.markdown(f"<h2 style='color: #000; text-align: center; margin: 20px 0;'>📊 Análise Técnica</h2>", unsafe_allow_html=True)

    if isinstance(df, dict) and "error" in df:
        st.error(f"Erro ao obter dados da Twelve Data: {df['error']}")
        st.info("Verifique se o símbolo do ativo está correto e se sua API Key é válida.")
        signal = "❌ Erro ao carregar dados da API"
    elif isinstance(df, pd.DataFrame) and not df.empty:
        # Médias móveis
        if 'close' in df:
            df['ma7'] = df['close'].rolling(window=7).mean()
            df['ma21'] = df['close'].rolling(window=21).mean()

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
                name="Candles"
            ))
            
            # Adicionar médias móveis
            if 'ma7' in df and 'ma21' in df:
                fig.add_trace(go.Scatter(
                    x=xticks,
                    y=df['ma7'],
                    mode='lines',
                    name='MA7',
                    line=dict(color='orange', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=xticks,
                    y=df['ma21'],
                    mode='lines',
                    name='MA21',
                    line=dict(color='blue', width=2)
                ))

            fig.update_layout(
                title=f"{selected_asset} - Gráfico de Velas",
                xaxis_title="Tempo",
                yaxis_title="Preço",
                height=500,
                showlegend=True,
                plot_bgcolor='#1e1e1e',
                paper_bgcolor='#1e1e1e',
                font=dict(color='white'),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#333',
                    tickmode='linear',
                    tick0=0,
                    dtick=30
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#333'
                )
            )
            st.plotly_chart(fig, use_container_width=True)

        # Gráfico de volume
        with col2:
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Bar(
                x=xticks,
                y=df['volume'],
                name="Volume",
                marker_color='rgba(0,100,80,0.7)'
            ))
            
            fig_volume.update_layout(
                title=f"{selected_asset} - Volume",
                xaxis_title="Tempo",
                yaxis_title="Volume",
                height=500,
                showlegend=False,
                plot_bgcolor='#1e1e1e',
                paper_bgcolor='#1e1e1e',
                font=dict(color='white'),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#333',
                    tickmode='linear',
                    tick0=0,
                    dtick=30
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#333'
                )
            )
            st.plotly_chart(fig_volume, use_container_width=True)

        # Gráfico estilo Toro
        fig_toro = go.Figure()
        fig_toro.add_trace(go.Candlestick(
            x=xticks,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name="Candles"
        ))
        
        fig_toro.update_layout(
            title=f"{selected_asset} - Visão Geral",
            xaxis_title="Tempo",
            yaxis_title="Preço",
            height=700,
            showlegend=False,
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#1e1e1e',
            font=dict(color='white'),
            xaxis=dict(
                showgrid=True,
                gridcolor='#333',
                tickmode='linear',
                tick0=0,
                dtick=30
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#333'
            )
        )
        st.plotly_chart(fig_toro, use_container_width=True)
    else:
        # Caso quando não há dados válidos
        signal = "❌ Dados insuficientes para análise"

    # Análise principal (fora das colunas para sempre aparecer)
    st.markdown("---")
    # CSS customizado para forçar cor branca
    st.markdown("""
    <style>
    .signal-text {
        color: white !important;
        font-weight: bold;
        font-size: 18px;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background-color: #23272F; padding: 20px; border-radius: 10px; margin: 10px 0; border: 1px solid #444;'>
        <div class="signal-text">{signal}</div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    # Título da aba de futebol
    st.markdown("<h2 style='color: #fff; margin-bottom: 20px; font-size:2rem; text-align:left;'>⚽ Análise de Futebol - Probabilidades Pré-Jogo</h2>", unsafe_allow_html=True)
    
    # Configurações
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### ⚙️ Configurações")
        prob_minima = st.slider("Probabilidade mínima para destaque (%)", 50, 100, 60)
        peso_casa = st.slider("Peso do fator casa", 1.0, 1.5, 1.1, 0.1)
    
    with col2:
        st.markdown("### 📊 Jogos de Hoje")
        
        # Buscar jogos do dia
        with st.spinner("Buscando jogos do dia..."):
            jogos = pegar_jogos_hoje()
        
        if not jogos:
            st.warning("Nenhum jogo encontrado para hoje.")
        else:
            st.success(f"Encontrados {len(jogos)} jogos para hoje!")
            
            for i, jogo in enumerate(jogos):
                if jogo['status'] == 'SCHEDULED' or jogo['status'] == 'TIMED':
                    casa_id = jogo["homeTeam"]["id"]
                    fora_id = jogo["awayTeam"]["id"]
                    casa_nome = jogo["homeTeam"]["name"]
                    fora_nome = jogo["awayTeam"]["name"]
                    
                    # Buscar estatísticas
                    with st.spinner(f"Analisando {casa_nome} x {fora_nome}..."):
                        gols_casa, _ = media_gols_time(casa_id)
                        gols_fora, _ = media_gols_time(fora_id)
                        v_casa, v_fora = confronto_direto(casa_id, fora_id)
                        prob_casa, prob_empate, prob_fora = calcular_probabilidade(
                            gols_casa, gols_fora, v_casa, v_fora, peso_casa
                        )
                    
                    # Determinar cor do card baseado na probabilidade
                    max_prob = max(prob_casa, prob_empate, prob_fora)
                    if max_prob >= prob_minima:
                        card_color = "#1f77b4"  # Azul para destaque
                        border_color = "#ff6b6b"  # Borda vermelha
                    else:
                        card_color = "#2d3748"  # Cinza escuro
                        border_color = "#4a5568"  # Borda cinza
                    
                    # Card do jogo
                    st.markdown(f"""
                    <div style='background-color: {card_color}; padding: 20px; border-radius: 10px; margin: 15px 0; border: 2px solid {border_color};'>
                        <h3 style='color: white; margin: 0 0 15px 0; text-align: center;'>{casa_nome} x {fora_nome}</h3>
                        <div style='display: flex; justify-content: space-around; margin: 15px 0;'>
                            <div style='text-align: center;'>
                                <div style='color: #90EE90; font-size: 24px; font-weight: bold;'>{prob_casa}%</div>
                                <div style='color: white; font-size: 14px;'>Vitória Casa</div>
                            </div>
                            <div style='text-align: center;'>
                                <div style='color: #FFD700; font-size: 24px; font-weight: bold;'>{prob_empate}%</div>
                                <div style='color: white; font-size: 14px;'>Empate</div>
                            </div>
                            <div style='text-align: center;'>
                                <div style='color: #FFB6C1; font-size: 24px; font-weight: bold;'>{prob_fora}%</div>
                                <div style='color: white; font-size: 14px;'>Vitória Fora</div>
                            </div>
                        </div>
                        <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #4a5568;'>
                            <div style='color: white; font-size: 14px; margin: 5px 0;'>
                                📊 <strong>Média gols recentes:</strong> {round(gols_casa,1)} x {round(gols_fora,1)}
                            </div>
                            <div style='color: white; font-size: 14px; margin: 5px 0;'>
                                ⚔️ <strong>Vitórias confronto direto:</strong> {v_casa} x {v_fora}
                            </div>
                            <div style='color: white; font-size: 14px; margin: 5px 0;'>
                                🏠 <strong>Fator casa:</strong> {peso_casa}x
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Gráfico de probabilidades
                    fig_prob = go.Figure(data=[
                        go.Bar(
                            x=['Vitória Casa', 'Empate', 'Vitória Fora'],
                            y=[prob_casa, prob_empate, prob_fora],
                            marker_color=['#90EE90', '#FFD700', '#FFB6C1'],
                            text=[f'{prob_casa}%', f'{prob_empate}%', f'{prob_fora}%'],
                            textposition='auto',
                        )
                    ])
                    
                    fig_prob.update_layout(
                        title=f"Probabilidades - {casa_nome} x {fora_nome}",
                        xaxis_title="Resultado",
                        yaxis_title="Probabilidade (%)",
                        height=300,
                        showlegend=False,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(fig_prob, use_container_width=True)
                    
                    st.markdown("---")




