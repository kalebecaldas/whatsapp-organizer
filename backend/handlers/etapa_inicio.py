import json
import unicodedata
from textwrap import dedent
from clinicaagil_client import call
from clients.openai_client import chat_with_functions
from handlers.etapa_perguntar_unidade import process as etapa_perguntar_unidade
from core.paciente_utils import buscar_paciente

def remover_acentos(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def process(texto, dados, session_data):
    if not dados.get("paciente"):
        paciente_encontrado = buscar_paciente(session_data.get("from_number"))
        if paciente_encontrado:
            dados["paciente"] = paciente_encontrado

    nome_paciente = dados.get("paciente", {}).get("paciente_nome")
    historico = session_data.get("historico", [])
    
    contexto_sistema = """Você é um assistente virtual da clínica IAAM. Sua função é entender a solicitação do usuário e chamar a função apropriada para respondê-lo.

FUNÇÕES DISPONÍVEIS:
1. iniciar_agendamento: Use quando o usuário quer agendar uma consulta
2. get_insurance_data: Use quando o usuário pergunta sobre convênios/planos de saúde
3. get_clinic_data: Use quando o usuário pergunta sobre localização, endereço, telefone das clínicas

EXEMPLOS DE USO:
- "Quero agendar" → iniciar_agendamento
- "Qual convênio vocês atendem?" → get_insurance_data
- "Onde fica a clínica?" → get_clinic_data
- "Localização da unidade Vieiralves" → get_clinic_data com unidade="Vieiralves"
- "Telefone da clínica" → get_clinic_data

IMPORTANTE: Sempre use as funções quando apropriado. Não responda diretamente sem chamar uma função."""
    
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
                # Lógica para informações das clínicas (endereço, telefone, etc.)
                try:
                    clinicas_response = call("get_clinic_data", {})
                    clinicas = clinicas_response.get("clinicas", [])
                    unidade_solicitada = remover_acentos(argumentos.get("unidade", "").lower())
                    
                    if unidade_solicitada:
                        # Busca clínica específica
                        clinica_encontrada = None
                        for clinica in clinicas:
                            nome_clinica = remover_acentos(clinica.get("nome", "").lower())
                            if unidade_solicitada in nome_clinica:
                                clinica_encontrada = clinica
                                break
                        
                        if clinica_encontrada:
                            nome = clinica_encontrada.get("nome", "Clínica")
                            endereco = clinica_encontrada.get("endereco", "Endereço não informado")
                            telefone = clinica_encontrada.get("telefone", "Telefone não informado")
                            
                            resposta_clinica = dedent(f"""\
                                📍 *{nome}*
                                
                                🏠 *Endereço:* {endereco}
                                📞 *Telefone:* {telefone}
                                
                                Precisa de mais alguma informação?
                            """).strip()
                            respostas_para_enviar.append(resposta_clinica)
                        else:
                            respostas_para_enviar.append(f"Não encontrei informações sobre a unidade '{argumentos.get('unidade')}'. Posso te ajudar com outras informações?")
                    else:
                        # Lista todas as clínicas
                        lista_clinicas = []
                        for clinica in clinicas:
                            nome = clinica.get("nome", "Clínica")
                            endereco = clinica.get("endereco", "Endereço não informado")
                            telefone = clinica.get("telefone", "Telefone não informado")
                            lista_clinicas.append(f"📍 *{nome}*\n🏠 {endereco}\n📞 {telefone}")
                        
                        resposta_todas = dedent(f"""\
                            🏥 *Nossas Unidades:*
                            
                            {chr(10).join(lista_clinicas)}
                            
                            Qual unidade você gostaria de saber mais sobre?
                        """).strip()
                        respostas_para_enviar.append(resposta_todas)
                        
                except Exception as e:
                    print(f"❌ Erro na lógica de clínicas: {e}")
                    respostas_para_enviar.append("Tive um problema ao consultar as informações das clínicas.")
        
        if proxima_etapa == "inicio" and respostas_para_enviar:
            respostas_para_enviar.append("\nPosso te ajudar com mais alguma coisa?")
        
        resposta = "\n\n".join(respostas_para_enviar)
        return resposta, dados, proxima_etapa

    elif content := getattr(resposta_ia, 'content', None):
        return content, dados, proxima_etapa

    else:
        primeiro_nome = nome_paciente.split()[0] if nome_paciente else "Olá"
        return f"{primeiro_nome}! 😊 Não entendi. Como posso ajudar?", dados, "inicio"
