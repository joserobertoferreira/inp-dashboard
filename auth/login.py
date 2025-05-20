import logging

import streamlit as st

from services.authentication import AuthenticationService

logger = logging.getLogger(__name__)

st.caption('Por favor, informe suas credenciais para acessar o sistema.')

if st.session_state.get('authenticated', False):
    st.success(f'Bem-vindo, {st.session_state.user}!')
    st.info('Você já está autenticado. Você pode acessar o sistema.')
    st.stop()

with st.form(key='login_form', clear_on_submit=True):
    username = st.text_input('Username', placeholder='Enter your username')
    password = st.text_input('Password', type='password', placeholder='Enter your password')
    login_btn = st.form_submit_button('Login')

if login_btn:
    result = {}
    login_ok = False

    try:
        result = AuthenticationService.login(username=username, password=password)
    except ValueError as e:
        st.error(f'Login failed: {e}')
        logger.error(f'Login failed for user {username}')

    if result and result.get('username'):
        login_ok = True
        st.session_state.authenticated = True
        st.session_state.user = result.get('username')
        logger.info(f'User {st.session_state.user} logged in successfully.')
        st.rerun()
    else:
        # st.session_state.authenticated = False
        # st.session_state.user = None
        logger.warning(f'Login failed for user {username}')
        st.error('Invalid username or password.')
