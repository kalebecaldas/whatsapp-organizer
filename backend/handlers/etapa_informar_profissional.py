import unicodedata
from clinicaagil_client import call
from rapidfuzz import process as fuzzy_process, fuzz

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def process(texto, dados, session_data):
    texto_original = texto.strip()
    texto_normalizado = remover_acentos(texto_original.lower())
    dados["profissional_nome"] = texto_original  # guarda o original para histórico

    dia = dados.get("dia") or dados.get("data_preferida", "")

    try:
        profs = call("get_available_professionals", {
            "clinica_id": "1",
            "dia": dia,
            "procedimento_id": dados.get("procedimento_id")
        })
    except Exception as e:
        print(f"❌ Erro ao buscar profissionais: {e}")
        return (
            "⚠️ Erro ao buscar profissionais disponíveis. Quer ver uma lista dos disponíveis? Responda com *Não*.",
            dados,
            "perguntar_profissional"
        )

    lista_profs = profs.get("data", [])
    nomes_originais = [p["nome"] for p in lista_profs]
    nomes_normalizados = [remover_acentos(nome.lower()) for nome in nomes_originais]

    # Match com IA (RapidFuzz)
    melhor, score, idx = fuzzy_process.extractOne(
        texto_normalizado, nomes_normalizados, scorer=fuzz.WRatio
    ) if nomes_normalizados else (None, 0, None)

    if score >= 75:
        profissional = lista_profs[idx]
        dados["profissional_id"] = profissional["id"]
        dados["profissional_nome"] = profissional["nome"]

        try:
            datas = call("get_available_dates", {"profissional_id": profissional["id"]})
            opcoes = [item["data_formatada"] for item in datas.get("data", [])]
        except Exception as e:
            print(f"❌ Erro ao buscar datas disponíveis: {e}")
            return "⚠️ Erro ao buscar datas disponíveis. Tente novamente mais tarde.", dados, "fim"

        if opcoes:
            resposta = "📅 Essas são as datas disponíveis:\n" + "\n".join(
                f"{i+1}. {d}" for i, d in enumerate(opcoes[:5])
            )
            resposta += "\n\nDigite o número da data que preferir."
            dados["datas_opcoes"] = opcoes
            return resposta, dados, "escolher_data"
        else:
            return "⚠️ Não encontrei datas disponíveis no momento. Deseja tentar outro profissional?", dados, "perguntar_profissional"

    else:
        return (
            "❌ Não consegui identificar o profissional com esse nome.\n"
            "Deseja tentar novamente ou ver uma lista dos disponíveis? Responda com *Não*.",
            dados,
            "perguntar_profissional"
        )
