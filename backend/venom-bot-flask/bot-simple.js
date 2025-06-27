// ===================================================================================
// BOT DE TESTE SIMPLIFICADO - SEM INTERAÇÃO COM BROWSER
// ===================================================================================

const axios = require('axios');

// --- CONFIGURAÇÃO ---
const config = {
  flaskWebhookUrl: 'http://localhost:5001/webhook',
  testMode: true
};

// --- LOGGER ---
const logger = {
  info: (message) => console.log(`[${new Date().toISOString()}] [INFO]  - ${message}`),
  warn: (message) => console.warn(`[${new Date().toISOString()}] [WARN]  - ${message}`),
  error: (message, error) => console.error(`[${new Date().toISOString()}] [ERROR] - ${message}`, error || ''),
  debug: (message) => console.debug(`[${new Date().toISOString()}] [DEBUG] - ${message}`)
};

/**
 * Função de teste que simula mensagens do WhatsApp
 */
async function testWebhook() {
  try {
    logger.info("🧪 Iniciando testes do webhook...");
    
    const testMessages = [
      { from: '559285026981@c.us', body: 'Olá, gostaria de agendar uma consulta' },
      { from: '559285026981@c.us', body: 'Qual é o horário disponível?' },
      { from: '559285026981@c.us', body: 'Obrigado' }
    ];

    for (let i = 0; i < testMessages.length; i++) {
      const message = testMessages[i];
      logger.info(`📤 Enviando mensagem de teste ${i + 1}: "${message.body}"`);
      
      try {
        const response = await axios.post(
          config.flaskWebhookUrl,
          message,
          { timeout: 30000 }
        );

        logger.info(`✅ Resposta recebida: ${JSON.stringify(response.data)}`);
      } catch (error) {
        logger.error(`❌ Erro ao enviar mensagem ${i + 1}:`, error.message);
      }

      // Aguarda 2 segundos entre as mensagens
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    logger.info("✅ Testes concluídos!");
    
  } catch (error) {
    logger.error("❌ Erro nos testes:", error);
  }
}

/**
 * Função principal
 */
async function main() {
  try {
    logger.info("🤖 Iniciando Bot de Teste...");
    
    if (config.testMode) {
      await testWebhook();
    }
    
    // Mantém o processo rodando
    setInterval(() => {
      logger.info("💓 Bot de teste ativo...");
    }, 30000); // Log a cada 30 segundos

  } catch (err) {
    logger.error("❌ Erro fatal na inicialização:", err);
    process.exit(1);
  }
}

// Inicia a aplicação
main(); 