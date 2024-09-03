import streamlit as st
from twilio.rest import Client

# Função para enviar mensagens usando Twilio
def send_message_via_twilio(to_number, message):
    # Carregar credenciais da Twilio a partir do st.secrets
    account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
    auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
    twilio_number = st.secrets["TWILIO_FROM"]
    
    
    # Inicializar o cliente Twilio
    client = Client(account_sid, auth_token)
    
    # Enviar a mensagem
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=to_number
        )
        return True
    except Exception as e:
        st.error(f"Erro ao enviar mensagem para {to_number}: {e}")
        return False
