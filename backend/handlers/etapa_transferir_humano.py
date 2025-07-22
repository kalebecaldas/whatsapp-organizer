def process(texto, dados, session_data):
    """
    Etapa para transferir pacientes cadastrados para atendimento humano.
    Salva os dados da conversa e marca para atendimento humano.
    """
    # Marcar conversa para atendimento humano
    dados["transferido_humano"] = True
    dados["motivo_transferencia"] = "Paciente cadastrado identificado"
    dados["timestamp_transferencia"] = session_data.get("timestamp", "")
    
    # Salvar dados do paciente e intenção
    dados["dados_transferencia"] = {
        "paciente": dados.get("paciente", {}),
        "agendamento_precarregado": dados.get("agendamento_precarregado", {}),
        "historico_conversa": session_data.get("historico", []),
        "intencao_detectada": dados.get("intencao_detectada", ""),
        "from_number": session_data.get("from_number", "")
    }
    
    return (
        "✅ Transferência realizada com sucesso!\n\n"
        "Nossa equipe entrará em contato em breve para finalizar seu agendamento.\n\n"
        "Obrigado por escolher a IAAM! 😊",
        dados,
        "encerrado"
    ) 