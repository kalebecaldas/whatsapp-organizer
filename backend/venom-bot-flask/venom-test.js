const venom = require('venom-bot');

venom
  .create({
    session: 'iaam-teste',
    headless: false,
    browserArgs: ['--no-sandbox'],
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' // para M1/M2
  })
  .then((client) => {
    console.log("✅ Venom conectado. Esperando mensagens...");

    client.onMessage(async (message) => {
      console.log("📩 RECEBIDO:", message.body);

      if (!message.isGroupMsg && message.body) {
        await client.sendText(message.from, "🧠 Você disse: " + message.body);
        console.log("📤 Respondido para:", message.from);
      }
    });
  })
  .catch((error) => {
    console.error("❌ Erro ao iniciar Venom:", error);
  });
