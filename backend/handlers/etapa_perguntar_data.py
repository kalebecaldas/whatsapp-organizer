# handlers/etapa_perguntar_data.py (VERSÃO COM FORMATAÇÃO APRIMORADA)

from core.intention_detector import detectar_mudanca_intencao, interpretar_resposta_com_gpt, processar_mudanca_intencao
import re
from datetime import datetime, timedelta

def process(texto, dados, session_data):
    """
    Esta etapa processa a escolha da data pelo usuário.
    """
    print(f"🔁 Etapa atual: perguntar_data | Texto: {texto}")
    
    # Normalizar texto
    texto_normalizado = texto.lower().strip()
    
    # Verificar se é uma mudança de intenção
    mudanca_detectada, nova_intencao = detectar_mudanca_intencao(texto_normalizado)
    if mudanca_detectada:
        print(f"🔄 Mudança de intenção detectada: {nova_intencao}")
        return processar_mudanca_intencao(nova_intencao, dados, "perguntar_data")
    
    # Buscar dados do agendamento
    agendamento_dados = dados.get("agendamento", {})
    procedimento_nome = agendamento_dados.get("procedimento_nome")
    
    if not procedimento_nome:
        return "❌ Erro: Não encontrei o procedimento selecionado. Vamos voltar ao início.", dados, "inicio"
    
    # Tentar extrair data do texto
    data_encontrada = extrair_data(texto_normalizado)
    
    if data_encontrada:
        agendamento_dados["data_selecionada"] = data_encontrada
        dados["agendamento"] = agendamento_dados
        
        print(f"✅ Data selecionada: {data_encontrada}")
        return "👨‍⚕️ Perfeito! Agora vou verificar os profissionais disponíveis para essa data...", dados, "perguntar_profissional"
    
    # Se chegou até aqui, a resposta não foi reconhecida
    # Usar GPT para interpretar a intenção
    print(f"🤖 Resposta não reconhecida, usando GPT para interpretar...")
    
    contexto_adicional = f"Procedimento selecionado: {procedimento_nome}"
    acao, _ = interpretar_resposta_com_gpt(texto, "perguntar_data", contexto_adicional)
    
    if acao == "continuar":
        # O GPT entendeu que o usuário está tentando responder corretamente
        return "🤔 Não consegui identificar a data. Pode digitar no formato DD/MM ou DD/MM/YYYY? Por exemplo: '25/06' ou '25/06/2025'.", dados, "perguntar_data"
    
    elif acao in ["agendar", "unidade", "procedimento", "data", "profissional", "cancelar", "ajuda"]:
        # O GPT detectou uma mudança de intenção
        print(f"🤖 GPT detectou mudança de intenção: {acao}")
        return processar_mudanca_intencao(acao, dados, "perguntar_data")
    
    else:
        # Fallback para ajuda
        return "🔧 Entendi que você está com dificuldade! Vou te ajudar:\n\n*1.* Para voltar à escolha de unidade\n*2.* Para ver os procedimentos novamente\n*3.* Para cancelar e começar de novo\n*4.* Para falar com um atendente\n\nO que você prefere?", dados, "ajuda_procedimento"

def extrair_data(texto):
    """
    Extrai uma data do texto usando regex.
    Suporta formatos: DD/MM, DD/MM/YYYY, DD-MM, DD-MM-YYYY
    """
    # Padrões de data
    padroes = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # DD/MM/YYYY
        r'(\d{1,2})/(\d{1,2})',          # DD/MM
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
        r'(\d{1,2})-(\d{1,2})',          # DD-MM
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            grupos = match.groups()
            dia = int(grupos[0])
            mes = int(grupos[1])
            
            # Se não tem ano, assume ano atual
            if len(grupos) == 3:
                ano = int(grupos[2])
            else:
                ano = datetime.now().year
            
            # Validar data
            try:
                data = datetime(ano, mes, dia)
                hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Verificar se a data é no futuro
                if data >= hoje:
                    return data.strftime("%d/%m/%Y")
                else:
                    return None
            except ValueError:
                continue
    
    return None