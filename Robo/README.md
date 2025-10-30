# 🤖 Robo-Ações - Sistema de Análise Financeira e Esportiva

Um sistema completo de análise em tempo real que combina análise técnica de ações com análise de probabilidades de jogos de futebol, utilizando APIs externas e tecnologias modernas.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Configuração](#-configuração)
- [Como Executar](#-como-executar)
- [APIs Utilizadas](#-apis-utilizadas)
- [Funcionalidades Detalhadas](#-funcionalidades-detalhadas)
- [Desenvolvimento](#-desenvolvimento)
- [Troubleshooting](#-troubleshooting)

## 🎯 Visão Geral

O **Robo-Ações** é uma aplicação web que oferece duas funcionalidades principais:

1. **📈 Radar de Ações**: Análise técnica em tempo real de ativos financeiros
2. **⚽ Análise de Futebol**: Cálculo de probabilidades para jogos de futebol

A aplicação é construída com arquitetura de microserviços usando Docker, proporcionando escalabilidade e facilidade de manutenção.

## ✨ Funcionalidades

### 📈 Radar de Ações
- **Análise em tempo real** de ativos (AAPL, MSFT, BTC, USD/BRL)
- **Gráficos de candlestick** interativos com Plotly
- **Indicadores técnicos**: Médias móveis (MA7 e MA21)
- **Sinais de compra/venda** baseados em cruzamento de médias
- **Análise de volume** de negociação
- **Hot-reload** para desenvolvimento ágil

### ⚽ Análise de Futebol
- **Busca de jogos** por data específica ou próximos dias
- **Cálculo de probabilidades** baseado em:
  - Média de gols dos últimos 5 jogos
  - Confronto direto entre times
  - Fator casa (ajustável)
- **Interface visual** com cards coloridos por probabilidade
- **Gráficos de barras** das probabilidades
- **Status dos jogos**: Finalizado, Agendado, Ao vivo

## 🛠 Tecnologias Utilizadas

### Backend
- **Python 3.10**
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para banco de dados
- **Redis** - Cache em memória
- **Requests** - Cliente HTTP para APIs

### Frontend
- **Streamlit** - Framework para aplicações web interativas
- **Plotly** - Gráficos interativos
- **HTML/CSS** - Customização de interface

### Infraestrutura
- **Docker & Docker Compose** - Containerização
- **SQLite** - Banco de dados (desenvolvimento)
- **Alpine Linux** - Imagem base leve

### APIs Externas
- **Twelve Data API** - Dados financeiros em tempo real
- **Football Data API** - Dados de futebol

## 📁 Estrutura do Projeto

```
Robo/
├── 📄 README.md                    # Este arquivo
├── 📄 docker-compose.yml           # Orquestração dos serviços
├── 📄 requirements.txt             # Dependências Python
├── 📄 .env                         # Variáveis de ambiente
├── 📄 Makefile                     # Comandos de desenvolvimento
├── 📄 Dockerfile.api               # Imagem da API
├── 📄 Dockerfile.streamlit         # Imagem do Streamlit
│
├── 📁 api/                         # Servidor FastAPI
│   ├── 📄 main.py                  # Aplicação principal
│   ├── 📄 models.py               # Modelos de dados
│   └── 📄 routers/                # Endpoints da API
│
├── 📁 apps/                        # Aplicações frontend
│   ├── 📁 streamlit/              # Dashboard Streamlit
│   │   └── 📄 radar.py            # Aplicação principal
│   └── 📁 dash/                   # Dashboard Dash (futuro)
│
├── 📁 core/                        # Lógica de negócio
│   ├── 📄 database.py             # Configuração do banco
│   └── 📄 config.py               # Configurações
│
├── 📁 services/                    # Serviços externos
│   ├── 📄 twelve_data.py          # Integração Twelve Data
│   └── 📄 football_data.py        # Integração Football Data
│
├── 📁 scripts/                     # Scripts utilitários
│   └── 📄 seed.py                 # População inicial do banco
│
└── 📁 Roboesporte.html            # Código original de futebol
```

## ⚙️ Pré-requisitos

- **Docker** (versão 20.10+)
- **Docker Compose** (versão 2.0+)
- **Git** (para clonar o repositório)

## 🔧 Configuração

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd Robo-Ac-es/Robo
```

### 2. Configure as variáveis de ambiente
Crie o arquivo `.env` na raiz do projeto:

```env
# API Keys
TWELVE_DATA_API_KEY=sua_chave_twelve_data
FOOTBALL_DATA_API_KEY=sua_chave_football_data

# Banco de dados
DATABASE_URL=sqlite:///./robo.db

# Redis
REDIS_URL=redis://localhost:6380
```

### 3. Obtenha as API Keys

#### Twelve Data API
1. Acesse [Twelve Data](https://twelvedata.com/)
2. Crie uma conta gratuita
3. Copie sua API key
4. Adicione no arquivo `.env`

#### Football Data API
1. Acesse [Football Data](https://www.football-data.org/)
2. Registre-se gratuitamente
3. Ative sua conta
4. Copie sua API key
5. Adicione no arquivo `.env`

## 🚀 Como Executar

### Método 1: Docker Compose (Recomendado)

```bash
# Construir e iniciar todos os serviços
docker compose up -d

# Verificar status dos containers
docker compose ps

# Ver logs
docker compose logs -f
```

### Método 2: Comandos individuais

```bash
# Construir as imagens
docker compose build

# Iniciar serviços específicos
docker compose up -d api
docker compose up -d streamlit
docker compose up -d db
docker compose up -d redis
```

### Método 3: Usando Makefile

```bash
# Construir tudo
make build

# Iniciar serviços
make up

# Popular banco de dados
make seed

# Executar backtest
make backtest
```

## 🌐 Acessando a Aplicação

Após executar os comandos acima, acesse:

- **📈 Dashboard Principal**: http://localhost:8501
- **🔧 API**: http://localhost:8000
- **📊 Documentação da API**: http://localhost:8000/docs

## 🔌 APIs Utilizadas

### Twelve Data API
- **Propósito**: Dados financeiros em tempo real
- **Endpoints utilizados**:
  - `/time_series` - Dados históricos de preços
- **Ativos suportados**: AAPL, MSFT, BTC/USD, USD/BRL
- **Limite**: 800 requests/dia (plano gratuito)

### Football Data API
- **Propósito**: Dados de futebol
- **Endpoints utilizados**:
  - `/matches` - Jogos por data
  - `/teams/{id}/matches` - Histórico de times
- **Limite**: 10 requests/minuto (plano gratuito)

## 📊 Funcionalidades Detalhadas

### Radar de Ações

#### Indicadores Técnicos
- **MA7**: Média móvel de 7 períodos
- **MA21**: Média móvel de 21 períodos
- **Volume**: Volume de negociação

#### Sinais de Trading
- **🔼 COMPRA**: MA7 cruza acima da MA21
- **🔽 VENDA**: MA7 cruza abaixo da MA21
- **📊 Lateral**: Tendência sem cruzamento claro

#### Gráficos
- **Candlestick**: Preços OHLC com médias móveis
- **Volume**: Barras de volume
- **Visão geral**: Gráfico estilo Toro Trader

### Análise de Futebol

#### Algoritmo de Probabilidades
```python
score_casa = gols_casa * peso_casa + vitorias_confronto_casa
score_fora = gols_fora + vitorias_confronto_fora
probabilidade = score / total_score * 100
```

#### Fatores Considerados
- **Média de gols**: Últimos 5 jogos de cada time
- **Confronto direto**: Histórico entre os times
- **Fator casa**: Multiplicador para vantagem local (padrão: 1.1x)

#### Interface Visual
- **Cards coloridos**: Destaque para alta probabilidade
- **Gráficos de barras**: Visualização das probabilidades
- **Status em tempo real**: Agendado, Ao vivo, Finalizado

## 🛠 Desenvolvimento

### Hot Reload
O Streamlit está configurado com hot-reload automático:

```bash
# Modificar arquivos em apps/streamlit/ atualiza automaticamente
# Não é necessário rebuildar o container
```

### Estrutura de Desenvolvimento
```bash
# Desenvolvimento com logs
docker compose up -f docker-compose.yml

# Desenvolvimento apenas do frontend
docker compose up -d streamlit

# Acessar container para debug
docker compose exec streamlit bash
```

### Adicionando Novos Ativos
1. Edite `apps/streamlit/radar.py`
2. Adicione o símbolo na lista `assets`
3. Mapeie o símbolo em `get_real_data()` se necessário

### Adicionando Novos Indicadores
1. Modifique `get_signal()` em `radar.py`
2. Adicione cálculos na função
3. Atualize a lógica de sinais

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Container não inicia
```bash
# Verificar logs
docker compose logs streamlit

# Reconstruir container
docker compose build --no-cache streamlit
```

#### 2. API não retorna dados
```bash
# Verificar API key
echo $TWELVE_DATA_API_KEY

# Testar API manualmente
curl "https://api.twelvedata.com/time_series?symbol=AAPL&interval=1min&apikey=SUA_KEY"
```

#### 3. Porta já em uso
```bash
# Verificar portas em uso
netstat -tulpn | grep :8501

# Parar containers
docker compose down

# Alterar porta no docker-compose.yml
```

#### 4. Erro de permissão
```bash
# Dar permissões ao Docker
sudo usermod -aG docker $USER
# Reiniciar sessão
```

### Logs Úteis
```bash
# Logs do Streamlit
docker compose logs -f streamlit

# Logs da API
docker compose logs -f api

# Logs de todos os serviços
docker compose logs -f
```

### Reset Completo
```bash
# Parar e remover tudo
docker compose down -v

# Remover imagens
docker system prune -a

# Reconstruir do zero
docker compose build --no-cache
docker compose up -d
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a seção [Troubleshooting](#-troubleshooting)
2. Consulte os logs do Docker
3. Teste as APIs manualmente
4. Abra uma issue no repositório

## 📄 Licença

Este projeto é para fins educacionais e de demonstração. Use com responsabilidade ao fazer investimentos reais.

---

**Desenvolvido com ❤️ usando Python, Streamlit e Docker**