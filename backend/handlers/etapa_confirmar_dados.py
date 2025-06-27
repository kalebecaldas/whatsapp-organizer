from textwrap import dedent
from clinicaagil_client import call 

def process(texto, dados, session_data):
    """
    Esta etapa não processa o input do usuário. Ela apenas coleta todos os dados
    da sessão, monta um resumo completo e pede a confirmação final.
    """
    # 1. Recupera os dicionários principais da sessão para facilitar o acesso
    agendamento_dados = dados.get("agendamento", {})
    paciente_dados = dados.get("paciente", {})
    
    # 2. Coleta todas as informações necessárias com valores padrão para segurança
    nome_paciente = paciente_dados.get("paciente_nome", "Não informado")
    telefone = dados.get("telefone", "Não informado")
    
    # Informações do agendamento
    unidade = agendamento_dados.get("unidade", "Não informada")
    procedimento = agendamento_dados.get("procedimento_nome", "Não informado")
    profissional = agendamento_dados.get("profissional_nome", "Qualquer profissional")
    data = agendamento_dados.get("data_selecionada", "Não informada")
    
    # Formata o horário
    horario_inicio = agendamento_dados.get("horario_inicio", "--:--")
    horario_fim = agendamento_dados.get("horario_fim", "--:--")
    faixa_horario = f"{horario_inicio} às {horario_fim}"
    
    # --- Lógica Aprimorada para Buscar o Nome do Convênio ---
    convenio_nome = "Particular" # Assume-se Particular como padrão
    try:
        convenio_id = paciente_dados.get("convenio_id")
        if convenio_id:
            convenios_response = call("get_insurance_data", {})
            todos_convenios = convenios_response.get("data", [])
            # Encontra o nome do convênio correspondente ao ID do paciente
            convenio_encontrado = next((c for c in todos_convenios if str(c.get("convenio_id")) == str(convenio_id)), None)
            if convenio_encontrado:
                convenio_nome = convenio_encontrado.get("nome_convenio", convenio_nome)
    except Exception as e:
        print(f"❌ Erro ao buscar nome do convênio para o resumo: {e}")
        convenio_nome = "A confirmar"
    # --------------------------------------------------------
    
    # 3. Monta a mensagem de resumo final para o usuário
    resumo = dedent(f"""\
        ✅ Tudo pronto! Vamos apenas revisar os dados para confirmar o agendamento.

        🗓️ *Resumo do Agendamento:*
        ---------------------------------
        👤 *Nome:* {nome_paciente}
        📋 *Procedimento:* {procedimento}
        👨‍⚕️ *Profissional:* {profissional}
        📍 *Unidade:* {unidade}
        📅 *Data:* {data}
        🕐 *Horário:* {faixa_horario}
        🏥 *Convênio:* {convenio_nome}
        📞 *Telefone:* {telefone}
        ---------------------------------

        As informações estão corretas?
        Digite *Sim* para confirmar o agendamento.
    """).strip()

    # 4. Define a próxima etapa como 'confirmar_agendamento', que irá processar o "Sim" ou "Não"
    return resumo, dados, "confirmar_agendamento"