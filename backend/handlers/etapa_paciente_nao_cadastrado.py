def process(texto, dados, session_data):
    texto = texto.strip()

    # Etapa inicial: perguntar se quer fazer pré-cadastro ou falar com atendente
    if "cadastro_status" not in dados:
        if texto == "1":
            dados["cadastro_status"] = "iniciando"
            return (
                "🧾 Perfeito! Para começarmos, por favor informe seu nome completo:",
                dados,
                "paciente_nao_cadastrado"
            )
        elif texto == "2":
            return (
                "📞 Ok! Encaminhei sua solicitação para um de nossos atendentes. Aguarde um momento.",
                dados,
                "encerrado"
            )
        else:
            return (
                "❓ Opção inválida. Por favor, digite:\n1️⃣ Para fazer o pré-cadastro online\n2️⃣ Para falar com um atendente agora",
                dados,
                "paciente_nao_cadastrado"
            )

    # Etapa seguinte: aguardando nome completo
    if dados.get("cadastro_status") == "iniciando" and "nome" not in dados:
        if len(texto.split()) < 2:
            return (
                "❗️Por favor, informe seu nome completo (nome e sobrenome).",
                dados,
                "paciente_nao_cadastrado"
            )
        dados["nome"] = texto
        dados["fluxo_manual"] = True  # Marcar que é fluxo sem cadastro
        return (
            f"✅ Nome salvo: {texto}\nAgora vamos seguir com o agendamento...",
            dados,
            "perguntar_procedimento"
        )
