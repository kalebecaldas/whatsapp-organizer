import json
import re
import time
import requests
from clients.openai_client import chat_with_functions
from session_store import get_session, set_session
from clinicaagil_client import call

SAUDACOES = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]

def buscar_paciente(telefone: str):
    try:
        telefone_limpo = re.sub(r'\D', '', telefone)

        if telefone_limpo.startswith("55"):
            telefone_limpo = telefone_limpo[2:]

        if len(telefone_limpo) == 10 and telefone_limpo.startswith("92"):
            telefone_limpo = telefone_limpo[:2] + "9" + telefone_limpo[2:]

        if len(telefone_limpo) != 11:
            print(f"⚠️ Número inesperado: {telefone_limpo}")
            return None

        url = "https://apps.clinicaagil.com.br/api/integration/patient_data"
        payload = {"numero_paciente": telefone_limpo}
        headers = {
            "accept": "application/json",
            "X-API-KEY": "a5dcc76d202fdc2eb86646c9e57754b19f34fff30332b865b19cca44232b460b-c1a-5468970561",
            "X-API-METHOD": "Ch4tB0tW4tsS4v3QRc0d3",
            "content-type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"✅ Paciente encontrado: {data['data'].get('paciente_nome')}")
                return data.get("data")
            else:
                print("🔍 Paciente não encontrado.")
        else:
            print(f"❌ Erro {response.status_code} na API Clínica Ágil: {response.text}")
    except Exception as e:
        print("❌ Exceção ao buscar paciente:", e)

    return None

def listar_procedimentos(convenio_id):
    procs = call("get_procedures_by_insurance", {"convenio_id": convenio_id})
    nomes = [p["nome"] for p in procs.get("data", [])]
    return nomes[:5]

def handle_message(from_number: str, text: str) -> str:
    session_data = get_session(from_number)
    try:
        session_data = json.loads(session_data) if isinstance(session_data, str) else session_data
    except:
        session_data = {}

    if not isinstance(session_data, dict) or "etapa" not in session_data:
        session_data = {
            "etapa": "inicio",
            "dados": {},
            "ultima_resposta_ts": 0
        }

    agora = time.time()
    if agora - session_data.get("ultima_resposta_ts", 0) < 1.5:
        return ""

    etapa = session_data["etapa"]
    dados = session_data["dados"]
    resposta = ""
    texto = text.strip()

    if etapa == "inicio":
        paciente = buscar_paciente(from_number)
        if paciente:
            dados["paciente"] = paciente
            convenio_id = paciente.get("convenio_id")
            dados["convenio_id"] = convenio_id

            convenio_nome = "não identificado"
            try:
                convenios = call("get_insurance_data", {})
                for conv in convenios.get("data", []):
                    if conv["convenio_id"] == convenio_id:
                        convenio_nome = conv.get("nome_convenio", "não identificado")
                        break
            except Exception as e:
                print(f"❌ Erro ao buscar nome do convênio: {e}")

            lista = listar_procedimentos(convenio_id)
            dados["procedimentos_disponiveis"] = lista
            lista_texto = "\n".join(f"- {proc}" for proc in lista)

            resposta = (
                f"📋 Olá {paciente['paciente_nome']}! Que bom falar com você 😊\n"
                f"Identificamos seu convênio: *{convenio_nome}*.\n"
                f"Estes são os procedimentos disponíveis:\n{lista_texto}\n\n"
                f"Por favor, digite qual deseja agendar."
            )
            session_data["etapa"] = "perguntar_procedimento"
        else:
            resposta = "🔍 Não encontrei seu cadastro. Por favor, informe seu nome completo para começarmos."
            session_data["etapa"] = "informar_nome"

    elif etapa in ["informar_nome", "informar_nome_convenio"]:
        dados["nome"] = texto
        resposta = "✅ Obrigado! Agora me diga qual procedimento você deseja? (Fisioterapia / Acupuntura)"
        session_data["etapa"] = "perguntar_procedimento"

    elif etapa == "perguntar_procedimento":
        if texto.lower() in SAUDACOES or "agendar" in texto.lower():
            resposta = (
                "✍️ Por favor, digite apenas o nome do procedimento que deseja agendar, "
                "como por exemplo: *Fisioterapia* ou *Acupuntura*."
            )
            session_data["etapa"] = "perguntar_procedimento"
        else:
            dados["procedimento"] = texto

            if "convenio_id" not in dados:
                resposta = "⚠️ Não encontrei seu convênio. Vamos reiniciar. Por favor, digite *agendar*."
                session_data = {
                    "etapa": "inicio",
                    "dados": {},
                    "ultima_resposta_ts": time.time()
                }
            else:
                procs = call("get_procedures_by_insurance", {"convenio_id": dados["convenio_id"]})

                sinonimos = {
                    "fisioterapia": ["fisioterapia", "fisio"],
                    "acupuntura": ["acupuntura", "acup"]
                }

                texto_normalizado = texto.lower()
                palavra_base = next(
                    (chave for chave, lista in sinonimos.items() if any(s in texto_normalizado for s in lista)),
                    texto_normalizado
                )

                procedimentos_disponiveis = procs.get("data", [])
                print("📋 Procedimentos retornados pela API:")
                for p in procedimentos_disponiveis:
                    print("-", p.get("nome", ""))

                encontrados = [
                    p for p in procedimentos_disponiveis
                    if palavra_base in p.get("nome", "").lower()
                ]

                if encontrados:
                    procedimento = encontrados[0]
                    dados["procedimento_id"] = procedimento["procedimento_id"]
                    resposta = (
                        f"✅ Procedimento selecionado: {procedimento['nome']}\n"
                        f"Você já tem um profissional em mente? (Sim / Não)"
                    )
                    session_data["etapa"] = "perguntar_profissional"
                else:
                    resposta = "❌ Procedimento não encontrado para o convênio informado. Tente novamente."

    elif etapa == "perguntar_profissional":
        if texto.lower() == "sim":
            resposta = "Informe o nome do profissional desejado."
            session_data["etapa"] = "informar_nome_profissional"
        else:
            profissionais = call("get_available_professionals", {
                "clinica_id": "1",
                "dia": "",
                "procedimento_id": dados["procedimento_id"]
            })
            nomes = [p["profissional"] for p in profissionais.get("data", [])]
            dados["profissionais_disponiveis"] = nomes
            if nomes:
                resposta = "Aqui estão alguns profissionais disponíveis:\n" + "\n".join(f"- {n}" for n in nomes[:5])
                resposta += "\nVocê deseja algum deles? Se sim, digite o nome. Se não, apenas diga 'Próximo'."
                session_data["etapa"] = "confirmar_profissional_lista"
            else:
                resposta = "⚠️ Nenhum profissional encontrado agora. Deseja tentar mais tarde?"

    elif etapa == "informar_nome_profissional":
        dados["profissional_nome"] = texto
        profs = call("get_available_professionals", {
            "clinica_id": "1",
            "dia": "",
            "procedimento_id": dados["procedimento_id"]
        })
        profissional = next((p for p in profs.get("data", []) if texto.lower() in p["profissional"].lower()), None)
        if profissional:
            dados["profissional_id"] = profissional["profissional_id"]
            datas = call("get_available_dates", {"profissional_id": profissional["profissional_id"]})
            opcoes = [item["data_formatada"] for item in datas.get("data", [])]
            if opcoes:
                resposta = "Essas são as datas disponíveis:\n" + "\n".join(f"{i+1}. {d}" for i, d in enumerate(opcoes[:5]))
                resposta += "\n\nDigite o número da data que preferir."
                dados["datas_opcoes"] = opcoes
                session_data["etapa"] = "escolher_data"
            else:
                resposta = "⚠️ Não encontrei datas disponíveis no momento. Tente novamente mais tarde."
                session_data["etapa"] = "fim"
        else:
            resposta = "❌ Não consegui identificar o profissional. Por favor, tente novamente."
            session_data["etapa"] = "fim"

    elif etapa == "confirmar_profissional_lista":
        if texto.lower() != "próximo":
            dados["profissional_nome"] = texto
        resposta = "Qual data prefere para seu atendimento? (Ex: 03/06)"
        session_data["etapa"] = "informar_nome_profissional"

    elif etapa == "escolher_data":
        try:
            idx = int(texto) - 1
            opcoes = dados.get("datas_opcoes", [])
            if 0 <= idx < len(opcoes):
                dados["data_preferida"] = opcoes[idx]
                resposta = "Perfeito! Agora me diga seu telefone para finalizar 😄"
                session_data["etapa"] = "confirmar_dados"
            else:
                resposta = "Número inválido. Escolha uma das opções da lista."
        except:
            resposta = "Por favor, digite apenas o número da data escolhida 😉"

    elif etapa == "confirmar_dados":
        dados["telefone"] = texto

        convenio_nome = dados.get("convenio_id")
        try:
            convenios = call("get_insurance_data", {})
            for conv in convenios.get("data", []):
                if conv["convenio_id"] == dados.get("convenio_id"):
                    convenio_nome = conv.get("nome_convenio", "não identificado")
                    break
        except Exception as e:
            print(f"❌ Erro ao exibir nome do convênio no resumo: {e}")

        resumo = (
            f"🗓️ Agendamento:\n"
            f"- Nome: {dados.get('paciente', {}).get('paciente_nome', dados.get('nome', ''))}\n"
            f"- Procedimento: {dados.get('procedimento')}\n"
            f"- Convênio: {convenio_nome}\n"
            f"- Profissional: {dados.get('profissional_nome', 'Qualquer')}\n"
            f"- Data: {dados.get('data_preferida')}\n"
            f"- Telefone: {dados.get('telefone')}\n\n"
            f"Deseja confirmar? (Sim / Não)"
        )
        resposta = resumo
        session_data["etapa"] = "confirmar_agendamento"

    elif etapa == "confirmar_agendamento":
        if texto.lower() in ["sim", "confirmar"]:
            resultado = call("register_appointment", dados)
            if resultado.get("status") == "success":
                resposta = "✅ Agendamento confirmado com sucesso! Até breve. 🦡"
            else:
                resposta = "❌ Algo deu errado ao registrar. Por favor, tente novamente mais tarde."
            session_data["etapa"] = "fim"
        else:
            resposta = "Agendamento cancelado. Se quiser começar de novo, digite *agendar*."
            session_data["etapa"] = "fim"

    else:
        print(f"⚠️ Etapa desconhecida: {etapa}")
        resposta = (
            "⚠️ Ocorreu um erro no atendimento automático.\n"
            "Vamos começar de novo. Por favor, digite *agendar* para reiniciar."
        )
        session_data = {
            "etapa": "inicio",
            "dados": {},
            "ultima_resposta_ts": time.time()
        }

    session_data["dados"] = dados
    session_data["ultima_resposta_ts"] = time.time()
    set_session(from_number, session_data)

    return resposta
