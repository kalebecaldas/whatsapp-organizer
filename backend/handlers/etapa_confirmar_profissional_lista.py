import unicodedata
from .etapa_escolher_horario import process as escolher_horario_process
from rapidfuzz import process as fuzzy_process, fuzz

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def process(texto, dados, session_data):
    texto_original = texto.strip()
    texto_normalizado = remover_acentos(texto_original.lower())
    lista = dados.get("profissionais_disponiveis", [])

    # Limpa dados antigos
    dados.pop("turno_escolhido", None)
    dados.pop("horarios_disponiveis", None)
    dados.pop("horario_escolhido", None)

    # Caso esteja aguardando confirmação de sugestão
    if dados.get("sugestao_profissional"):
        if texto_normalizado in ["sim", "s", "isso"]:
            dados["profissional_nome"] = dados.pop("sugestao_profissional")
            print(f"✅ Profissional confirmado por sugestão: {dados['profissional_nome']}")
            return escolher_horario_process("", dados, session_data)
        elif texto_normalizado in ["nao", "não", "n"]:
            dados.pop("sugestao_profissional", None)
            return "Tudo bem. Você pode digitar outro nome ou responder *Lista* para ver as opções disponíveis.", dados, "confirmar_profissional_lista"

    # Solicita exibição da lista
    if texto_normalizado in ["nao", "não", "lista"]:
        print("📋 Usuário solicitou a lista de profissionais.")
        if not lista:
            return "⚠️ Nenhum profissional disponível para esse dia. Tente outra data.", dados, "perguntar_data"
        
        msg = "👥 Veja abaixo os profissionais disponíveis:\n"
        for i, nome in enumerate(lista):
            msg += f"{i + 1}. {nome}\n"
        msg += "\nDigite o número do profissional desejado ou *Próximo* para continuar sem escolher."
        return msg, dados, "confirmar_profissional_lista"

    # 1. Número
    if texto_normalizado.isdigit():
        indice = int(texto_normalizado) - 1
        if 0 <= indice < len(lista):
            dados["profissional_nome"] = lista[indice]
            print(f"✅ Profissional selecionado: {dados['profissional_nome']}")
            return escolher_horario_process("", dados, session_data)
        else:
            return "❌ Número inválido. Escolha da lista ou digite *Próximo*.", dados, "confirmar_profissional_lista"

    # 2. Palavra
    elif texto_normalizado != "proximo":
        nomes_normalizados = [remover_acentos(nome.lower()) for nome in lista]

        # Exato
        if texto_normalizado in nomes_normalizados:
            dados["profissional_nome"] = lista[nomes_normalizados.index(texto_normalizado)]
            print(f"✅ Profissional selecionado (exato): {dados['profissional_nome']}")
            return escolher_horario_process("", dados, session_data)

        # Fuzzy
        match = fuzzy_process.extractOne(
            texto_normalizado, nomes_normalizados, scorer=fuzz.WRatio
        )

        if match:
            melhor_nome_normalizado, score, idx = match
            profissional_correspondente = lista[idx]
            print(f"🤖 Fuzzy match ➜ '{profissional_correspondente}' (score: {score})")

            if score >= 65:
                dados["profissional_nome"] = profissional_correspondente
                return escolher_horario_process("", dados, session_data)

            elif score >= 50:
                dados["sugestao_profissional"] = profissional_correspondente
                return (
                    f"🤔 Você quis dizer *{profissional_correspondente}*? Responda com *Sim* ou *Não*.",
                    dados,
                    "confirmar_profissional_lista"
                )

        return (
            "❌ Nome não encontrado. Digite novamente ou envie *Lista* para ver os profissionais disponíveis.",
            dados,
            "confirmar_profissional_lista"
        )

    # 3. Próximo
    print("⏩ Usuário pulou a escolha do profissional.")
    return escolher_horario_process("", dados, session_data)
