import logging

import streamlit as st

from utils.logging_config import setup_logging

# Configuração de logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info('Aplicação iniciada.')

st.set_page_config(
    page_title='Dashboard de Consultas',
    page_icon='📊',
    layout='wide',  # Usar layout 'wide' para dashboards
    initial_sidebar_state='expanded',  # Manter sidebar aberta por padrão
)

st.title('📊 Bem-vindo ao Dashboard de Consultas')

st.sidebar.success('Selecione um relatório acima.')

st.markdown(
    """
    Este é um dashboard interativo para visualizar dados importantes.

    **👈 Selecione um relatório na barra lateral** para começar!

    ### Relatórios Disponíveis:
    *   **Comparativo de Vendas Anual:** Analisa vendas de uma publicação comparando o ano atual com o anterior.
    *   _(Outros relatórios serão adicionados aqui)_

    ---
    *Desenvolvido com Streamlit*
    """
)

# Você pode adicionar mais informações aqui, como links úteis, contatos, etc.
