import json
from utils.gpt import ask_gpt

def detectar_mudanca_intencao(texto_normalizado):
    """
    Detecta se o usuário quer mudar de contexto/intenção.
    Retorna (True, nova_intencao) se detectar mudança, (False, None) caso contrário.
    """
    # Palavras-chave que indicam mudança de intenção
    mudancas_intencao = {
        "agendar": ["agendar", "agendamento", "marcar", "marcação", "consulta", "agenda", "novo"],
        "unidade": ["unidade", "clinica", "clínica", "sao jose", "vieiralves", "local", "endereço", "endereco", "outra clinica", "outra clínica"],
        "procedimento": ["procedimento", "tratamento", "terapia", "fisioterapia", "acupuntura", "tipo", "outro procedimento"],
        "data": ["data", "dia", "quando", "horário", "horario", "tempo", "outra data"],
        "profissional": ["profissional", "medico", "médico", "doutor", "dr", "fisioterapeuta", "terapeuta", "outro profissional"],
        "convenio": ["convenio", "convênio", "plano", "seguro", "cobertura", "particular"],
        "cancelar": ["cancelar", "desistir", "não quero", "nao quero", "parar", "sair", "encerrar", "não", "nao"],
        "ajuda": ["ajuda", "help", "socorro", "problema", "erro", "bug", "loop", "preso", "travei", "travei", "não entendo", "nao entendo"]
    }
    
    for intencao, palavras_chave in mudancas_intencao.items():
        if any(palavra in texto_normalizado for palavra in palavras_chave):
            return True, intencao
    
    return False, None

def interpretar_resposta_com_gpt(texto, etapa_atual, contexto_adicional=""):
    """
    Usa o ChatGPT para interpretar a resposta do usuário quando não é reconhecida.
    Retorna (acao, resposta) onde acao pode ser: 'continuar', 'voltar', 'ajuda', 'cancelar'
    """
    
    # Contexto específico para cada etapa
    contextos_etapa = {
        "perguntar_procedimento": "O usuário deve escolher um procedimento da lista numerada ou digitar o nome do procedimento. Se não entender, deve interpretar a intenção.",
        "perguntar_data": "O usuário deve informar uma data no formato DD/MM ou DD/MM/YYYY. Se não for uma data válida, deve interpretar a intenção.",
        "perguntar_profissional": "O usuário deve escolher um profissional da lista numerada ou digitar 0 para sem preferência. Se não entender, deve interpretar a intenção.",
        "perguntar_unidade": "O usuário deve escolher entre Vieiralves (1) ou São José (2). Se não entender, deve interpretar a intenção.",
        "escolher_horario": "O usuário deve escolher um horário da lista numerada. Se não entender, deve interpretar a intenção."
    }
    
    contexto = contextos_etapa.get(etapa_atual, "O usuário está em uma etapa de agendamento e deve fornecer uma resposta específica.")
    
    prompt = f"""
Você é um assistente virtual da clínica IAAM. O usuário está na etapa: {etapa_atual}.

{contexto}

Contexto adicional: {contexto_adicional}

O usuário disse: "{texto}"

Analise a resposta do usuário e determine a melhor ação:

1. Se o usuário está tentando agendar algo novo → retorne "agendar"
2. Se o usuário quer mudar de unidade/clínica → retorne "unidade"  
3. Se o usuário quer mudar de procedimento → retorne "procedimento"
4. Se o usuário quer mudar de data → retorne "data"
5. Se o usuário quer mudar de profissional → retorne "profissional"
6. Se o usuário quer cancelar → retorne "cancelar"
7. Se o usuário está confuso/pedindo ajuda → retorne "ajuda"
8. Se o usuário está tentando responder corretamente mas de forma diferente → retorne "continuar"

Responda APENAS com uma das opções acima, sem explicações adicionais.
"""

    try:
        response = ask_gpt(prompt)
        acao = response.strip().lower()
        
        # Mapeia a ação para o sistema
        if acao in ["agendar", "unidade", "procedimento", "data", "profissional", "cancelar", "ajuda"]:
            return acao, None
        elif acao == "continuar":
            return "continuar", None
        else:
            # Se o GPT não retornou uma ação válida, assume que precisa de ajuda
            return "ajuda", None
            
    except Exception as e:
        print(f"❌ Erro ao interpretar resposta com GPT: {e}")
        # Em caso de erro, assume que precisa de ajuda
        return "ajuda", None

def processar_mudanca_intencao(nova_intencao, dados, etapa_atual):
    """
    Processa a mudança de intenção detectada e retorna a resposta apropriada.
    """
    if nova_intencao == "cancelar":
        return "Ok, agendamento cancelado. Se mudar de ideia ou precisar de outra coisa, é só chamar! 😉", dados, "encerrado"
    
    elif nova_intencao == "ajuda":
        return "🔧 Entendi que você está com dificuldade! Vou te ajudar:\n\n*1.* Para voltar à escolha de unidade\n*2.* Para ver os procedimentos novamente\n*3.* Para cancelar e começar de novo\n*4.* Para falar com um atendente\n\nO que você prefere?", dados, "ajuda_procedimento"
    
    elif nova_intencao == "agendar":
        # Reinicia completamente o processo
        dados.clear()
        return "🔄 Ok! Vamos começar do zero. Diga 'agendar' para iniciar um novo agendamento.", dados, "inicio"
    
    elif nova_intencao == "unidade":
        # Limpa dados da unidade anterior e volta para escolher unidade
        agendamento_dados = dados.get("agendamento", {})
        agendamento_dados.pop("unidade", None)
        agendamento_dados.pop("clinica_ids", None)
        agendamento_dados.pop("procedimentos", None)
        agendamento_dados.pop("procedimento_nome", None)
        agendamento_dados.pop("procedimento_id", None)
        agendamento_dados.pop("data_selecionada", None)
        agendamento_dados.pop("profissionais_disponiveis", None)
        dados["agendamento"] = agendamento_dados
        return "🏥 Claro! Para qual unidade deseja agendar?\n\n*1.* Vieiralves\n*2.* São José", dados, "perguntar_unidade"
    
    elif nova_intencao == "procedimento":
        # Volta para perguntar_procedimento
        agendamento_dados = dados.get("agendamento", {})
        procedimentos_disponiveis = agendamento_dados.get("procedimentos", [])
        
        if not procedimentos_disponiveis:
            return "❌ Desculpe, ocorreu um erro. Por favor, tente iniciar novamente dizendo 'agendar'.", dados, "inicio"
        
        lista_procedimentos_texto = "\n".join(
            f"*{i+1}.* {proc.get('nome', 'Procedimento sem nome')}" 
            for i, proc in enumerate(procedimentos_disponiveis)
        )
        
        return f"📋 Claro! Aqui estão os procedimentos disponíveis novamente:\n\n{lista_procedimentos_texto}\n\nPor favor, digite o número do procedimento que deseja agendar.", dados, "perguntar_procedimento"
    
    elif nova_intencao == "data":
        # Volta para perguntar_data
        return "📅 Claro! Para que dia você gostaria de agendar? (ex: 25/06 ou 25/06/2025)", dados, "perguntar_data"
    
    elif nova_intencao == "profissional":
        # Volta para perguntar_profissional
        agendamento_dados = dados.get("agendamento", {})
        profissionais_disponiveis = agendamento_dados.get("profissionais_disponiveis", [])
        
        if not profissionais_disponiveis:
            return "❌ Não encontrei os profissionais. Vamos voltar à escolha de data.", dados, "perguntar_data"
        
        lista_profissionais_texto = "\n".join(
            f"*{i+1}.* {prof.get('nome', 'Profissional sem nome')}" 
            for i, prof in enumerate(profissionais_disponiveis)
        )
        
        return f"👨‍⚕️ Claro! Aqui estão os profissionais disponíveis novamente:\n\n{lista_profissionais_texto}\n\nVocê tem preferência por algum deles? Digite o número. Se não tiver preferência, digite *0*.", dados, "perguntar_profissional"
    
    elif nova_intencao == "convenio":
        return "🏥 Para verificar convênios, você pode:\n\n*1.* Ver todos os convênios aceitos\n*2.* Verificar se um convênio específico é aceito\n*3.* Voltar ao agendamento\n\nO que você prefere?", dados, "ajuda_procedimento"
    
    # Se não reconheceu a intenção, oferece ajuda genérica
    return "🔧 Entendi que você quer mudar algo! Vou te ajudar:\n\n*1.* Para voltar à escolha de unidade\n*2.* Para ver os procedimentos novamente\n*3.* Para cancelar e começar de novo\n*4.* Para falar com um atendente\n\nO que você prefere?", dados, "ajuda_procedimento" 