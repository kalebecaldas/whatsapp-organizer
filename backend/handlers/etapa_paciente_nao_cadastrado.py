import re
from datetime import datetime
from handlers.etapa_perguntar_procedimento import process as etapa_perguntar_procedimento
from data.convenios import CONVENIOS
from core.paciente_utils import precarregar_agendamento_para_paciente
from clinicaagil_client import call

def validar_cpf(cpf):
    """Valida CPF usando algoritmo oficial"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    return cpf[-2:] == f"{digito1}{digito2}"

def validar_data_nascimento(data_str):
    """Valida data de nascimento no formato DD/MM/YYYY"""
    try:
        data = datetime.strptime(data_str, "%d/%m/%Y")
        hoje = datetime.now()
        
        # Verifica se a data é no passado e não muito antiga
        if data > hoje:
            return False, "Data de nascimento não pode ser no futuro"
        
        idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
        if idade < 0 or idade > 120:
            return False, "Idade deve estar entre 0 e 120 anos"
        
        return True, None
    except ValueError:
        return False, "Formato inválido. Use DD/MM/YYYY"

def validar_telefone(telefone):
    """Valida formato de telefone brasileiro"""
    # Remove caracteres não numéricos
    telefone_limpo = re.sub(r'[^0-9]', '', telefone)
    
    # Verifica se tem 10 ou 11 dígitos (com DDD)
    if len(telefone_limpo) not in [10, 11]:
        return False
    
    return True

def process(texto, dados, session_data):
    """
    Etapa de cadastro de paciente não cadastrado.
    Coleta todos os dados necessários e depois integra com o fluxo de agendamento.
    """
    texto = texto.strip()
    
    # Inicialização do fluxo de cadastro
    if "cadastro_status" not in dados:
        if texto == "1":
            dados["cadastro_status"] = "iniciando"
            dados["dados_paciente"] = {}  # Inicializa estrutura para dados do paciente
            return (
                "🎉 Perfeito! Vamos fazer seu cadastro para agilizar o processo!\n\n"
                "📝 **Por favor, informe seu nome completo:**\n"
                "Exemplo: João Silva Santos",
                dados,
                "paciente_nao_cadastrado"
            )
        elif texto == "2":
            return (
                "📞 Entendi! Encaminhei sua solicitação para um de nossos atendentes. "
                "Eles entrarão em contato em breve.\n\n"
                "⏰ **Tempo médio de resposta:** 5-10 minutos\n"
                "📱 **Canal:** WhatsApp\n\n"
                "Obrigado pela paciência! 😊",
                dados,
                "encerrado"
            )
        else:
            return (
                "❓ Opção inválida. Por favor, escolha:\n\n"
                "1️⃣ **Fazer cadastro online** (recomendado)\n"
                "2️⃣ **Falar com atendente**\n\n"
                "Qual opção você prefere?",
                dados,
                "paciente_nao_cadastrado"
            )

    # Coleta de dados do paciente
    dados_paciente = dados.get("dados_paciente", {})
    cadastro_status = dados.get("cadastro_status")
    
    # Etapa 1: Nome completo
    if cadastro_status == "iniciando" and "nome" not in dados_paciente:
        if len(texto.split()) < 2:
            return (
                "❗️ Por favor, informe seu **nome completo** (nome e sobrenome).\n\n"
                "📝 **Exemplo:** João Silva Santos",
                dados,
                "paciente_nao_cadastrado"
            )
        
        dados_paciente["nome"] = texto.title()
        dados["dados_paciente"] = dados_paciente
        dados["cadastro_status"] = "coletando_cpf"
        
        return (
            f"✅ **Nome salvo:** {texto.title()}\n\n"
            "🆔 **Agora preciso do seu CPF:**\n"
            "📝 Digite apenas os números (11 dígitos)\n"
            "Exemplo: 12345678901",
            dados,
            "paciente_nao_cadastrado"
        )
    
    # Etapa 2: CPF
    elif cadastro_status == "coletando_cpf" and "cpf" not in dados_paciente:
        cpf_limpo = re.sub(r'[^0-9]', '', texto)
        
        if len(cpf_limpo) != 11:
            return (
                "❗️ CPF deve ter **11 dígitos**. Digite apenas os números.\n\n"
                "📝 **Exemplo:** 12345678901",
                dados,
                "paciente_nao_cadastrado"
            )
        
        if not validar_cpf(cpf_limpo):
            return (
                "❗️ CPF inválido. Verifique os números e tente novamente.\n\n"
                "📝 **Exemplo:** 12345678901",
                dados,
                "paciente_nao_cadastrado"
            )
        
        dados_paciente["cpf"] = cpf_limpo
        dados["dados_paciente"] = dados_paciente
        dados["cadastro_status"] = "coletando_data_nascimento"
        
        return (
            "✅ **CPF validado com sucesso!**\n\n"
            "📅 **Agora preciso da sua data de nascimento:**\n"
            "📝 Formato: DD/MM/AAAA\n"
            "Exemplo: 15/03/1990",
            dados,
            "paciente_nao_cadastrado"
        )
    
    # Etapa 3: Data de nascimento
    elif cadastro_status == "coletando_data_nascimento" and "data_nascimento" not in dados_paciente:
        valido, erro = validar_data_nascimento(texto)
        
        if not valido:
            return (
                f"❗️ {erro}\n\n"
                "📅 **Formato correto:** DD/MM/AAAA\n"
                "📝 **Exemplo:** 15/03/1990",
                dados,
                "paciente_nao_cadastrado"
            )
        
        dados_paciente["data_nascimento"] = texto
        dados["dados_paciente"] = dados_paciente
        dados["cadastro_status"] = "coletando_telefone"
        
        return (
            "✅ **Data de nascimento salva!**\n\n"
            "📱 **Agora preciso do seu telefone:**\n"
            "📝 Digite com DDD (apenas números)\n"
            "Exemplo: 92991234567",
            dados,
            "paciente_nao_cadastrado"
        )
    
    # Etapa 4: Telefone
    elif cadastro_status == "coletando_telefone" and "telefone" not in dados_paciente:
        telefone_limpo = re.sub(r'[^0-9]', '', texto)
        
        if not validar_telefone(telefone_limpo):
            return (
                "❗️ Telefone inválido. Digite apenas os números com DDD.\n\n"
                "📝 **Exemplo:** 92991234567",
                dados,
                "paciente_nao_cadastrado"
            )
        
        dados_paciente["telefone"] = telefone_limpo
        dados["dados_paciente"] = dados_paciente
        dados["cadastro_status"] = "coletando_endereco"
        
        return (
            "✅ **Telefone salvo!**\n\n"
            "🏠 **Agora preciso do seu endereço:**\n"
            "📝 Digite: Rua, número, bairro, cidade\n"
            "Exemplo: Rua das Flores, 123, Centro, Manaus",
            dados,
            "paciente_nao_cadastrado"
        )
    
    # Etapa 5: Endereço
    elif cadastro_status == "coletando_endereco" and "endereco" not in dados_paciente:
        if len(texto) < 10:
            return (
                "❗️ Por favor, informe um endereço mais completo.\n\n"
                "📝 **Exemplo:** Rua das Flores, 123, Centro, Manaus",
                dados,
                "paciente_nao_cadastrado"
            )
        
        dados_paciente["endereco"] = texto
        dados["dados_paciente"] = dados_paciente
        dados["cadastro_status"] = "coletando_convenio"
        
        # Apresentar lista de convênios disponíveis
        opcoes_convenios = [nome for nome in CONVENIOS.keys() if CONVENIOS[nome] != "DESCONTO"]
        opcoes_convenios.append("Particular")
        lista_convenios = "\n".join(f"{i+1}. {nome}" for i, nome in enumerate(opcoes_convenios))
        return (
            f"✅ **Endereço salvo!**\n\n"
            f"🏥 **Agora preciso saber sobre convênio:**\n"
            f"Escolha uma das opções abaixo ou digite o nome do seu convênio:\n"
            f"{lista_convenios}\n\n"
            f"Se não tiver convênio, escolha 'Particular'.",
            dados,
            "paciente_nao_cadastrado"
        )

    # Etapa 6: Convênio
    elif cadastro_status == "coletando_convenio" and "convenio" not in dados_paciente:
        # Normalizar entrada
        texto_normalizado = texto.strip().lower()
        opcoes_convenios = [nome for nome in CONVENIOS.keys() if CONVENIOS[nome] != "DESCONTO"]
        opcoes_convenios.append("Particular")
        nomes_normalizados = [nome.lower() for nome in opcoes_convenios]
        
        # Verificar se o convênio está na lista
        convenio_escolhido = None
        if texto_normalizado.isdigit():
            idx = int(texto_normalizado) - 1
            if 0 <= idx < len(opcoes_convenios):
                convenio_escolhido = opcoes_convenios[idx]
        elif texto_normalizado in nomes_normalizados:
            convenio_escolhido = opcoes_convenios[nomes_normalizados.index(texto_normalizado)]
        else:
            # Estratégia para convênio não atendido
            return (
                "No momento não atendemos esse convênio. Mas podemos te atender como particular, com condições especiais para primeira consulta.\n\n"
                "Deseja saber mais sobre o atendimento particular?",
                dados,
                "paciente_nao_cadastrado"
            )
        
        dados_paciente["convenio"] = convenio_escolhido
        dados["dados_paciente"] = dados_paciente
        dados["cadastro_status"] = "finalizado"
        
        # Pré-carregar procedimentos e profissionais se não for particular
        if convenio_escolhido != "Particular":
            paciente_fake = {"convenio_id": convenio_escolhido, "clinica_id": 1}  # clinica_id pode ser ajustado
            dados["agendamento_precarregado"] = precarregar_agendamento_para_paciente(paciente_fake, call)
        # Estratégia para particular
        else:
            # Pode adicionar lógica para diferenciais, condições, etc.
            pass
        
        # Resumo dos dados coletados
        nome = dados_paciente.get("nome", "")
        cpf = dados_paciente.get("cpf", "")
        data_nasc = dados_paciente.get("data_nascimento", "")
        telefone = dados_paciente.get("telefone", "")
        endereco = dados_paciente.get("endereco", "")
        convenio = dados_paciente.get("convenio", "")
        
        resumo = (
            f"🎉 **Cadastro concluído com sucesso!**\n\n"
            f"📋 **Dados coletados:**\n"
            f"👤 **Nome:** {nome}\n"
            f"🆔 **CPF:** {cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}\n"
            f"📅 **Nascimento:** {data_nasc}\n"
            f"📱 **Telefone:** {telefone}\n"
            f"🏠 **Endereço:** {endereco}\n"
            f"🏥 **Convênio:** {convenio}\n\n"
            f"✅ **Agora vamos para o agendamento!**\n\n"
            f"📅 **Qual procedimento você gostaria de agendar?**\n\n"
            f"Digite o número ou nome do procedimento:"
        )
        
        # Inicializar dados do agendamento (pode ser ajustado para usar agendamento_precarregado)
        dados["agendamento"] = {
            "procedimentos": []  # Será preenchido na próxima etapa
        }
        
        return resumo, dados, "perguntar_procedimento"
    
    # Fallback para casos inesperados
    else:
        return (
            "❓ Desculpe, não entendi. Vamos recomeçar o cadastro.\n\n"
            "📝 **Digite seu nome completo:**",
            dados,
            "paciente_nao_cadastrado"
        )
