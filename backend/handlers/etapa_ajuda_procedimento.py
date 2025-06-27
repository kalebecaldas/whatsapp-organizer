from clinicaagil_client import call

def process(texto, dados, session_data):
    """
    Etapa de ajuda que permite ao usuário navegar entre diferentes opções
    quando está preso em alguma etapa do agendamento.
    """
    texto = texto.strip().lower()
    
    if texto in ["1", "unidade", "clinica", "clínica"]:
        # Volta para escolher unidade
        agendamento_dados = dados.get("agendamento", {})
        agendamento_dados.pop("unidade", None)
        agendamento_dados.pop("clinica_ids", None)
        agendamento_dados.pop("procedimentos", None)
        dados["agendamento"] = agendamento_dados
        return "🏥 Claro! Para qual unidade deseja agendar?\n\n*1.* Vieiralves\n*2.* São José", dados, "perguntar_unidade"
    
    elif texto in ["2", "procedimentos", "procedimento", "lista"]:
        # Mostra os procedimentos novamente
        agendamento_dados = dados.get("agendamento", {})
        procedimentos_disponiveis = agendamento_dados.get("procedimentos", [])
        
        if not procedimentos_disponiveis:
            return "❌ Não encontrei os procedimentos. Vamos voltar à escolha de unidade.", dados, "perguntar_unidade"
        
        lista_procedimentos_texto = "\n".join(
            f"*{i+1}.* {proc.get('nome', 'Procedimento sem nome')}" 
            for i, proc in enumerate(procedimentos_disponiveis)
        )
        
        return f"📋 Aqui estão os procedimentos disponíveis:\n\n{lista_procedimentos_texto}\n\nPor favor, digite o número do procedimento que deseja agendar.", dados, "perguntar_procedimento"
    
    elif texto in ["3", "cancelar", "desistir", "sair"]:
        # Cancela o agendamento
        return "Ok, agendamento cancelado. Se mudar de ideia ou precisar de outra coisa, é só chamar! 😉", dados, "encerrado"
    
    elif texto in ["4", "atendente", "humano", "pessoa"]:
        # Encaminha para atendente humano
        return "📞 Entendi! Encaminhei sua solicitação para um de nossos atendentes. Aguarde um momento, eles entrarão em contato em breve.", dados, "encerrado"
    
    elif texto in ["convenio", "convênio", "plano"]:
        # Mostra informações sobre convênios
        try:
            convenios_response = call("get_insurance_data", {})
            todos_convenios = convenios_response.get("data", [])
            
            if todos_convenios:
                lista_convenios = "\n".join(
                    f"• {conv.get('nome_convenio', 'Convênio sem nome')}"
                    for conv in todos_convenios[:10]  # Limita a 10 para não ficar muito longo
                )
                
                resposta = f"🏥 Aqui estão alguns dos convênios aceitos:\n\n{lista_convenios}"
                if len(todos_convenios) > 10:
                    resposta += f"\n\n... e mais {len(todos_convenios) - 10} convênios."
                
                resposta += "\n\nPara verificar um convênio específico, digite o nome dele."
                return resposta, dados, "ajuda_procedimento"
            else:
                return "❌ Não consegui carregar a lista de convênios no momento. Tente novamente mais tarde.", dados, "ajuda_procedimento"
                
        except Exception as e:
            print(f"❌ Erro ao buscar convênios: {e}")
            return "❌ Não consegui carregar a lista de convênios no momento. Tente novamente mais tarde.", dados, "ajuda_procedimento"
    
    else:
        # Se não entendeu, oferece as opções novamente
        return "❓ Não entendi sua escolha. Por favor, digite:\n\n*1.* Para voltar à escolha de unidade\n*2.* Para ver os procedimentos novamente\n*3.* Para cancelar e começar de novo\n*4.* Para falar com um atendente\n\nO que você prefere?", dados, "ajuda_procedimento" 