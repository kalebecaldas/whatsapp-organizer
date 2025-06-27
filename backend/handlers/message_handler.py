import json
import time
import re
from session_store import get_session, set_session, acquire_lock, release_lock
from handlers.etapa_inicio import process as etapa_inicio
from handlers.etapa_perguntar_unidade import process as etapa_perguntar_unidade
from handlers.etapa_perguntar_procedimento import process as etapa_perguntar_procedimento
from handlers.etapa_perguntar_data import process as etapa_perguntar_data
from handlers.etapa_perguntar_profissional import process as etapa_perguntar_profissional
from handlers.etapa_escolher_horario import process as etapa_escolher_horario
from handlers.etapa_confirmar_dados import process as etapa_confirmar_dados
from handlers.etapa_confirmar_agendamento import process as etapa_confirmar_agendamento
from handlers.etapa_paciente_nao_cadastrado import process as etapa_paciente_nao_cadastrado
from handlers.etapa_feedback import process as etapa_feedback
from handlers.etapa_encerrado import process as etapa_encerrado
from handlers.etapa_padrao import process as etapa_padrao
from handlers.etapa_ajuda_procedimento import process as etapa_ajuda_procedimento
from core.intention_detector import detectar_mudanca_intencao, processar_mudanca_intencao

ETAPAS_MAPEAMENTO = {
    "inicio": etapa_inicio,
    "perguntar_unidade": etapa_perguntar_unidade,
    "perguntar_procedimento": etapa_perguntar_procedimento,
    "perguntar_data": etapa_perguntar_data,
    "perguntar_profissional": etapa_perguntar_profissional,
    "escolher_horario": etapa_escolher_horario,
    "confirmar_dados": etapa_confirmar_dados,
    "confirmar_agendamento": etapa_confirmar_agendamento,
    "paciente_nao_cadastrado": etapa_paciente_nao_cadastrado,
    "feedback": etapa_feedback,
    "encerrado": etapa_encerrado,
    "padrao": etapa_padrao,
    "ajuda_procedimento": etapa_ajuda_procedimento,
}

def normalizar_numero(telefone: str) -> str:
    telefone = re.sub(r'\D', '', telefone)
    if telefone.startswith("55"):
        telefone = telefone[2:]
    if len(telefone) > 9 and telefone[2] != '9':
         telefone = telefone[:2] + "9" + telefone[2:]
    return telefone

def analisar_intencao_resposta(texto: str, etapa_atual: str) -> tuple[str | None, dict]:
    """
    Analisa a intenção da resposta do usuário e determina se deve redirecionar para outra etapa.
    Retorna (nova_etapa, dados_limpos) ou (None, {}) se deve continuar na etapa atual.
    """
    texto_lower = texto.strip().lower()
    
    # Palavras-chave para diferentes intenções
    palavras_agendamento = ["agendar", "consulta", "marcar", "agendamento", "marcação", "quero agendar"]
    palavras_procedimento = [
        "procedimento", "tratamento", "outro procedimento", "trocar procedimento",
        "escolher outro procedimento", "quero escolher outro", "posso escolher outro",
        "mudar procedimento", "trocar tratamento", "outro tratamento"
    ]
    palavras_unidade = ["unidade", "clínica", "local", "onde", "vieiralves", "são josé", "sao jose"]
    palavras_data = ["data", "dia", "quando", "horário", "horario"]
    palavras_profissional = ["profissional", "médico", "medico", "doutor", "dr", "fisioterapeuta"]
    palavras_convênio = ["convênio", "convenio", "plano", "seguro", "cobertura"]
    palavras_endereco = ["endereço", "endereco", "onde fica", "localização", "localizacao", "a localização", "localização da clínica"]
    palavras_cancelar = ["cancelar", "desistir", "não quero", "nao quero", "parar"]
    palavras_ajuda = ["ajuda", "menu", "opções", "opcoes", "o que posso fazer"]
    
    # Detecção mais inteligente de intenções
    
    # 1. Se detectar intenção de agendamento, volta para início
    if any(palavra in texto_lower for palavra in palavras_agendamento):
        return "inicio", {}
    
    # 2. Se detectar perguntas sobre localização/endereço
    if any(palavra in texto_lower for palavra in palavras_endereco):
        # Se está perguntando sobre localização, volta para início para usar as funções
        return "inicio", {}
    
    # 3. Se detectar perguntas sobre convênios
    if any(palavra in texto_lower for palavra in palavras_convênio):
        return "inicio", {}
    
    # 4. Se detectar intenção de trocar procedimento
    if any(palavra in texto_lower for palavra in palavras_procedimento):
        if etapa_atual in ["perguntar_data", "perguntar_profissional", "escolher_horario"]:
            # Volta para perguntar_procedimento e limpa dados posteriores
            return "perguntar_procedimento", {"limpar_posteriores": True}
    
    # 5. Se detectar intenção de trocar unidade
    if any(palavra in texto_lower for palavra in palavras_unidade):
        if etapa_atual in ["perguntar_procedimento", "perguntar_data", "perguntar_profissional", "escolher_horario"]:
            return "perguntar_unidade", {"limpar_posteriores": True}
    
    # 6. Se detectar intenção de cancelar
    if any(palavra in texto_lower for palavra in palavras_cancelar):
        return "encerrado", {}
    
    # 7. Se detectar pedido de ajuda
    if any(palavra in texto_lower for palavra in palavras_ajuda):
        return "inicio", {}
    
    # 8. Detecção específica para perguntas sobre localização
    if "localização" in texto_lower or "onde fica" in texto_lower or "endereço" in texto_lower:
        return "inicio", {}
    
    # 9. Se detectar perguntas sobre horários de funcionamento
    if "horário" in texto_lower and ("funcionamento" in texto_lower or "atende" in texto_lower):
        return "inicio", {}
    
    # Se não detectar nenhuma intenção específica, continua na etapa atual
    return None, {}

def handle_message(from_number: str, text: str) -> str:
    from_number = normalizar_numero(from_number)
    
    if not acquire_lock(from_number):
        print(f"🔒 Mensagem de {from_number} ignorada, uma requisição anterior está em andamento.")
        return "" 

    try:
        session_data = get_session(from_number)
        session_data["from_number"] = from_number
        texto_processado = text.strip().lower()

        palavras_chave_reset = ["oi", "ola", "bom dia", "agendar", "menu", "inicio", "ajuda", "convenio", "endereço"]
        etapa_atual_salva = session_data.get("etapa")
        if any(keyword in texto_processado for keyword in palavras_chave_reset) or etapa_atual_salva in ["encerrado", "fim", None]:
            if etapa_atual_salva != "inicio" or "etapa" not in session_data:
                print("🔁 Detectado comando de início/reset. Redefinindo sessão.")
                dados_antigos = session_data.get("dados", {})
                session_data = {
                    "etapa": "inicio",
                    "dados": {"paciente": dados_antigos.get("paciente", {})},
                    "historico": [],
                    "from_number": from_number
                }

        historico = session_data.get("historico", [])
        historico.append({"role": "user", "content": text})
        session_data["historico"] = historico[-6:]

        etapa_atual = session_data.get("etapa", "inicio")
        dados_atuais = session_data.get("dados", {})
        print(f"🔁 Etapa atual: {etapa_atual} | Texto: {texto_processado}")

        # Analisa se a resposta indica uma intenção diferente
        nova_etapa, dados_limpos = analisar_intencao_resposta(text, etapa_atual)
        
        if nova_etapa and nova_etapa != etapa_atual:
            print(f"🔄 Redirecionando de '{etapa_atual}' para '{nova_etapa}' devido à intenção detectada")
            etapa_atual = nova_etapa
            session_data["etapa"] = nova_etapa
            
            # Se precisa limpar dados posteriores (ex: ao trocar procedimento)
            if dados_limpos.get("limpar_posteriores"):
                agendamento = dados_atuais.get("agendamento", {})
                if nova_etapa == "perguntar_procedimento":
                    # Remove dados do procedimento em diante
                    agendamento.pop("procedimento_nome", None)
                    agendamento.pop("procedimento_id", None)
                    agendamento.pop("data_selecionada", None)
                    agendamento.pop("profissionais_disponiveis", None)
                    agendamento.pop("profissional_id", None)
                    agendamento.pop("profissional_nome", None)
                    agendamento.pop("horario_inicio", None)
                    agendamento.pop("horario_fim", None)
                elif nova_etapa == "perguntar_unidade":
                    # Remove dados da unidade em diante
                    agendamento.pop("unidade", None)
                    agendamento.pop("clinica_ids", None)
                    agendamento.pop("procedimentos", None)
                    agendamento.pop("procedimento_nome", None)
                    agendamento.pop("procedimento_id", None)
                    agendamento.pop("data_selecionada", None)
                    agendamento.pop("profissionais_disponiveis", None)
                    agendamento.pop("profissional_id", None)
                    agendamento.pop("profissional_nome", None)
                    agendamento.pop("horario_inicio", None)
                    agendamento.pop("horario_fim", None)
                dados_atuais["agendamento"] = agendamento

        funcao_etapa = ETAPAS_MAPEAMENTO.get(etapa_atual, etapa_padrao)
        resposta, dados_atualizados, proxima_etapa = funcao_etapa(texto_processado, dados_atuais, session_data)

        session_data["dados"] = dados_atualizados
        session_data["etapa"] = proxima_etapa
        if resposta:
            session_data["historico"].append({"role": "assistant", "content": resposta})
            session_data["historico"] = session_data["historico"][-6:]
        
        set_session(from_number, session_data)
        return resposta

    finally:
        print(f"🔓 Liberando trava para {from_number}")
        release_lock(from_number)
