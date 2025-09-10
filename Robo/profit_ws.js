const WebSocket = require('ws');
const axios = require('axios');

// URL do WebSocket do Profit (substitua pela oficial)
const PROFIT_WS_URL = 'ws://localhost:8502/realtime';

// Conecta ao WebSocket do Profit
function conectarProfit() {
    const ws = new WebSocket(PROFIT_WS_URL);

    ws.on('open', () => {
        console.log('Conectado ao Profit WebSocket');
        // Se necessário, enviar mensagem de subscribe para os símbolos desejados
        ws.send(JSON.stringify({ action: 'subscribe', symbols: ['WINJ23','WDOJ23'] }));
    });

    ws.on('message', (data) => {
        try {
            const message = JSON.parse(data);
            // Supondo que message.candle contenha os campos corretos
            if (message.candle) {
                const { symbol, timestamp, open, high, low, close, volume } = message.candle;
                enviarCandle({ symbol, timestamp, open, high, low, close, volume });
            }
        } catch (err) {
            console.error('Erro processando mensagem:', err.message);
        }
    });

    ws.on('close', () => {
        console.log('WebSocket desconectado. Tentando reconectar em 3s...');
        setTimeout(conectarProfit, 3000);
    });

    ws.on('error', (err) => {
        console.error('Erro WebSocket:', err.message);
        ws.close();
    });
}

// Função para enviar candle para o cache via API
async function enviarCandle(candle) {
    try {
        await axios.post('http://localhost:3000/realtime-cache', candle);
        console.log(`Candle enviado: ${candle.symbol} ${candle.timestamp}`);
    } catch (err) {
        console.error('Erro ao enviar candle:', err.message);
    }
}

// Inicia a conexão
conectarProfit();
