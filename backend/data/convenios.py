# backend/data/convenios.py

CONVENIOS = {
    "BRADESCO": [
        "Acupuntura",
        "Consulta com Ortopedista",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Infiltração de ponto gatilho e Agulhamento a seco",
        "RPG"
    ],
    "SULAMERICA": [
        "Acupuntura",
        "Estimulação Elétrica Transcutânea",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica"
    ],
    "MEDISERVICE": [
        "Acupuntura",
        "Consulta com Ortopedista",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Infiltração de ponto gatilho e Agulhamento a seco",
        "RPG"
    ],
    "SAÚDE CAIXA": [
        "Acupuntura",
        "Consulta com Ortopedista",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Terapias por ondas de Choque"
    ],
    "PETROBRAS": [
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "RPG"
    ],
    "GEAP": [
        "Consulta com Ortopedista",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica"
    ],
    "PRO SOCIAL": [
        "Acupuntura",
        "Consulta Ortopédica",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Fisioterapia Respiratória",
        "Infiltração de ponto gatilho e Agulhamento a seco",
        "RPG"
    ],
    "POSTAL SAÚDE": [
        "Acupuntura",
        "Consulta com Ortopedista",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "RPG"
    ],
    "CONAB": [
        "Acupuntura",
        "Consulta com Ortopedista",
        "Estimulação elétrica transcutânea (TENS)",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Fisioterapia Respiratória",
        "Infiltração de ponto gatilho",
        "RPG"
    ],
    "AFFEAM": [
        "Acupuntura",
        "Consulta Ortopédica",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Fisioterapia Respiratória"
    ],
    "AMBEP": [
        "Acupuntura",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Fisioterapia Respiratória",
        "RPG"
    ],
    "GAMA": [
        "Acupuntura",
        "Consulta Ortopédica",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Respiratória"
    ],
    "LIFE": [
        "Acupuntura",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Fisioterapia Respiratória",
        "RPG"
    ],
    "NOTREDAME": [
        "Acupuntura",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "RPG"
    ],
    "OAB": [
        "Acupuntura",
        "Consulta Ortopédica",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Respiratória",
        "RPG"
    ],
    "CASEMBRAPA": [
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "RPG"
    ],
    "CULTURAL": [
        "Acupuntura",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Fisioterapia Respiratória",
        "RPG"
    ],
    "EVIDA": [
        "Acupuntura",
        "Consulta Ortopédica",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Respiratória",
        "RPG"
    ],
    "FOGAS": [
        "Acupuntura",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Respiratória",
        "RPG"
    ],
    "FUSEX": [
        "Acupuntura",
        "Consulta Ortopédica",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "Fisioterapia Pélvica",
        "Quiropraxia",
        "RPG"
    ],
    "PLAN-ASSITE": [
        "Acupuntura",
        "Consulta Ortopédica",
        "Fisioterapia Pélvica",
        "Fisioterapia Neurológica",
        "Fisioterapia Ortopédica",
        "RPG"
    ],
    # Convênios de desconto e sem procedimentos listados
    "ADEPOL": "DESCONTO",
    "BEM CARE": "DESCONTO",
    "BEMOL": "DESCONTO",
    "CLUBSAUDE": "DESCONTO",
    "PRO-SAUDE": "DESCONTO",
    "VITA": "DESCONTO",
    "CAPESAUDE": [],
}

PARTICULAR_VALORES = {
    "FISIOTERAPIA ORTOPEDICA": 90.00,
    "FISIOTERAPIA NEUROLOGICA": 100.00,
    "FISIOTERAPIA RESPIRATORIA": 100.00,
    "FISIOTERAPIA PELVICA": 220.00,
    "CONSULTA ORTOPEDISTA": 400.00,
    "AVALIAÇÃO ACUPUNTURA": 200.00,
    "ACUPUNTURA": 180.00,
    "AVALIAÇÃO FISIOTERAPIA PÉLVICA": 250.00,
    "RPG": 120.00,
    "PILATES 2x na Semana": 39.00,
    "PILATES 3x na Semana": 56.00,
    "PILATES SESSÃO AVULSA": 70.00,
    "QUIROPRAXIA": 120.00
}

PARTICULAR_REGRAS = """
Para procedimentos como fisioterapia pélvica e acupuntura, esses sempre terão que ter a avaliação primeiro, ou seja, se caso o paciente queira agendar somente uma sessão ele terá que pagar a avaliação. Mas se pagar o pacote de 10 sessões ele terá desconto na avaliação, ficando somente valor de sessão avulsa.
""" 