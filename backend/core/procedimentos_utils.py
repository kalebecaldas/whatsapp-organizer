from clinicaagil_client import call

SAUDACOES = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]

sinonimos = {
    "fisioterapia": ["fisioterapia", "fisio"],
    "acupuntura": ["acupuntura", "acup"]
}

def listar_procedimentos(convenio_id):
    procs = call("get_procedures_by_insurance", {"convenio_id": convenio_id})
    nomes = [p["nome"] for p in procs.get("data", [])]
    return nomes[:5]
