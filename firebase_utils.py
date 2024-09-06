from google.cloud import firestore
from datetime import datetime, timedelta
import streamlit as st

# Configurações do Firestore
project_id = st.secrets["FIRESTORE_PROJECT_ID"]
credentials_info = st.secrets["FIRESTORE_CREDENTIALS"]
database = st.secrets["FIRESTORE_DATABASE"]

# Autenticando e inicializando o cliente do Firestore
db = firestore.Client(
    project=project_id,
    credentials=firestore.Client.from_service_account_info(credentials_info)._credentials,
    database=database
)

users_collection = db.collection('users')

# Função para obter os dados dos usuários da coleção
def get_users():
    users = users_collection.order_by('updatedAt', direction=firestore.Query.DESCENDING).stream()
    user_data = []
    for user in users:
        data = user.to_dict()
        data['id'] = user.id
        if 'updatedAt' not in data:
            if 'lastMessageTime' in data:
                data['updatedAt'] = data['lastMessageTime']
            else:
                data['updatedAt'] = datetime(1900, 1, 1)
        user_data.append(data)
    user_data.sort(key=lambda x: x['updatedAt'], reverse=True)
    return user_data

# Função para buscar usuários por telefone ou profileName
def search_users(query):
    users_ref = users_collection.where('phone', '==', query).stream()
    user_data = [user.to_dict() for user in users_ref]

    if not user_data:
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
    one_week_ago_datetime = datetime.combine(one_week_ago, datetime.min.time())

    users_data = []
    messages_data = []

    users_query = users_collection.where('updatedAt', '>=', one_week_ago_datetime)
    users_data = [user.to_dict() for user in users_query.stream()]

    sessions_collection = db.collection('sessions')
    for session in sessions_collection.stream():
        messages_query = session.reference.collection('messages').where('createdAt', '>=', one_week_ago_datetime)
        messages_data += [message.to_dict() for message in messages_query.stream()]

    return users_data, messages_data

# Função para criar links para WhatsApp
def create_whatsapp_link(profile_name, phone):
    phone_number = phone if phone else profile_name
    return f"https://wa.me/{phone_number}" if phone_number else None


def get_active_users_last_48_hours():
    two_days_ago = datetime.utcnow() - timedelta(hours=48)
    users_ref = users_collection.where('lastMessageTime', '>=', two_days_ago).stream()
    active_users = [user.to_dict() for user in users_ref]
    return active_users


def get_user_conversation(user):
    thread_id = user.get('threadId')
    messages_collection = db.collection('sessions').document(thread_id).collection('messages')
    messages_collection = messages_collection.order_by('createdAt').stream()
    messages = [message.to_dict() for message in messages_collection]
    return messages

# Função para adicionar uma mensagem no log
def log_message(phone, message):
    try:
        # Referência para a subcoleção 'messages' dentro do documento 'session_id'
        messages_ref = db.collection('sessions').document(threadId).collection('messages').document()

        # Adiciona a mensagem com o campo 'createdAt' como a timestamp do servidor
        messages_ref.set({
            **message,
            'createdAt': firestore.SERVER_TIMESTAMP
        })
        print(f"Mensagem adicionada com sucesso à sessão {threadId}")
    
    except Exception as e:
        print(f"Erro ao adicionar mensagem ao Firestore: {e}")
        raise e  # Lança a exceção novamente para que o erro seja detectado no nível superior
