import streamlit as st
from firebase_utils import get_active_users_last_48_hours, log_message
from twilio_utils import send_message_via_twilio
from utils import check_permission

st.set_page_config(layout="wide")

@check_permission("editor")  # Verifica se o usuário tem permissão de editor ou superior
def show():
    st.title("Envio de Mensagens")

    # Obter usuários que enviaram mensagens nas últimas 48 horas
    active_users = get_active_users_last_48_hours()
    total_active_users = len(active_users)

    # Exibir contador de usuários válidos
    st.subheader(f"Usuários válidos nas últimas 48 horas: {total_active_users}")

    # Inicializa a lista de usuários selecionados se não estiver presente
    if "selected_users" not in st.session_state:
        st.session_state.selected_users = []

    
      # Caixa de texto para escrever a mensagem
    st.subheader("Escrever Mensagem")
    message = st.text_area("Mensagem")

    # Botão para enviar mensagem
    if st.button("Enviar Mensagem"):
        if not st.session_state.selected_users:
            st.warning("Nenhum usuário selecionado.")
        elif not message:
            st.warning("Mensagem está vazia.")
        else:
            success_count = 0
            for user in st.session_state.selected_users:
                if user.get('phone'):
                    phone = 'whatsapp:' + user['phone']
                    if send_message_via_twilio(phone, message):
                        success_count += 1
                
            st.success(f"{success_count} mensagens enviadas com sucesso.")
            st.session_state.selected_users = []  # Limpa a lista após o envio
            st.rerun()
    
    # Exibir a coluna de busca e adição de destinatários
    col1, col2 = st.columns(2)

    with col1:
        col1_1, col1_2 = st.columns([3, 1])
        with col1_1:
            st.subheader("Buscar Usuários")
        with col1_2:
            if st.button("Adicionar TODOS"):
                for user in active_users:
                    if user not in st.session_state.selected_users:
                        st.session_state.selected_users.append({**user, "remove": False})

        search_query = st.text_input("Digite um nome ou número para buscar", "")

        # Filtrar usuários ativos com base na consulta
        filtered_users = [
            user for user in active_users
            if search_query.lower() in user.get("profileName", "").lower() or search_query.lower() in user.get("phone", "").lower()
        ]

        # Cria um container para os botões com rolagem
        with st.container():
            button_cols = st.columns(4)  # Divida a área de botões em 4 colunas

            for idx, user in enumerate(filtered_users):
                col = button_cols[idx % 4]  # Use o índice para distribuir os botões nas colunas
                with col:
                    if st.button(f"{user['profileName']} ({user['phone']})", key=f"add_{user['profileName']}_{user['phone']}"):
                        if user not in st.session_state.selected_users:
                            st.session_state.selected_users.append({**user, "remove": False})


    
    # Exibir a tabela de destinatários selecionados e a interface de edição
    with col2:
        st.subheader("Destinatários Selecionados")
        if not st.session_state.selected_users:
            st.write("Nenhum destinatário selecionado.")
        else:
            col2_1, col2_2 = st.columns([4, 1])
            with col2_1:
                st.write(f"Total de destinatários selecionados: {len(st.session_state.selected_users)}")
            with col2_2:
                # Botão para remover todos os destinatários
                if st.button("Remover Todos"):
                    st.session_state.selected_users = []
                    st.rerun()

            # Exibir cada usuário selecionado com opção de remoção
            for index, user in enumerate(st.session_state.selected_users):
                
                with col2_1:
                    st.write(f"{user['profileName']} ({user['phone']})")
                with col2_2:
                    # Checkbox para remover usuário
                    if st.checkbox("Remover", key=f"remove_{index}"):
                        user["remove"] = True

            # Botão para aplicar as remoções selecionadas
            if st.button("Aplicar Remoções"):
                st.session_state.selected_users = [user for user in st.session_state.selected_users if not user.get("remove")]
                import time
                time.sleep(1)
                st.rerun()  # Força a interface a ser atualizada

  

show()
