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
                print(f"✅ Paciente encontrado: {data['data'].get('paciente_nome')}")
                return data.get("data")
            else:
                print("🔍 Paciente não encontrado.")
        else:
            print(f"❌ Erro {response.status_code} na API Clínica Ágil: {response.text}")
    except Exception as e:
        print("❌ Exceção ao buscar paciente:", e)

    return None
