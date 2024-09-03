import streamlit as st
import altair as alt
import pandas as pd
from datetime import datetime, timedelta
from firebase_utils import get_users, get_total_messages, get_weekly_data, create_whatsapp_link
from utils import check_permission

# Função para paginar os usuários
def paginate_data(data, page_size, page_number):
    start_index = page_number * page_size
    end_index = start_index + page_size
    return data[start_index:end_index]

# Função para exibir o log de conversa de um usuário específico junto com os dados do usuário
def show_user_conversation(user):
    st.subheader("Dados do Usuário")
    st.write(f"**Nome:** {user.get('profileName', 'N/A')}")
    st.write(f"**Telefone:** {user.get('phone', user['id'])}")
    st.write(f"**Última Mensagem:** {user.get('lastMessageTime', 'N/A')}")

    st.subheader("Histórico de Conversa")
    thread_id = user.get('threadId')
    if not thread_id:
        st.write("Nenhuma conversa disponível para este usuário.")
        return

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
@check_permission("admin")
def show():
    st.set_page_config(layout="wide")
    user_data = get_users()
    total_users = len(user_data)
    total_messages = get_total_messages()
    
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

    col3, col4 = st.columns([2, 3])

    with col3:
        st.header("Últimos Usuários Registrados")
        page_size = 10
        page_number = st.number_input("Página", min_value=0, max_value=(total_users // page_size), step=1)
        paginated_users = paginate_data(user_data, page_size, page_number)

        for user in paginated_users:
            profile_name = user.get('profileName')
            phone = user.get('phone') or user['id']
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
                    st.write("💬", unsafe_allow_html=True)

    with col4:
        if 'selected_user' in st.session_state:
            show_user_conversation(st.session_state.selected_user)
        else:
            st.write("Selecione um usuário para ver a conversa.")

show()
