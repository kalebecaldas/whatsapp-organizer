# handlers/etapa_perguntar_profissional.py (VERSÃO FINAL REFINADA)

from textwrap import dedent
from core.intention_detector import detectar_mudanca_intencao, interpretar_resposta_com_gpt, processar_mudanca_intencao
from clinicaagil_client import call
import re

def process(texto, dados, session_data):
    """
    Esta etapa processa a escolha do profissional pelo usuário.
    """
    print(f"🔁 Etapa atual: perguntar_profissional | Texto: {texto}")
    print(f"📊 Dados da sessão: {dados}")
    
    # Normalizar texto
    texto_normalizado = texto.lower().strip()
    
    # Verificar se é uma mudança de intenção
    mudanca_detectada, nova_intencao = detectar_mudanca_intencao(texto_normalizado)
    if mudanca_detectada:
        print(f"🔄 Mudança de intenção detectada: {nova_intencao}")
        return processar_mudanca_intencao(nova_intencao, dados, "perguntar_profissional")
    
    # Buscar dados do agendamento
    agendamento_dados = dados.get("agendamento", {})
    profissionais_disponiveis = agendamento_dados.get("profissionais_disponiveis", [])
    
    print(f"🔍 Profissionais já carregados: {len(profissionais_disponiveis)}")
    print(f"🔍 Profissionais apresentados: {agendamento_dados.get('profissionais_apresentados', False)}")
    
    # Se não tem profissionais, buscar da API
    if not profissionais_disponiveis:
        print(f"🔍 Buscando profissionais disponíveis da API...")
        print(f"📊 Dados do agendamento: {agendamento_dados}")
        print(f"🏥 Clinica ID: {agendamento_dados.get('clinica_id', '1')}")
        print(f"📅 Data selecionada: {agendamento_dados.get('data_selecionada', '')}")
        print(f"🔍 Procedimento ID: {agendamento_dados.get('procedimento_id', '')}")
        
        try:
            # Buscar profissionais disponíveis
            profissionais_response = call("get_available_professionals", {
                "clinica_id": agendamento_dados.get("clinica_id", "1"),
                "dia": agendamento_dados.get("data_selecionada", ""),
                "procedimento_id": agendamento_dados.get("procedimento_id", "")
            })
            
            print(f"📡 Resposta da API get_available_professionals: {profissionais_response}")
            
            profissionais_disponiveis = profissionais_response.get("data", [])
            agendamento_dados["profissionais_disponiveis"] = profissionais_disponiveis
            dados["agendamento"] = agendamento_dados
            
            print(f"✅ Profissionais encontrados: {len(profissionais_disponiveis)}")
            
            if not profissionais_disponiveis:
                print(f"⚠️ Nenhum profissional encontrado, voltando para perguntar_data")
                return "⚠️ Não encontrei profissionais disponíveis para essa data. Você pode:\n\n*1.* Escolher outra data\n*2.* Escolher outro procedimento\n*3.* Escolher outra unidade\n\nO que você prefere fazer?", dados, "perguntar_data"
                
        except Exception as e:
            print(f"❌ Erro ao buscar profissionais: {e}")
            return "⚠️ Erro ao buscar profissionais disponíveis. Tente novamente mais tarde.", dados, "perguntar_data"
    
    # Se é a primeira vez que está mostrando os profissionais, apresentar a lista
    if not agendamento_dados.get("profissionais_apresentados"):
        print(f"📋 Apresentando lista de profissionais pela primeira vez")
        agendamento_dados["profissionais_apresentados"] = True
        dados["agendamento"] = agendamento_dados
        
        lista_profissionais_texto = "\n".join(
            f"*{i+1}.* {prof.get('nome', 'Profissional sem nome')}" 
            for i, prof in enumerate(profissionais_disponiveis)
        )
        
        resposta = f"👨‍⚕️ Perfeito! Aqui estão os profissionais disponíveis para {agendamento_dados.get('data_selecionada', 'essa data')}:\n\n{lista_profissionais_texto}\n\nVocê tem preferência por algum deles? Digite o número. Se não tiver preferência, digite *0*."
        print(f"📤 Retornando lista de profissionais")
        return resposta, dados, "perguntar_profissional"
    
    # Tentar extrair número do profissional
    numero_match = re.search(r'(\d+)', texto_normalizado)
    if numero_match:
        numero = int(numero_match.group(1))
        print(f"🔢 Número extraído: {numero}")
        
        if numero == 0:
            # Sem preferência
            agendamento_dados["profissional_nome"] = "Sem preferência"
            agendamento_dados["profissional_id"] = None
            dados["agendamento"] = agendamento_dados
            
            print(f"✅ Sem preferência de profissional - indo para confirmar_agendamento")
            return "📋 Perfeito! Agora vou confirmar os dados do seu agendamento...", dados, "confirmar_agendamento"
        
        elif 1 <= numero <= len(profissionais_disponiveis):
            profissional_selecionado = profissionais_disponiveis[numero - 1]
            agendamento_dados["profissional_nome"] = profissional_selecionado.get("nome")
            agendamento_dados["profissional_id"] = profissional_selecionado.get("id")
            dados["agendamento"] = agendamento_dados
            
            print(f"✅ Profissional selecionado: {profissional_selecionado.get('nome')} - indo para confirmar_agendamento")
            return "📋 Perfeito! Agora vou confirmar os dados do seu agendamento...", dados, "confirmar_agendamento"
    
    # Tentar encontrar profissional por nome
    for profissional in profissionais_disponiveis:
        nome_profissional = profissional.get("nome", "").lower()
        if nome_profissional in texto_normalizado or texto_normalizado in nome_profissional:
            agendamento_dados["profissional_nome"] = profissional.get("nome")
            agendamento_dados["profissional_id"] = profissional.get("id")
            dados["agendamento"] = agendamento_dados
            
            print(f"✅ Profissional selecionado por nome: {profissional.get('nome')} - indo para confirmar_agendamento")
            return "📋 Perfeito! Agora vou confirmar os dados do seu agendamento...", dados, "confirmar_agendamento"
    
    # Se chegou até aqui, a resposta não foi reconhecida
    print(f"🤖 Resposta não reconhecida: '{texto_normalizado}'")
    
    # Usar GPT para interpretar a intenção
    print(f"🤖 Usando GPT para interpretar...")
    
    # Contexto adicional para o GPT
    lista_profissionais = "\n".join(
        f"{i+1}. {prof.get('nome', 'Profissional sem nome')}" 
        for i, prof in enumerate(profissionais_disponiveis)
    )
    contexto_adicional = f"Profissionais disponíveis:\n{lista_profissionais}\n\nDigite 0 para sem preferência."
    
    acao, _ = interpretar_resposta_com_gpt(texto, "perguntar_profissional", contexto_adicional)
    
    if acao == "continuar":
        # O GPT entendeu que o usuário está tentando responder corretamente
        print(f"🤖 GPT entendeu como continuação")
        return "🤔 Não consegui identificar qual profissional você quer. Pode digitar o número ou o nome? Por exemplo: '1' para o primeiro da lista, ou '0' para sem preferência.", dados, "perguntar_profissional"
    
    elif acao in ["agendar", "unidade", "procedimento", "data", "profissional", "cancelar", "ajuda"]:
        # O GPT detectou uma mudança de intenção
        print(f"🤖 GPT detectou mudança de intenção: {acao}")
        return processar_mudanca_intencao(acao, dados, "perguntar_profissional")
    
    else:
        # Fallback para ajuda
        print(f"🤖 Fallback para ajuda")
        return "🔧 Entendi que você está com dificuldade! Vou te ajudar:\n\n*1.* Para voltar à escolha de unidade\n*2.* Para ver os procedimentos novamente\n*3.* Para cancelar e começar de novo\n*4.* Para falar com um atendente\n\nO que você prefere?", dados, "ajuda_procedimento"

    # 4. Constrói a próxima pergunta (lista de turnos)
    
    # Filtra os horários disponíveis com base na escolha do profissional
    # Se nenhum profissional foi escolhido (opção 0), considera horários de todos os profissionais apresentados.
    lista_profissionais_para_filtrar = [profissional_selecionado] if profissional_selecionado else profissionais_disponiveis
    
    horarios_por_turno = {}
    for prof in lista_profissionais_para_filtrar:
        # A API retorna 'horarios_matutino', 'horarios_vespertino', etc.
        if prof.get("horarios_matutino"):
            horarios_por_turno.setdefault("matutino", []).extend(prof["horarios_matutino"])
        if prof.get("horarios_vespertino"):
            horarios_por_turno.setdefault("vespertino", []).extend(prof["horarios_vespertino"])
        if prof.get("horarios_noturno"):
            horarios_por_turno.setdefault("noturno", []).extend(prof["horarios_noturno"])
            
    # Salva os horários filtrados na sessão para a próxima etapa usar
    agendamento_dados["horarios_filtrados_por_turno"] = horarios_por_turno
    
    turnos_com_horarios = sorted(horarios_por_turno.keys())

    if not turnos_com_horarios:
         return "⚠️ Infelizmente, não encontrei horários disponíveis para sua seleção. Você pode:\n\n*1.* Escolher outra data\n*2.* Escolher outro procedimento\n*3.* Escolher outra unidade\n\nO que você prefere fazer?", dados, "perguntar_data"

    # Monta a lista de turnos numerada
    lista_turnos_texto = "\n".join(
        f"*{i+1}.* {turno.capitalize()}" 
        for i, turno in enumerate(turnos_com_horarios)
    )

    # Monta a resposta final
    resposta_final = dedent(f"""\
        {resposta_confirmacao}⏰ Agora, em qual turno você prefere o atendimento?

        {lista_turnos_texto}

        Digite o número ou o nome do turno.
    """).strip()
    
    # Atualiza o dicionário de dados principal e avança a etapa
    dados["agendamento"] = agendamento_dados
    return resposta_final, dados, "escolher_horario"