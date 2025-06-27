// ===================================================================================
// BOT DE INTEGRAÇÃO WHATSAPP-FLASK - VERSÃO AVANÇADA COM DEBOUNCE
// ===================================================================================

const venom = require('venom-bot');
const axios = require('axios');
const express = require('express');
const cors = require('cors');

// --- CONFIGURAÇÃO ---
const config = {
  sessionName: 'iaam-teste',
  flaskWebhookUrl: 'http://localhost:5001/webhook',
  serverPort: 3000, // Porta para o servidor HTTP do bot
  
  // Tempo (em milissegundos) que o bot espera por novas mensagens antes de processar.
  // 3000ms (3 segundos) é um bom ponto de partida.
  debounceTimeout: 3000,
  
  // NÚMEROS DE TELEFONE PERMITIDOS PARA TESTES
  // Deixe como array vazio ([]) para permitir mensagens de TODOS os números.
  allowedTestNumbers: [
    '559285026981@c.us',
    '559293596706@c.us'
  ], // Altere para os seus números de teste
};

// --- LOGGER ---
const logger = {
  info: (message) => console.log(`[${new Date().toISOString()}] [INFO]  - ${message}`),
  warn: (message) => console.warn(`[${new Date().toISOString()}] [WARN]  - ${message}`),
  error: (message, error) => console.error(`[${new Date().toISOString()}] [ERROR] - ${message}`, error || ''),
  debug: (message) => console.debug(`[${new Date().toISOString()}] [DEBUG] - ${message}`)
};

// --- SERVIDOR HTTP ---
const app = express();
app.use(cors());
app.use(express.json());

// Variável global para armazenar o cliente Venom
let venomClient = null;

// Endpoint para receber mensagens do backend
app.post('/send-message', async (req, res) => {
  try {
    const { phone, message } = req.body;
    
    if (!phone || !message) {
      return res.status(400).json({ error: 'Phone and message are required' });
    }
    
    if (!venomClient) {
      return res.status(503).json({ error: 'Venom client not ready' });
    }
    
    logger.info(`📤 Enviando mensagem para ${phone}: ${message}`);
    
    // Envia a mensagem via Venom Bot
    await venomClient.sendText(phone, message);
    
    logger.info(`✅ Mensagem enviada com sucesso para ${phone}`);
    res.json({ success: true, message: 'Message sent successfully' });
    
  } catch (error) {
    logger.error('❌ Erro ao enviar mensagem:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// Endpoint de health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    venomReady: venomClient !== null,
    timestamp: new Date().toISOString()
  });
});

// Inicia o servidor HTTP
app.listen(config.serverPort, () => {
  logger.info(`🌐 Servidor HTTP iniciado na porta ${config.serverPort}`);
  logger.info(`📡 Endpoint de envio: http://localhost:${config.serverPort}/send-message`);
});

// --- LÓGICA DE BUFFER (DEBOUNCE) ---
const messageBuffer = {}; // Armazena as mensagens de cada usuário. Ex: { '55...': ['msg1', 'msg2'] }
const timeoutHandlers = {}; // Armazena os timers de cada usuário.

/**
 * Processa a mensagem acumulada e a envia para o webhook do Flask.
 */
async function processBufferedMessages(client, from) {
  if (!messageBuffer[from] || messageBuffer[from].length === 0) {
    return;
  }

  // Junta todas as mensagens do buffer em um único texto com quebras de linha.
  const fullMessage = messageBuffer[from].join('\n');
  
  // Limpa o buffer e o timer para este usuário ANTES de enviar.
  delete messageBuffer[from];
  if (timeoutHandlers[from]) {
    clearTimeout(timeoutHandlers[from]);
    delete timeoutHandlers[from];
  }

  try {
    logger.info(`📡 Enviando mensagem completa para webhook: { from: "${from}", body: "${fullMessage}" }`);
    
    const response = await axios.post(
      config.flaskWebhookUrl,
      { from, body: fullMessage },
      { timeout: 30000 } // Timeout de 30s para dar tempo à IA processar
    );

    logger.info(`✅ Resposta recebida do webhook: ${JSON.stringify(response.data)}`);

    const reply = response.data.result;
    if (reply) {
      await client.sendText(from, reply);
      logger.info(`📤 Resposta enviada para ${from}.`);
    } else {
      logger.warn("⚠️ Webhook respondeu, mas não retornou um 'result' para enviar.");
    }
  } catch (error) {
    logger.error("❌ Erro ao enviar para o webhook do Flask:", error.message);
    if (error.response) {
        logger.error(`📥 Status do erro: ${error.response.status}`);
        logger.error(`📄 Corpo da resposta de erro: ${JSON.stringify(error.response.data)}`);
    } else if (error.request) {
        logger.error("📭 Sem resposta do servidor Flask. Ele está rodando e acessível?");
    }
    await client.sendText(from, "❌ Desculpe, estou com um problema técnico no momento. Por favor, tente novamente em instantes.");
  }
}

/**
 * Função principal que lida com cada mensagem recebida.
 */
function handleIncomingMessage(client, message) {
  // Filtro de número de teste
  if (config.allowedTestNumbers.length > 0 && !config.allowedTestNumbers.includes(message.from)) {
    return logger.info(`🚫 Mensagem de [${message.from}] ignorada (não é um número de teste).`);
  }

  // Ignora mensagens de grupo, de status, ou sem corpo de texto
  if (message.isGroupMsg || !message.body || message.from.includes("status@broadcast")) {
    return;
  }

  const from = message.from;
  const body = message.body.trim();
  logger.info(`📩 Mensagem recebida de ${from}: "${body}"`);

  // Adiciona a nova mensagem ao buffer do usuário.
  if (!messageBuffer[from]) {
    messageBuffer[from] = [];
  }
  messageBuffer[from].push(body);

  // Se já existe um timer, cancela para reiniciar a contagem.
  if (timeoutHandlers[from]) {
    clearTimeout(timeoutHandlers[from]);
  }

  // Cria um novo timer. Se o usuário não enviar mais nada em X segundos, processa tudo.
  timeoutHandlers[from] = setTimeout(() => {
    processBufferedMessages(client, from);
  }, config.debounceTimeout);
}

/**
 * Lida com o encerramento seguro do processo.
 */
async function gracefulShutdown(client) {
  logger.warn("🛑 Recebido sinal de encerramento. Fechando conexões...");
  try {
    if (client) await client.close();
    logger.info("✅ Conexões fechadas. Encerrando.");
  } catch(e) {
    logger.error("❌ Erro durante o encerramento:", e);
  }
  process.exit(0);
}

/**
 * Função principal que inicializa o sistema.
 */
async function main() {
  try {
    logger.info("🤖 Iniciando sistema do Bot...");
    
    const client = await venom.create({
      session: config.sessionName,
      headless: false,
      browserArgs: ['--no-sandbox', '--disable-setuid-sandbox'],
      multidevice: true
    });

    logger.info("✅ Cliente Venom iniciado. Anexando handler de mensagens.");
    client.onMessage((message) => handleIncomingMessage(client, message));
    
    // Armazena o cliente na variável global para uso no servidor HTTP
    venomClient = client;
    
    process.on('SIGINT', () => gracefulShutdown(client));
    process.on('SIGTERM', () => gracefulShutdown(client));

  } catch (err) {
    logger.error("❌ Erro fatal na inicialização:", err);
    process.exit(1);
  }
}

// Inicia a aplicação
main();