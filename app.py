from google.cloud import firestore
import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime, timedelta
import os


# Configurações do Firestore
project_id = st.secrets["FIRESTORE_PROJECT_ID"]
credentials_info = st.secrets["FIRESTORE_CREDENTIALS"]
database = st.secrets["FIRESTORE_DATABASE"]
login_password = st.secrets["LOGIN_PASSWORD"]

# Autenticando e inicializando o cliente do Firestore
db = firestore.Client(
    project=project_id,
    credentials=firestore.Client.from_service_account_info(credentials_info)._credentials,
    database=database
)

# Função para obter os dados dos usuários da coleção
def get_users():
    users = users_collection.order_by('updatedAt', direction=firestore.Query.DESCENDING).stream()
    user_data = []
    for user in users:
        data = user.to_dict()
        # Adiciona o ID do documento ao dicionário
        data['id'] = user.id
        # Verifica se o usuário tem updatedAt; se não tiver, define como uma data muito antiga
        if 'updatedAt' not in data:
            if 'lastMessageTime' in data:
                data['updatedAt'] = data['lastMessageTime']
            else:
                data['updatedAt'] = datetime(1900, 1, 1)  # Data antiga para ordenar no final
        user_data.append(data)

    # Ordena os usuários colocando os sem updatedAt no final
    user_data.sort(key=lambda x: x['updatedAt'], reverse=True)
    return user_data

# Função para buscar usuários por telefone ou profileName
def search_users(query):
    users_ref = users_collection.where('phone', '==', query).stream()
    user_data = [user.to_dict() for user in users_ref]

    if not user_data:  # Se não encontrar por telefone, buscar por profileName
        users_ref = users_collection.where('profileName', '==', query).stream()
        user_data = [user.to_dict() for user in users_ref]

    return user_data

# Função para obter o total de mensagens na coleção sessions->messages
def get_total_messages():
    sessions_collection = db.collection('sessions')
    total_messages = 0
    for session in sessions_collection.stream():
        messages = session.reference.collection('messages').stream()
        total_messages += sum(1 for _ in messages)
    return total_messages

# Função para obter os dados dos usuários e mensagens na última semana
def get_weekly_data():
    today = datetime.utcnow().date()
    one_week_ago = today - timedelta(days=7)

    # Converter datetime.date para datetime.datetime
    one_week_ago_datetime = datetime.combine(one_week_ago, datetime.min.time())

    users_data = []
    messages_data = []

    # Obtendo usuários na última semana
    users_query = users_collection.where('updatedAt', '>=', one_week_ago_datetime)
    users_data = [user.to_dict() for user in users_query.stream()]

    # Obtendo mensagens na última semana
    sessions_collection = db.collection('sessions')
    for session in sessions_collection.stream():
        messages_query = session.reference.collection('messages').where('createdAt', '>=', one_week_ago_datetime)
        messages_data += [message.to_dict() for message in messages_query.stream()]

    return users_data, messages_data

# Função para criar links para WhatsApp
def create_whatsapp_link(profile_name, phone):
    phone_number = phone if phone else profile_name
    return f"https://wa.me/{phone_number}" if phone_number else None

# Função para paginar os usuários
def paginate_data(data, page_size, page_number):
    start_index = page_number * page_size
    end_index = start_index + page_size
    return data[start_index:end_index]

# Função para exibir o log de conversa de um usuário específico junto com os dados do usuário
def show_user_conversation(user):
    # Exibe os dados do usuário
    st.subheader("Dados do Usuário")
    st.write(f"**Nome:** {user.get('profileName', 'N/A')}")
    st.write(f"**Telefone:** {user.get('phone', user['id'])}")
    st.write(f"**Última Mensagem:** {user.get('lastMessageTime', 'N/A')}")

    # Exibe o histórico de conversa
    st.subheader("Histórico de Conversa")
    thread_id = user.get('threadId')
    if not thread_id:
        st.write("Nenhuma conversa disponível para este usuário.")
        return

    # Acessar as mensagens na subcoleção 'messages'
    messages_collection = db.collection('sessions').document(thread_id).collection('messages')
    messages = messages_collection.order_by('createdAt').stream()

    for message in messages:
        message_data = message.to_dict()
        role = message_data.get('role')
        content = message_data.get('content')

        if role == 'ai':
            st.markdown(f"<div style='background-color: #e0f7fa; padding: 10px; border-radius: 5px;'>{content}</div>", unsafe_allow_html=True)
        elif role == 'human':
            st.markdown(f"<div style='background-color: #f1f8e9; padding: 10px; border-radius: 5px;'>{content}</div>", unsafe_allow_html=True)

# Exibindo os dados no dashboard principal
def show_dashboard():
    st.set_page_config(layout="wide")  # Configura para usar a largura total da página
    user_data = get_users()
    total_users = len(user_data)
    total_messages = get_total_messages()
    
    # Configurando o layout em duas colunas para Estatísticas Gerais e Atividade na Última Semana
    st.title("Dashboard de Usuários")
    col1, col2 = st.columns(2)

    with col1:
        st.header("Estatísticas Gerais")
        st.write(f"Total de Usuários Registrados: {total_users}")
        st.write(f"Total de Mensagens Enviadas: {total_messages}")

    with col2:
        users_data, messages_data = get_weekly_data()
        st.header("Atividade na Última Semana")
        dates = [datetime.utcnow().date() - timedelta(days=i) for i in range(7)]
        users_count = [len([u for u in users_data if u['updatedAt'].date() == date]) for date in dates]
        messages_count = [len([m for m in messages_data if m['createdAt'].date() == date]) for date in dates]

        data = pd.DataFrame({
            'Data': dates * 2,
            'Quantidade': users_count + messages_count,
            'Categoria': ['Usuários Registrados'] * len(dates) + ['Mensagens Enviadas'] * len(dates)
        })

        chart = alt.Chart(data).mark_line(point=True).encode(
            x='Data:T',
            y='Quantidade:Q',
            color='Categoria:N',
            tooltip=['Data:T', 'Quantidade:Q', 'Categoria:N']
        ).properties(
            title='Atividade na Última Semana'
        )

        st.altair_chart(chart, use_container_width=True)

    # Configurando o layout em duas colunas para Últimos Usuários e Conversas
    col3, col4 = st.columns([2, 3])

    with col3:
        st.header("Últimos Usuários Registrados")
        page_size = 10
        page_number = st.number_input("Página", min_value=0, max_value=(total_users // page_size), step=1)
        paginated_users = paginate_data(user_data, page_size, page_number)

        for user in paginated_users:
            profile_name = user.get('profileName')
            phone = user.get('phone') or user['id']  # Use o ID do documento como phone se phone não estiver disponível
            link = create_whatsapp_link(profile_name, phone)
            thread_id = user.get('threadId')
            
            col3_1, col3_2 = st.columns([4, 1])
            with col3_1:
                st.write(f"[{profile_name or phone}]({link})", unsafe_allow_html=True)
            with col3_2:
                if thread_id:
                    if st.button("💬", key=f"{thread_id}_{profile_name or phone}"):
                        st.session_state.selected_user = user
                else:
                    st.write("💬", unsafe_allow_html=True)  # Emoji desativado

    with col4:
        if 'selected_user' in st.session_state:
            show_user_conversation(st.session_state.selected_user)
        else:
            st.write("Selecione um usuário para ver a conversa.")

def show_login():
    st.title("Login")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if password == login_password:
            st.session_state.logged_in = True
        else:
            st.error("Senha incorreta. Tente novamente.")

if __name__ == "__main__":
    users_collection = db.collection('users')
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        show_login()
    else:
        show_dashboard()
