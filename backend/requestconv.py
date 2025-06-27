import requests

API_KEY = "a5dcc76d202fdc2eb86646c9e57754b19f34fff30332b865b19cca44232b460b-c1a-5468970561"
API_METHOD = "Ch4tB0tMK4tsQ4v3QRc0d3"
URL = "https://apps.clinicaagil.com.br/api/integration/clinic_data"

headers = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY,
    "X-API-METHOD": API_METHOD
}

response = requests.post(URL, headers=headers, json={})
data = response.json()

# 👇 Depuração: imprime o JSON completo da resposta
print("Resposta completa da API:")
print(data)
print("\n---\n")

if data["status"] == "success":
    print("Convênios da clínica 1 (Unidade Vieiralves):\n")
    for item in data["data"]:
        if item.get("clinica_id") == "1":
            convenios = item.get("convenios", [])
            if not convenios:
                print("Nenhum convênio encontrado para esta clínica.")
            else:
                for conv in convenios:
                    print(f"- {conv['nome']} (ID: {conv['id']})")
else:
    print("Erro ao buscar dados:", data)
