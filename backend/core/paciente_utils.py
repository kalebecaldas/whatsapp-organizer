import re
import requests

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
                paciente_data = data.get("data", {})
                
                # Verifica se realmente há dados válidos do paciente
                if paciente_data and paciente_data.get("paciente_nome") and paciente_data.get("paciente_id"):
                    print(f"✅ Paciente encontrado: {paciente_data.get('paciente_nome')}")
                    return paciente_data
                else:
                    print("🔍 Paciente não encontrado (dados nulos ou inválidos)")
                    return None
            else:
                print("🔍 Paciente não encontrado (status não é success)")
        else:
            print(f"❌ Erro {response.status_code} na API Clínica Ágil: {response.text}")
    except Exception as e:
        print("❌ Exceção ao buscar paciente:", e)

    return None

def precarregar_agendamento_para_paciente(paciente, call_func):
    """
    Pré-carrega convênio, procedimentos e profissionais disponíveis para o paciente identificado.
    Armazena tudo em um dicionário para uso rápido no fluxo.
    call_func: função para chamadas à API (ex: clinicaagil_client.call)
    """
    agendamento = {}
    convenio_id = paciente.get("convenio_id")
    agendamento["convenio_id"] = convenio_id
    agendamento["procedimentos"] = []
    agendamento["profissionais_por_procedimento"] = {}

    if convenio_id:
        # Buscar procedimentos disponíveis
        procs_response = call_func("get_procedures_by_insurance", {"convenio_id": convenio_id})
        procedimentos = procs_response.get("data", []) if procs_response else []
        agendamento["procedimentos"] = procedimentos

        # Buscar profissionais para cada procedimento (pode ser otimizado para datas futuras)
        for proc in procedimentos:
            proc_id = proc.get("id")
            if not proc_id:
                continue
            # Aqui, por padrão, busca para o dia atual (pode ser ajustado para datas futuras)
            profissionais_response = call_func("get_available_professionals", {
                "clinica_id": paciente.get("clinica_id", 1),
                "dia": "",  # Data pode ser ajustada conforme necessário
                "procedimento_id": proc_id
            })
            profissionais = profissionais_response.get("data", []) if profissionais_response else []
            agendamento["profissionais_por_procedimento"][proc_id] = profissionais
    return agendamento
