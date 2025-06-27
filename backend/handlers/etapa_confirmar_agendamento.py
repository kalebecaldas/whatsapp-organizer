from textwrap import dedent
from clinicaagil_client import call

def process(texto, dados, session_data):
    """
    Esta é a etapa final. Processa a confirmação ("Sim") do utilizador,
    monta o payload com os tipos de dados corretos e envia para a API para criar o agendamento.
    """
    texto = texto.strip().lower()

    # --- Caso 1: Utilizador confirma o agendamento ---
    if texto in ["sim", "1", "confirmar", "confirma", "ok", "isso"]:
        try:
            # 1. Recupera os dicionários principais da sessão
            agendamento_dados = dados.get("agendamento", {})
            paciente_dados = dados.get("paciente", {})

            # 2. Validação para garantir que os dados essenciais existem
            dados_essenciais = [
                agendamento_dados.get("clinica_ids"),
                paciente_dados.get("paciente_id"),
                paciente_dados.get("convenio_id"),
                agendamento_dados.get("procedimento_id"),
                agendamento_dados.get("data_selecionada"),
                agendamento_dados.get("horario_inicio")
            ]
            if not all(dados_essenciais):
                print(f"❌ Dados incompletos para agendamento. Sessão: {dados}")
                return "❌ Desculpe, alguns dados essenciais perderam-se. Por favor, reinicie o processo dizendo 'agendar'.", dados, "inicio"

            # 3. Monta o payload para a API com os tipos de dados corretos
            payload = {
                "clinica_id": int(agendamento_dados["clinica_ids"][0]),
                "paciente_id": int(paciente_dados["paciente_id"]),
                "paciente_nome": paciente_dados.get("paciente_nome"),
                "paciente_telefone": f"55{dados.get('telefone')}",
                "convenio_id": int(paciente_dados["convenio_id"]),
                "procedimento_id": int(agendamento_dados["procedimento_id"]),
                "data": agendamento_dados["data_selecionada"],
                # Enviando apenas o horário de início, que é mais comum em APIs
                "horario": agendamento_dados["horario_inicio"], 
            }

            # Adiciona o profissional_id ao payload apenas se ele tiver sido escolhido/atribuído
            if profissional_id := agendamento_dados.get("profissional_id"):
                payload["profissional_id"] = int(profissional_id)

            print("📨 Enviando payload final para a API de agendamento:", payload)
            resultado = call("register_appointment", payload)

            # 4. Processa a resposta da API
            status = resultado.get("status")
            if status == "success" or status is True:
                resposta = dedent("""\
                    ✅ Agendamento confirmado com sucesso! Você receberá uma mensagem de lembrete um dia antes.

                    Até breve! 😊

                    📊 Para nos ajudar a melhorar, como avalia este atendimento?
                    *1.* Excelente
                    *2.* Bom
                    *3.* Regular
                    *4.* Ruim
                """).strip()
                return resposta, dados, "feedback"
            else:
                erro_msg = resultado.get("message", "Não foi possível completar seu agendamento.")
                print(f"❌ Erro retornado pela API de agendamento: {resultado}")
                resposta = f"❌ Desculpe, algo deu errado: {erro_msg}. Por favor, tente novamente ou fale com um atendente."
                return resposta, dados, "encerrado"

        except (ValueError, TypeError) as e:
            print(f"❌ Erro de tipo de dado ao montar o payload: {e}")
            return "❌ Desculpe, ocorreu um erro com os dados da sua sessão. Por favor, reinicie o agendamento.", dados, "inicio"
        except Exception as e:
            print(f"❌ Erro técnico inesperado ao tentar agendar: {e}")
            return "❌ Ocorreu um erro técnico em nosso sistema. Nossa equipa já foi notificada.", dados, "encerrado"

    # --- Caso 2: Utilizador cancela o agendamento ---
    elif texto in ["não", "nao", "cancelar", "2"]:
        return "Ok, agendamento cancelado. Se mudar de ideia ou precisar de outra coisa, é só chamar! 😉", dados, "encerrado"

    # --- Caso 3: Resposta inválida ---
    else:
        return (
            "❓ Desculpe, não entendi. Por favor, digite *Sim* para confirmar ou *Não* para cancelar.",
            dados,
            "confirmar_agendamento" # Mantém na mesma etapa para nova tentativa
        )