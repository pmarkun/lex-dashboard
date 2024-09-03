import streamlit as st
from utils import check_permission  # Importe o decorador do utils

@check_permission("viewer")
def show():
    st.title("Aba 2")
    st.write("Conteúdo da Aba 2 - Acesso para Visualizadores, Editores e Admins")

show()