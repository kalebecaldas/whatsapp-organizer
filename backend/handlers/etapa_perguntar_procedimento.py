from core.intention_detector import detectar_mudanca_intencao, interpretar_resposta_com_gpt, processar_mudanca_intencao
from core.procedimentos_utils import sinonimos
import re
import unicodedata

def remover_acentos(texto):
    """Normaliza o texto removendo acentos para facilitar a comparação."""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def process(texto, dados, session_data):
    """
    Função principal que é chamada pelo message_handler.
    """
    return handle_perguntar_procedimento(texto, dados, session_data.get("from_number", ""))

def handle_perguntar_procedimento(texto, dados, telefone):
    """
    Handler para a etapa de perguntar procedimento.
    """
    print(f"🔁 Etapa atual: perguntar_procedimento | Texto: {texto}")
    
    # Normalizar texto
    texto_normalizado = texto.lower().strip()
    
    # Verificar se é uma mudança de intenção
    mudanca_detectada, nova_intencao = detectar_mudanca_intencao(texto_normalizado)
    if mudanca_detectada:
        print(f"🔄 Mudança de intenção detectada: {nova_intencao}")
        return processar_mudanca_intencao(nova_intencao, dados, "perguntar_procedimento")
    
    # Buscar dados do agendamento
    agendamento_dados = dados.get("agendamento", {})
    procedimentos_disponiveis = agendamento_dados.get("procedimentos", [])
    
    if not procedimentos_disponiveis:
        return "❌ Erro: Não encontrei os procedimentos. Vamos voltar ao início.", dados, "inicio"
    
    # Tentar extrair número do procedimento
    numero_match = re.search(r'(\d+)', texto_normalizado)
    if numero_match:
        numero = int(numero_match.group(1))
        if 1 <= numero <= len(procedimentos_disponiveis):
            procedimento_selecionado = procedimentos_disponiveis[numero - 1]
            agendamento_dados["procedimento_nome"] = procedimento_selecionado.get("nome")
            agendamento_dados["procedimento_id"] = procedimento_selecionado.get("id")
            dados["agendamento"] = agendamento_dados
            
            print(f"✅ Procedimento selecionado: {procedimento_selecionado.get('nome')}")
            print(f"🔍 ID do procedimento salvo: {procedimento_selecionado.get('id')}")
            print(f"📊 Dados do agendamento após seleção: {agendamento_dados}")
            return "📅 Perfeito! Para que dia você gostaria de agendar? (ex: 25/06 ou 25/06/2025)", dados, "perguntar_data"
    
    # Tentar encontrar procedimento por nome
    for procedimento in procedimentos_disponiveis:
        nome_procedimento = procedimento.get("nome", "").lower()
        if nome_procedimento in texto_normalizado or texto_normalizado in nome_procedimento:
            agendamento_dados["procedimento_nome"] = procedimento.get("nome")
            agendamento_dados["procedimento_id"] = procedimento.get("id")
            dados["agendamento"] = agendamento_dados
            
            print(f"✅ Procedimento selecionado por nome: {procedimento.get('nome')}")
            print(f"🔍 ID do procedimento salvo: {procedimento.get('id')}")
            print(f"📊 Dados do agendamento após seleção: {agendamento_dados}")
            return "📅 Perfeito! Para que dia você gostaria de agendar? (ex: 25/06 ou 25/06/2025)", dados, "perguntar_data"
    
    # Se chegou até aqui, a resposta não foi reconhecida
    # Usar GPT para interpretar a intenção
    print(f"🤖 Resposta não reconhecida, usando GPT para interpretar...")
    
    # Contexto adicional para o GPT
    lista_procedimentos = "\n".join(
        f"{i+1}. {proc.get('nome', 'Procedimento sem nome')}" 
        for i, proc in enumerate(procedimentos_disponiveis)
    )
    contexto_adicional = f"Procedimentos disponíveis:\n{lista_procedimentos}"
    
    acao, _ = interpretar_resposta_com_gpt(texto, "perguntar_procedimento", contexto_adicional)
    
    if acao == "continuar":
        # O GPT entendeu que o usuário está tentando responder corretamente
        # Vamos tentar uma abordagem mais flexível
        return "🤔 Não consegui identificar exatamente qual procedimento você quer. Pode digitar o número ou o nome do procedimento? Por exemplo: '1' para o primeiro da lista, ou 'Fisioterapia' se for esse o nome.", dados, "perguntar_procedimento"
    
    elif acao in ["agendar", "unidade", "procedimento", "data", "profissional", "cancelar", "ajuda"]:
        # O GPT detectou uma mudança de intenção
        print(f"🤖 GPT detectou mudança de intenção: {acao}")
        return processar_mudanca_intencao(acao, dados, "perguntar_procedimento")
    
    else:
        # Fallback para ajuda
        return "🔧 Entendi que você está com dificuldade! Vou te ajudar:\n\n*1.* Para voltar à escolha de unidade\n*2.* Para ver os procedimentos novamente\n*3.* Para cancelar e começar de novo\n*4.* Para falar com um atendente\n\nO que você prefere?", dados, "ajuda_procedimento"