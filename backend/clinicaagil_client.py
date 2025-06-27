import requests
import logging

# Configura o logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BASE_URL = "https://apps.clinicaagil.com.br/api/integration"
API_KEY = "a5dcc76d202fdc2eb86646c9e57754b19f34fff30332b865b19cca44232b460b-c1a-5468970561"

METHODS = {
    "get_clinic_data": "Ch4tB0tMK4tsQ4v3QRc0d3",
    "get_insurance_data": "Ch4tB0tP4tsQ4v3Q32c0d3",
    "get_procedures_by_insurance": "Ch4tB0tW4tsPpr0cs",
    "get_available_dates": "Ch4tB0tW4tsd4ttt@s",
    "get_available_professionals": "Ch4tB0tW4tspPr0of33",
    "register_appointment": "Ch4tB0tW4tsa4g3nDD",
    "get_patient_data": "Ch4tB0tW4tsS4v3QRc0d3"  # ✅ Adicionado
}

def call(function_name: str, args: dict) -> dict:
    try:
        logging.info(f"🔍 Executando: {function_name} | Args: {args}")

        if function_name == "get_clinic_data":
            return {
                "clinicas": [
                    {
                        "clinica_id": "1",
                        "nome": "Unidade Vieiralves",
                        "telefone": "(92) 3584-2864",
                        "endereco": "Rua Rio Içá, 850 - Nossa Senhora das Graças, Manaus - AM"
                    },
                    {
                        "clinica_id": "2",
                        "nome": "Unidade São José",
                        "telefone": "(92) 3249-7412",
                        "endereco": "São José Operário, Manaus - AM"
                    },
                    {
                        "clinica_id": "3",
                        "nome": "Unidade Vieiralves (ANEXO)",
                        "telefone": "(92) 3584-2864",
                        "endereco": "Nossa Senhora das Graças, Manaus - AM"
                    }
                ]
            }

        def erro_response(res):
            logging.error(f"❌ Erro HTTP {res.status_code} em {function_name}")
            logging.error(f"📄 Resposta: {res.text}")
            return {
                "erro": f"Erro na API ({res.status_code})",
                "detalhes": res.text,
                "funcao": function_name
            }

        headers_common = {
            "accept": "application/json",
            "X-API-KEY": API_KEY,
            "X-API-METHOD": METHODS.get(function_name),
        }

        if function_name == "get_insurance_data":
            headers = headers_common | {"content-type": "application/json"}
            res = requests.post(f"{BASE_URL}/insurance_data", headers=headers)
            return res.json() if res.ok else erro_response(res)

        if function_name == "get_procedures_by_insurance":
            headers = headers_common | {"content-type": "application/x-www-form-urlencoded"}
            payload = {"convenio_id": args.get("convenio_id")}
            res = requests.post(f"{BASE_URL}/procedures_by_insurance", data=payload, headers=headers)
            return res.json() if res.ok else erro_response(res)

        if function_name == "get_available_dates":
            headers = headers_common | {"content-type": "application/x-www-form-urlencoded"}
            payload = {"avancar_semanas": args.get("avancar_semanas", 1)}
            res = requests.post(f"{BASE_URL}/available_dates", data=payload, headers=headers)
            return res.json() if res.ok else erro_response(res)

        if function_name == "get_available_professionals":
            headers = headers_common | {"content-type": "application/x-www-form-urlencoded"}
            payload = {
                "clinica_id": args.get("clinica_id"),
                "dia": args.get("dia"),
                "procedimento_id": args.get("procedimento_id")
            }
            res = requests.post(f"{BASE_URL}/available_professionals", data=payload, headers=headers)
            return res.json() if res.ok else erro_response(res)

        if function_name == "register_appointment":
            headers = headers_common | {"content-type": "application/x-www-form-urlencoded"}
            res = requests.post(f"{BASE_URL}/register_appointment", data=args, headers=headers)
            return res.json() if res.ok else erro_response(res)

        if function_name == "get_patient_data":  # ✅ Novo bloco
            headers = headers_common | {"content-type": "application/x-www-form-urlencoded"}
            payload = {"numero_paciente": int(args.get("numero_paciente"))}
            res = requests.post(f"{BASE_URL}/patient_data", data=payload, headers=headers)
            return res.json() if res.ok else erro_response(res)

        logging.warning(f"⚠️ Função desconhecida chamada: {function_name}")
        return {"erro": "Função não reconhecida", "funcao": function_name}

    except Exception as e:
        logging.exception(f"💥 Erro inesperado em {function_name}: {e}")
        return {"erro": str(e), "funcao": function_name}
