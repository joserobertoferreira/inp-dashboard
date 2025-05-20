import logging
from pathlib import Path

import streamlit as st
import yaml

from services.user_service import UserService

logger = logging.getLogger(__name__)

PROJECT_ROOT_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_DIR = PROJECT_ROOT_DIR / '.streamlit'
CREDENTIALS_FILE = CREDENTIALS_DIR / 'credentials.yaml'


def setup_credentials_file():
    """
    Set up the credentials.yaml file for Streamlit Authenticator
    by fetching users from the database.
    """
    logger.info(f'Tentando gerar o arquivo de credenciais em: {CREDENTIALS_FILE}')

    user_list_for_auth = UserService.fetch_users_for_auth()

    if not user_list_for_auth:
        st.warning('Nenhum utilizador encontrado no banco para gerar o credentials.yaml ou houve um erro na busca.')
        logger.warning('Arquivo credentials.yaml não será gerado/atualizado pois não há utilizadores ou ocorreu erro.')
        return

    authenticator_cookie_key = st.secrets['database']['authenticator_cookie_key']
    if not authenticator_cookie_key:
        logger.warning("Chave 'authenticator_cookie_key' não encontrada em st.secrets. Usando valor padrão inseguro.")
        authenticator_cookie_key = 'default_random_key_CHANGE_ME_IN_SECRETS_TOML'
        st.warning("ALERTA DE SEGURANÇA: 'authenticator_cookie_key' não definida em secrets.toml. Usando chave padrão.")

    expiry_days = int(st.secrets['database']['authenticator_cookie_expiry_days'])
    cookie_name = st.secrets['database']['authenticator_cookie_name']

    credentials_config = {
        'credentials': {'usernames': user_list_for_auth},
        'cookie': {
            'expiry_days': expiry_days if expiry_days else 1,
            'key': authenticator_cookie_key,
            'name': cookie_name if cookie_name else 'inp_rms_cookie',
        },
        'preauthorized': {'emails': st.secrets.get('authenticator_preauthorized_emails', [])},
    }

    try:
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(credentials_config, f, default_flow_style=False, sort_keys=False)
        logger.info(f'Arquivo credentials.yaml gerado/atualizado com sucesso em {CREDENTIALS_FILE}')
        # st.toast("Arquivo de credenciais atualizado.", icon="🔑") # Feedback sutil
    except IOError as e:
        st.error(f'Erro de I/O ao escrever o arquivo credentials.yaml: {e}')
        logger.error(f'Erro de I/O ao escrever o arquivo credentials.yaml: {e}', exc_info=True)
    except Exception as e:
        st.error(f'Erro inesperado ao escrever o arquivo credentials.yaml: {e}')
        logger.error(f'Erro inesperado ao escrever o arquivo credentials.yaml: {e}', exc_info=True)
