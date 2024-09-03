import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Função para carregar o arquivo de configuração YAML
def load_config():
    with open('users.yaml', 'r') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    # Verifica se as senhas precisam ser hash
    credentials = config['credentials']
    usernames = credentials['usernames']
    hasher = stauth.Hasher([])
    
    # Converte senhas em texto simples para hash, se necessário
    for username in usernames:
        password = usernames[username]['password']
        if not password.startswith('$2b$'):  # Verifica se a senha já não está hash
            hashed_password = hasher._hash(password)
            usernames[username]['password'] = hashed_password

    return config

# Função para configurar o autentificador
def setup_authenticator(config):
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )
    return authenticator

# Decorador para verificar permissões
def check_permission(required_permission):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Verifica se o usuário está autenticado
            if 'authentication_status' in st.session_state and st.session_state['authentication_status']:
                # Acessa diretamente o nome de usuário e as permissões do arquivo de configuração
                username = st.session_state['username']
                config = load_config()  # Carrega as configurações
                user_permissions = config['credentials']['usernames']
                
                # Verifica se o usuário tem a permissão necessária
                if user_permissions.get(username).get("role") in ("admin", required_permission):
                    return func(*args, **kwargs)
                else:
                    st.error("Permissão Negada")
            else:
                st.error("Você não está autenticado.")
        return wrapper
    return decorator
