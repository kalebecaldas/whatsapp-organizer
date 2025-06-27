import unicodedata
from textwrap import dedent
from handlers.etapa_confirmar_dados import process as etapa_confirmar_dados

def remover_acentos(texto):
    """Normaliza o texto removendo acentos."""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def process(texto, dados, session_data):
    """
    Processa a escolha do turno e do horário. Se o usuário não escolheu um profissional,
    atribui automaticamente o profissional dono do horário selecionado.
    """
    agendamento_dados = dados.get("agendamento", {})
    texto_original = texto.strip()
    texto_normalizado = remover_acentos(texto_original.lower())

    # Recupera os horários que foram pré-filtrados e enriquecidos pela etapa anterior
    horarios_por_turno = agendamento_dados.get("horarios_filtrados_por_turno", {})
    turnos_disponiveis = sorted(horarios_por_turno.keys())
    
    # --- PARTE 1: Processar a escolha do TURNO ---
    if "turno_escolhido" not in agendamento_dados:
        turno_escolhido = None
        
        # Tenta identificar o turno pelo nome ou número
        if "manha" in texto_normalizado: turno_escolhido = "matutino"
        elif "tarde" in texto_normalizado: turno_escolhido = "vespertino"
        elif "noite" in texto_normalizado: turno_escolhido = "noturno"
        elif texto_original.isdigit():
            try:
                indice = int(texto_original) - 1
                if 0 <= indice < len(turnos_disponiveis):
                    turno_escolhido = turnos_disponiveis[indice]
            except (ValueError, IndexError):
                pass

        if turno_escolhido and turno_escolhido in horarios_por_turno:
            dados["agendamento"]["turno_escolhido"] = turno_escolhido
            texto_original = "" # Limpa para entrar na próxima fase de listagem de horários
        else:
            # Se não conseguiu identificar, pergunta novamente listando as opções numeradas
            lista_turnos_texto = "\n".join(f"*{i+1}.* {turno.capitalize()}" for i, turno in enumerate(turnos_disponiveis))
            resposta = f"Não entendi o turno. Por favor, escolha uma das opções abaixo:\n\n{lista_turnos_texto}"
            return resposta, dados, "escolher_horario"

    # --- PARTE 2: Processar a escolha do HORÁRIO ESPECÍFICO ---
    
    turno_selecionado = agendamento_dados.get("turno_escolhido")
    horarios_finais_disponiveis = sorted(horarios_por_turno.get(turno_selecionado, []), key=lambda x: x.get('inicio', ''))
    
    if texto_original.isdigit():
        try:
            indice = int(texto_original) - 1
            if 0 <= indice < len(horarios_finais_disponiveis):
                horario_selecionado = horarios_finais_disponiveis[indice]
                
                # Lógica de atribuição inteligente de profissional
                if agendamento_dados.get("profissional_id") is None:
                    id_do_profissional = horario_selecionado.get("profissional_id")
                    nome_do_profissional = horario_selecionado.get("profissional_nome")
                    
                    if id_do_profissional and nome_do_profissional:
                        agendamento_dados["profissional_id"] = id_do_profissional
                        agendamento_dados["profissional_nome"] = nome_do_profissional
                        print(f"✅ Profissional '{nome_do_profissional}' (ID: {id_do_profissional}) foi atribuído pelo horário.")
                
                # Salva a escolha do horário
                agendamento_dados["horario_inicio"] = horario_selecionado.get("inicio")
                agendamento_dados["horario_fim"] = horario_selecionado.get("fim")
                dados["agendamento"] = agendamento_dados
                
                # Chama diretamente a etapa de confirmação para uma transição fluida
                print("✅ Horário escolhido. Chamando a etapa de confirmação diretamente...")
                return etapa_confirmar_dados(texto, dados, session_data)
            else:
                return "❌ Opção inválida. Por favor, escolha um dos números da lista de horários.", dados, "escolher_horario"
        except (ValueError, IndexError):
            return "❌ Entrada inválida. Por favor, digite um número da lista.", dados, "escolher_horario"

    # Se ainda não temos um horário escolhido, lista as opções
    else:
        data_selecionada = agendamento_dados.get('data_selecionada', 'a data escolhida')
        lista_horarios_texto = "\n".join(
            f"*{i+1}.* {h.get('inicio')} às {h.get('fim')}"
            for i, h in enumerate(horarios_finais_disponiveis)
        )

        resposta = dedent(f"""\
            🕐 Horários disponíveis para *{turno_selecionado.capitalize()}* no dia *{data_selecionada}*:

            {lista_horarios_texto}

            Por favor, digite o número do horário que você deseja.
        """).strip()
        
        return resposta, dados, "escolher_horario"