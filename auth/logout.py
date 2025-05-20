import logging

import streamlit as st

logger = logging.getLogger(__name__)

st.title('Logout')

if not st.session_state.get('authenticated', False):
    st.switch_page('pages/login.py')
    st.stop()

st.warning('Você tem certeza que deseja sair?')

if st.button('Logout'):
    user_logout = st.session_state.get('user', 'Unknown user')
    # Limpa as chaves de sessão relacionadas à autenticação
    for key in ['authenticated', 'user']:  # Adicione outras chaves se tiver
        if key in st.session_state:
            del st.session_state[key]

    logger.info(f'User {user_logout} logged out.')
    st.rerun()
