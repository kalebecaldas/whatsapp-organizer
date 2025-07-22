import json
import unicodedata
from textwrap import dedent
from clinicaagil_client import call
from clients.openai_client import chat_with_functions
from handlers.etapa_perguntar_unidade import process as etapa_perguntar_unidade
from core.paciente_utils import buscar_paciente, precarregar_agendamento_para_paciente
from data.convenios import CONVENIOS, PARTICULAR_VALORES, PARTICULAR_REGRAS

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def process(texto, dados, session_data):
    if not dados.get("paciente"):
        paciente_encontrado = buscar_paciente(session_data.get("from_number"))
        if paciente_encontrado:
            dados["paciente"] = paciente_encontrado
            # Pré-carregar agendamento para paciente cadastrado
            dados["agendamento_precarregado"] = precarregar_agendamento_para_paciente(paciente_encontrado, call)
            
            # PACIENTE CADASTRADO - Repassar para atendimento humano
            return (
                "👋 Olá! Identificamos que você já é nosso paciente cadastrado.\n\n"
                "Para melhor atendê-lo, vou transferir você para nossa equipe de atendimento humano.\n\n"
                "⏰ **Tempo médio de resposta:** 2-5 minutos\n"
                "📱 **Canal:** WhatsApp\n\n"
                "Obrigado pela paciência! 😊",
                dados,
                "transferir_humano"
            )

    nome_paciente = dados.get("paciente", {}).get("paciente_nome")
    historico = session_data.get("historico", [])
    
    contexto_sistema = """
Você é um consultor de vendas da clínica IAAM, especializado em transformar contatos em agendamentos. Sua função é entender a necessidade do usuário e oferecer soluções personalizadas.

FUNÇÕES DISPONÍVEIS:
1. iniciar_agendamento: Use quando o usuário quer agendar uma consulta
2. get_insurance_data: Use quando o usuário pergunta sobre convênios/planos de saúde
3. get_clinic_data: Use quando o usuário pergunta sobre localização, endereço, telefone das clínicas
4. get_particular_values: Use quando o usuário pergunta sobre valores/preços particulares

EXEMPLOS DE USO:
- "Quero agendar" → iniciar_agendamento
- "Qual convênio vocês atendem?" → get_insurance_data
- "Onde fica a clínica?" → get_clinic_data
- "Localização da unidade Vieiralves" → get_clinic_data com unidade="Vieiralves"
- "Telefone da clínica" → get_clinic_data
- "Quanto custa fisioterapia?" → get_particular_values com procedimento="fisioterapia"
- "Qual o valor da acupuntura?" → get_particular_values com procedimento="acupuntura"
- "Preço particular" → get_particular_values
- "Quanto custa fisioterapia ortopédica?" → get_particular_values com procedimento="fisioterapia ortopédica"

IMPORTANTE: 
- Sempre use as funções quando apropriado. Não responda diretamente sem chamar uma função.
- Para perguntas sobre valores, seja específico sobre qual procedimento o usuário está perguntando.
- Se o usuário perguntar sobre "fisioterapia" de forma genérica, use get_particular_values com procedimento="fisioterapia" para mostrar todas as opções.
- SEMPRE termine suas respostas com uma pergunta ou call-to-action para manter a conversa fluindo.

PERFIL DE ATENDIMENTO:
Você é um consultor de vendas humanizado que:
- Foca em entender a DOR do paciente (física ou emocional)
- Apresenta BENEFÍCIOS antes de preços
- Oferece SOLUÇÕES personalizadas
- Faz PERGUNTAS para qualificar o lead
- Termina sempre com um CALL-TO-ACTION
- Usa linguagem acolhedora e empática
- Transforma objeções em oportunidades
- Conduz naturalmente para o agendamento

EXEMPLOS DE ABORDAGEM:
- "Entendo que você está com dor nas costas. A fisioterapia ortopédica pode te ajudar muito com isso..."
- "A acupuntura é excelente para o que você está sentindo. Quer que eu te explique como funciona?"
- "Posso te ajudar a agendar uma avaliação para entendermos melhor seu caso?"
"""
    
    if nome_paciente:
        contexto_sistema += f" Você já sabe que está falando com {nome_paciente.split()[0]}."

    messages = [{"role": "system", "content": contexto_sistema}] + historico
    resposta_ia = chat_with_functions(messages)
    proxima_etapa = "inicio"

    if tool_calls := getattr(resposta_ia, 'tool_calls', None):
        respostas_para_enviar = []
        for tool_call in tool_calls:
            function_data = tool_call.function
            nome_funcao = function_data.name
            argumentos = json.loads(function_data.arguments or "{}")

            if nome_funcao == "iniciar_agendamento":
                dados["agendamento"] = {}
                unidade_extraida = remover_acentos(argumentos.get("unidade", "").lower())
                if unidade_extraida:
                    return etapa_perguntar_unidade(unidade_extraida, dados, session_data)
                else:
                    proxima_etapa = "perguntar_unidade"
                    respostas_para_enviar.append(dedent("Ok, vamos iniciar seu agendamento!\n🏥 Para qual unidade deseja agendar?\n1. Vieiralves\n2. São José").strip())
                break
            
            elif nome_funcao == "get_insurance_data":
                # Lógica completa para convênios
                try:
                    convenios_response = call("get_insurance_data", {})
                    todos_convenios_api = convenios_response.get("data", [])
                    nome_convenio_usuario = remover_acentos(argumentos.get("nome_convenio", "").lower())
                    if nome_convenio_usuario:
                        convenio_encontrado = next((c for c in todos_convenios_api if nome_convenio_usuario in remover_acentos(c.get("nome_convenio", "").lower())), None)
                        if convenio_encontrado:
                            convenio_id = convenio_encontrado.get("convenio_id")
                            convenio_nome = convenio_encontrado.get("nome_convenio")
                            procs_response = call("get_procedures_by_insurance", {"convenio_id": convenio_id})
                            procedimentos = procs_response.get("data", []) if procs_response else []
                            lista_texto = "\n".join(f"• {p.get('nome')}" for p in procedimentos)
                            respostas_para_enviar.append(dedent(f"Sim, atendemos pelo convênio *{convenio_nome}*! ✅\n\nOs procedimentos cobertos são:\n{lista_texto}"))
                        else:
                            respostas_para_enviar.append("Não atendemos este convênio, mas você pode agendar como particular.")
                    else:
                        lista_texto = "\n".join(f"• {c.get('nome_convenio')}" for c in todos_convenios_api)
                        respostas_para_enviar.append(dedent(f"📋 Atendemos os seguintes convênios:\n{lista_texto}"))
                except Exception as e:
                    print(f"❌ Erro na lógica de convênios: {e}")
                    respostas_para_enviar.append("Tive um problema ao consultar as informações de convênios.")
            
            elif nome_funcao == "get_clinic_data":
                # Lógica para dados das clínicas
                try:
                    clinicas_response = call("get_clinic_data", {})
                    clinicas = clinicas_response.get("clinicas", [])
                    unidade_especifica = argumentos.get("unidade", "").lower()
                    
                    if unidade_especifica:
                        # Busca clínica específica
                        clinica_encontrada = None
                        for clinica in clinicas:
                            if unidade_especifica in clinica.get("nome", "").lower():
                                clinica_encontrada = clinica
                                break
                        
                        if clinica_encontrada:
                            respostas_para_enviar.append(dedent(f"""\
                                📍 **{clinica_encontrada['nome']}**
                                
                                📞 **Telefone:** {clinica_encontrada['telefone']}
                                🏠 **Endereço:** {clinica_encontrada['endereco']}
                            """).strip())
                        else:
                            respostas_para_enviar.append("Não encontrei essa unidade específica.")
                    else:
                        # Lista todas as clínicas
                        lista_clinicas = "\n\n".join([
                            f"📍 **{c['nome']}**\n📞 {c['telefone']}\n🏠 {c['endereco']}"
                            for c in clinicas
                        ])
                        respostas_para_enviar.append(dedent(f"""\
                            📍 **Nossas Unidades:**
                            
                            {lista_clinicas}
                        """).strip())
                except Exception as e:
                    print(f"❌ Erro na lógica de clínicas: {e}")
                    respostas_para_enviar.append("Tive um problema ao consultar as informações das clínicas.")
            
            elif nome_funcao == "get_particular_values":
                # Lógica para valores particulares com abordagem de vendas
                try:
                    procedimento_especifico = argumentos.get("procedimento", "").lower()
                    
                    # Detectar se é uma pergunta genérica sobre fisioterapia
                    if procedimento_especifico in ["fisioterapia", "fisio", "fisioterapia ortopédica", "fisioterapia neurológica", "fisioterapia respiratória", "fisioterapia pélvica"]:
                        # Se for genérico, mostrar opções com abordagem consultiva
                        fisioterapias = {
                            "FISIOTERAPIA ORTOPEDICA": 90.00,
                            "FISIOTERAPIA NEUROLOGICA": 100.00,
                            "FISIOTERAPIA RESPIRATORIA": 100.00,
                            "FISIOTERAPIA PELVICA": 220.00
                        }
                        
                        lista_fisioterapias = "\n".join([
                            f"• {proc.replace('_', ' ').title()}: R$ {valor:.2f}"
                            for proc, valor in fisioterapias.items()
                        ])
                        
                        respostas_para_enviar.append(dedent(f"""\
                            💪 **Fisioterapia - Recupere sua qualidade de vida!**
                            
                            Temos especialidades específicas para cada necessidade:
                            
                            {lista_fisioterapias}
                            
                            **Qual área você gostaria de tratar?** 
                            Posso te explicar como cada uma pode te ajudar especificamente.
                        """).strip())
                        
                    elif procedimento_especifico in ["acupuntura", "acup"]:
                        # Abordagem consultiva para acupuntura
                        respostas_para_enviar.append(dedent(f"""\
                            🌟 **Acupuntura - Equilíbrio natural para seu bem-estar!**
                            
                            A acupuntura é excelente para:
                            • Alívio de dores crônicas
                            • Redução de estresse e ansiedade
                            • Melhora na qualidade do sono
                            • Tratamento de enxaquecas
                            
                            **Investimento:**
                            💳 **Avaliação inicial:** R$ 200,00 (essencial para personalizar seu tratamento)
                            💵 **Sessões:** R$ 180,00 cada
                            
                            **Dica:** Na primeira consulta fazemos uma avaliação completa para entender suas necessidades específicas. Quer agendar sua avaliação?
                        """).strip())
                        
                    elif procedimento_especifico in ["fisioterapia pélvica", "fisioterapia pelvica", "pelvica"]:
                        # Abordagem consultiva para fisioterapia pélvica
                        respostas_para_enviar.append(dedent(f"""\
                            🌸 **Fisioterapia Pélvica - Cuidado especializado para sua saúde íntima!**
                            
                            Ideal para:
                            • Incontinência urinária
                            • Dores pélvicas
                            • Recuperação pós-parto
                            • Problemas de próstata
                            
                            **Investimento:**
                            💳 **Avaliação especializada:** R$ 250,00 (diagnóstico completo)
                            💵 **Sessões:** R$ 220,00 cada
                            
                            **Por que a avaliação é importante?** Ela nos permite criar um tratamento personalizado para seu caso específico.
                            
                            Quer agendar sua avaliação? Posso te ajudar a escolher um horário.
                        """).strip())
                        
                    elif procedimento_especifico in ["fisioterapia ortopédica", "fisioterapia ortopedica", "ortopédica", "ortopedica"]:
                        # Abordagem consultiva para fisioterapia ortopédica
                        respostas_para_enviar.append(dedent(f"""\
                            🦴 **Fisioterapia Ortopédica - Recupere sua mobilidade!**
                            
                            Perfeita para:
                            • Dores nas costas, joelhos, ombros
                            • Recuperação pós-cirúrgica
                            • Lesões esportivas
                            • Melhora da postura
                            
                            **Investimento:**
                            💳 **Parcelado:** 3x de R$ 30,00
                            💵 **À vista:** R$ 90,00
                            
                            **Diferencial:** Nossos fisioterapeutas são especializados e usam técnicas modernas para acelerar sua recuperação.
                            
                            Quer agendar sua primeira sessão? Posso te ajudar a escolher um horário que funcione para você.
                        """).strip())
                        
                    else:
                        # Busca valor específico com abordagem consultiva
                        valor_encontrado = None
                        for proc, valor in PARTICULAR_VALORES.items():
                            if procedimento_especifico in proc.lower():
                                valor_encontrado = (proc, valor)
                                break
                        
                        if valor_encontrado:
                            proc_nome, valor = valor_encontrado
                            respostas_para_enviar.append(dedent(f"""\
                                💰 **{proc_nome} - Investimento na sua saúde!**
                                
                                **Valores:**
                                💳 **Parcelado:** 3x de R$ {valor/3:.2f}
                                💵 **À vista:** R$ {valor:.2f}
                                
                                **Por que escolher a IAAM?**
                                • Profissionais especializados
                                • Equipamentos modernos
                                • Atendimento personalizado
                                
                                Quer agendar sua consulta? Posso te ajudar a escolher um horário.
                            """).strip())
                        else:
                            # Lista todos os valores com abordagem consultiva
                            lista_valores = "\n".join([
                                f"• {proc}: R$ {valor:.2f}"
                                for proc, valor in PARTICULAR_VALORES.items()
                            ])
                            respostas_para_enviar.append(dedent(f"""\
                                💰 **Nossos Procedimentos - Cuidado completo para você!**
                                
                                {lista_valores}
                                
                                **Qual procedimento você tem interesse?** 
                                Posso te explicar como cada um pode te ajudar especificamente e te ajudar a agendar.
                            """).strip())
                except Exception as e:
                    print(f"❌ Erro na lógica de valores: {e}")
                    respostas_para_enviar.append("Tive um problema ao consultar os valores particulares.")
        
        if proxima_etapa == "inicio" and respostas_para_enviar:
            respostas_para_enviar.append("\nPosso te ajudar com mais alguma coisa?")
        
        resposta = "\n\n".join(respostas_para_enviar)
        return resposta, dados, proxima_etapa

    elif content := getattr(resposta_ia, 'content', None):
        return content, dados, proxima_etapa

    else:
        primeiro_nome = nome_paciente.split()[0] if nome_paciente else "Olá"
        return f"{primeiro_nome}! 😊 Não entendi. Como posso ajudar?", dados, "inicio"
