const WebSocket = require('ws');
const axios = require('axios');
const express = require('express');
const bodyParser = require('body-parser');
const Redis = require('ioredis');

const axios = require('axios');

// --- Conexão Profit ---
const PROFIT_WS_URL = 'ws://localhost:8502/realtime';
function conectarProfit() {
    const ws = new WebSocket(PROFIT_WS_URL);
    ws.on('open', () => {
        console.log('Conectado ao Profit WebSocket local');
        ws.send(JSON.stringify({ action: 'subscribe', symbols: ['WINJ23','WDOJ23'] }));
    });
    ws.on('message', (data) => {
        try {
            const message = JSON.parse(data);
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

async function enviarCandle(candle) {
    try {
        await axios.post('http://localhost:8501/realtime-cache', candle);
        console.log(`Candle enviado: ${candle.symbol} ${candle.timestamp}`);
    } catch (err) {
        console.error('Erro ao enviar candle:', err.message);
    }
}

conectarProfit();
        console.log('Conectado ao Profit WebSocket');
