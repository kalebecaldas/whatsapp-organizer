def process(texto, dados, session_data):
    texto = texto.strip().lower()

    opcoes = {
        "1": "Excelente",
        "2": "Bom",
        "3": "Regular",
        "4": "Ruim"
    }

    if texto in opcoes:
        dados["avaliacao"] = opcoes[texto]
        # Aqui você pode salvar no banco, enviar pra API etc.
        return "🙏 Obrigado pelo seu feedback! Ficamos felizes em poder ajudar. Até a próxima! 💙", dados, "encerrado"

    return (
        "📊 Como você avalia nosso atendimento de hoje?\n"
        "1. Excelente\n"
        "2. Bom\n"
        "3. Regular\n"
        "4. Ruim"
    ), dados, "feedback"
