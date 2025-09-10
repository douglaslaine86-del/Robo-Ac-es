# Stock Analyzer Monorepo
Repositório com módulos: Radar de Ações, Backtester, Painel em Tempo Real e Analisador de Opções.

## Requisitos
- Docker & Docker Compose
- Python 3.10+

## Como rodar (local)
1. git clone <seu-repo>
2. cp .env.example .env e preencha chaves
3. make build
4. docker compose up -d
5. make seed
6. Acesse API em http://localhost:8000/docs e Streamlit em http://localhost:8501
