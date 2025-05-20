import logging

import streamlit as st

logger = logging.getLogger(__name__)

st.title('Reset Password')

# --- Verificação de Autenticação ---
if not st.session_state.get('authenticated', False):
    st.error('🔒 Acesso negado. Por favor, faça login para visualizar esta página.')
    st.caption('Você será redirecionado para a página de login.')
    if st.button('Ir para Login', key='redirect_login_sales_board'):
        st.switch_page('pages/login.py')
    st.stop()
