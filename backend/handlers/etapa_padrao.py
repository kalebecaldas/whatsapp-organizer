from clinicaagil_client import call

def process(texto, dados, session_data):
    if texto.lower() in ["sim", "confirmar"]:
        resultado = call("register_appointment", dados)

        if resultado.get("status") == "success":
            resposta = "✅ Agendamento confirmado com sucesso! Até breve. 🦡"
        else:
            resposta = "❌ Algo deu errado ao registrar. Por favor, tente novamente mais tarde."

        return resposta, dados, "fim"
    else:
        return "Agendamento cancelado. Se quiser começar de novo, digite *agendar*.", dados, "fim"
