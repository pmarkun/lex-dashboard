import streamlit as st
from utils import load_config, setup_authenticator

# Carregar a configuração do arquivo YAML
config = load_config()

# Configurar o autentificador
authenticator = setup_authenticator(config)

def show_login():
    # Página de Login
    name, authentication_status, username = authenticator.login()
    print(authentication_status)

    if authentication_status:
        # Salva o estado de autenticação na sessão
        st.session_state['authentication_status'] = True
        st.session_state['username'] = username
        st.session_state['name'] = name
        
    elif authentication_status == False:
        st.error('Nome de usuário ou senha incorretos')
    elif authentication_status == None:
        st.warning('Por favor, insira seu nome de usuário e senha')

def show_authenticated_user():
    # Exibe o nome do usuário autenticado e um botão de logout
    st.success(f"Bem-vindo, {st.session_state['name']}!")
    if st.button('Sair'):
        # Limpa a sessão ao clicar em "Sair"
        authenticator.logout()
        st.session_state.clear()

# Verifica o estado de autenticação
if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    # Mostra a página de login se o usuário não estiver autenticado
    show_login()
else:
    # Se autenticado, mostra o nome do usuário e o botão de logout
    show_authenticated_user()
