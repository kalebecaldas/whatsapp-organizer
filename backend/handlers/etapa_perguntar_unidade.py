import re
import unicodedata
from textwrap import dedent
from clinicaagil_client import call
from core.paciente_utils import buscar_paciente

def remover_acentos(texto):
    """Normaliza o texto removendo acentos para facilitar a comparação."""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def limpar_numero(numero):
    """Remove todos os caracteres não numéricos de uma string."""
    return re.sub(r'\D', '', str(numero))

def process(texto, dados, session_data):
    """
    Processa a escolha da unidade, busca o paciente no sistema
    e pré-carrega os procedimentos disponíveis.
    """
    texto_original = texto.strip()
    texto_normalizado = remover_acentos(texto_original.lower())

    # Garante que a estrutura 'agendamento' exista no dicionário de dados
    if "agendamento" not in dados:
        dados["agendamento"] = {}

    # --- PARTE 1: Identificar a unidade escolhida ---
    # Este bloco só executa se a unidade ainda não foi definida
    if "unidade" not in dados["agendamento"]:
        if "vieiralves" in texto_normalizado or texto_original == "1":
            dados["agendamento"]["unidade"] = "Vieiralves"
            # Supondo que Vieiralves corresponde a múltiplas IDs na API
            dados["agendamento"]["clinica_ids"] = [1, 3] 
        elif "sao jose" in texto_normalizado or texto_original == "2":
            dados["agendamento"]["unidade"] = "São José"
            dados["agendamento"]["clinica_ids"] = [2]
        else:
            # Se a entrada não corresponde a nenhuma unidade, pergunta novamente
            resposta = dedent("""\
                Não entendi a unidade. Por favor, digite o nome ou o número correspondente:

                🏥 *Para qual unidade deseja agendar?*
                *1.* Vieiralves
                *2.* São José
            """).strip()
            return resposta, dados, "perguntar_unidade"

    # --- PARTE 2: A unidade foi definida, agora busca o paciente e os procedimentos ---
    
    # Busca o paciente apenas se ainda não tivermos os dados na sessão
    if not dados.get("paciente"):
        print("🔍 Verificando cadastro do paciente...")
        paciente_encontrado = buscar_paciente(session_data.get("from_number"))
        if paciente_encontrado:
            print(f"✅ Paciente encontrado: {paciente_encontrado.get('paciente_nome')}")
            dados["paciente"] = paciente_encontrado
        else:
            # Se não encontrou, direciona para o fluxo de paciente não cadastrado
            print("⚠️ Paciente não encontrado. Direcionando para cadastro.")
            return "⚠️ Não encontramos seu cadastro em nosso sistema. Vamos fazer um pré-cadastro rápido.", dados, "paciente_nao_cadastrado"
            
    # Pré-carrega os procedimentos disponíveis para o convênio do paciente
    convenio_id_paciente = dados.get("paciente", {}).get("convenio_id")
    if not convenio_id_paciente:
        return "⚠️ Identificamos seu cadastro, mas não há um convénio associado. Por favor, entre em contacto com a clínica para atualizar seus dados.", dados, "encerrado"

    print(f"🔗 Buscando procedimentos para o convénio ID: {convenio_id_paciente}")
    procedimentos_response = call("get_procedures_by_insurance", {"convenio_id": convenio_id_paciente})
    
    print(f"📡 Resposta da API get_procedures_by_insurance: {procedimentos_response}")
    
    procedimentos_disponiveis = procedimentos_response.get("data", []) if procedimentos_response else []
    
    # Log detalhado dos procedimentos
    print(f"📊 Procedimentos encontrados: {len(procedimentos_disponiveis)}")
    for i, proc in enumerate(procedimentos_disponiveis):
        print(f"  {i+1}. Nome: {proc.get('nome', 'N/A')} | ID: {proc.get('id', 'N/A')} | Estrutura: {proc}")
    
    dados["agendamento"]["procedimentos"] = procedimentos_disponiveis

    if not procedimentos_disponiveis:
        return f"✅ Unidade selecionada: *{dados['agendamento']['unidade']}*.\n\nNo entanto, não encontramos procedimentos disponíveis para o seu convénio nesta unidade. Por favor, entre em contacto com um atendente.", dados, "encerrado"

    # --- PARTE 3: Constrói a resposta para a próxima etapa ---
    
    lista_procedimentos_texto = "\n".join(
        f"*{i+1}.* {proc.get('nome', 'Procedimento sem nome')}" 
        for i, proc in enumerate(procedimentos_disponiveis)
    )
    
    primeiro_nome = dados.get("paciente", {}).get('paciente_nome', 'Olá').split()[0]
    
    resposta = dedent(f"""\
        Perfeito, {primeiro_nome}! Unidade selecionada: *{dados['agendamento']['unidade']}*.

        📋 Identificamos seu convénio e estes são os procedimentos disponíveis para você:

        {lista_procedimentos_texto}

        Por favor, digite o número do procedimento que deseja agendar.
    """).strip()

    return resposta, dados, "perguntar_procedimento"