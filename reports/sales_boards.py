import datetime
import logging

import streamlit as st
from streamlit_extras.grid import grid

from services.partners_service import PartnersService
from services.publications_service import PublicationsService
from services.sales_boards_service import SalesBoardsService
from utils.comparison_table_data import config_columns_to_sales_boards

logger = logging.getLogger(__name__)

# --- Verificação de Autenticação ---
if not st.session_state.get('authenticated', False):
    st.warning('🔒 Acesso negado. Por favor, faça login para visualizar esta página.')
    st.stop()


# --- Page configuration ---
st.subheader('📊 Relatório Resultado de Vendas Anual')
st.markdown('Compare os resultados de vendas de uma publicação entre o ano selecionado e o ano anterior.')

# --- Inputs ---
st.sidebar.header('Filtros do Relatório')

db_schema = st.secrets.get('database', {}).get('schema', 'X3')

sales_data = SalesBoardsService

# 1. Busca e Seleção de Fornecedor
supplier_options = PartnersService.fetch_raw_suppliers(db_schema)
selected_supplier_name = None
selected_supplier_code = None

if not supplier_options:
    st.sidebar.error('Não foi possível carregar a lista de fornecedores.')
else:
    selected_supplier_name = st.sidebar.selectbox(
        'Selecione o Fornecedor (Editor):',
        options=list(supplier_options.keys()),  # Mostra os nomes
        index=None,  # Começa sem seleção
        placeholder='Escolha um fornecedor...',
        key='supplier_select',  # Chave para o selectbox
    )
    # Se um nome foi selecionado, pega o código correspondente
    if selected_supplier_name:
        selected_supplier_code = supplier_options[selected_supplier_name]
        logger.info(f'Fornecedor selecionado: {selected_supplier_name} (Código: {selected_supplier_code})')

# 2. Busca e Seleção de Publicação (Condicional ao Fornecedor)
publication_options = {}
selected_publication_name = None
selected_publication_code = None

if selected_supplier_code:  # Só busca se um fornecedor foi selecionado
    try:
        # Busca as publicações associadas ao fornecedor selecionado
        with st.spinner(f'Buscar publicações para {selected_supplier_name}...'):
            publication_options = PublicationsService.fetch_publications_by_supplier(db_schema, selected_supplier_code)

        if publication_options:
            selected_publication_name = st.sidebar.selectbox(
                'Selecione a Publicação:',
                options=list(publication_options.keys()),  # Mostra os nomes/descrições
                index=None,
                placeholder='Escolha uma publicação...',
                key=f'pub_select_{selected_supplier_code}',  # Chave dinâmica ajuda a resetar
                help='Publicações disponíveis para o fornecedor selecionado.',
            )
            if selected_publication_name:
                selected_publication_code = publication_options[selected_publication_name]
                logger.debug(
                    f'Publicação selecionada: {selected_publication_name} (Código: {selected_publication_code})'
                )
        else:
            st.sidebar.info(f"Nenhuma publicação encontrada para '{selected_supplier_name}'.")
            # Limpa seleção anterior se houver
            selected_publication_name = None
            selected_publication_code = None

    except Exception as e:
        st.sidebar.error(f'Erro ao buscar publicações: {e}')
        # Limpa seleções em caso de erro
        publication_options = {}
        selected_publication_name = None
        selected_publication_code = None

# 3. Seleção do Ano (Condicional à Seleção da Publicação)
selected_year = None
if selected_publication_code:  # Só mostra se uma publicação foi selecionada
    current_year = datetime.date.today().year
    selected_year = st.sidebar.number_input(
        'Selecione o Ano:',
        min_value=2000,
        max_value=current_year,
        value=current_year,
        step=1,
        format='%d',
        key=f'year_input_{selected_supplier_code}_{selected_publication_code}',  # Chave dinâmica
    )
    logger.debug(f'Ano selecionado: {selected_year}')


# --- Botão para Gerar Relatório e Lógica Principal ---
if st.sidebar.button(
    'Gerar Relatório', key='generate_report_button', disabled=(not selected_publication_code or not selected_year)
):
    if not selected_supplier_code:
        st.warning('Por favor, selecione um fornecedor.')
    elif not selected_publication_code:
        st.warning('Por favor, selecione uma publicação.')
    elif not selected_year:
        st.warning('Por favor, selecione um ano.')
    else:
        # Todos os inputs estão ok, prossegue com a geração
        st.info(
            f'Gerar relatório para Fornecedor: {selected_supplier_name}, '
            f"Pub: '{selected_publication_name}' ({selected_year - 1} vs {selected_year})..."
        )

        # 1. Buscar os dados brutos (passando só publicação e ano)
        with st.spinner('Buscar dados de vendas...'):
            raw_data = sales_data.fetch_sales_data(db_schema, selected_publication_code, selected_year)

        if raw_data.empty:
            st.error('Nenhum dado de venda encontrado para os filtros selecionados.')
        else:
            # 2. Criar tabelas de comparação
            with st.spinner('Montar a visualização...'):
                df_sales, prev_metrics, curr_metrics = sales_data.create_comparison_table(raw_data, selected_year)

                if not df_sales.empty:
                    df_show = df_sales.drop(columns=['Year_prev', 'Year_curr'], errors='ignore')

                    st.dataframe(
                        df_show,
                        use_container_width=True,
                        hide_index=True,
                        column_config=config_columns_to_sales_boards(
                            prev_year=selected_year - 1, curr_year=selected_year
                        ),
                    )

                    st.divider()

                    my_grid = grid(1, [2, 4, 1], 1, 4, vertical_align='bottom')

                    # Row 1:
                    my_grid.dataframe(
                        df_show,
                        use_container_width=True,
                    )
                    # Row 2:
                    my_grid.selectbox('Select Country', ['Germany', 'Italy', 'Japan', 'USA'])
                    my_grid.text_input('Your name')
                    my_grid.button('Send', use_container_width=True)
                    # Row 3:
                    my_grid.text_area('Your message', height=68)
                    # Row 4:
                    my_grid.button('Example 1', use_container_width=True)
                    my_grid.button('Example 2', use_container_width=True)
                    my_grid.button('Example 3', use_container_width=True)
                    my_grid.button('Example 4', use_container_width=True)
                    # Row 5 (uses the spec from row 1):
                    with my_grid.expander('Show Filters', expanded=True):
                        st.slider('Filter by Age', 0, 100, 50)
                        st.slider('Filter by Height', 0.0, 2.0, 1.0)
                        st.slider('Filter by Weight', 0.0, 100.0, 50.0)
                else:
                    st.info('Não há dados processados para exibir a tabela de comparação.')

# # Mensagem inicial ou de status na área principal
# elif not selected_supplier_code:
#     st.info('⬅️ Comece selecionando um fornecedor na barra lateral.')
# elif not selected_publication_code:
#     if selected_supplier_code and not publication_options:
#         st.info(f'⬅️ Nenhuma publicação encontrada para {selected_supplier_name}. Verifique o fornecedor ou os dados.')
#     else:
#         st.info('⬅️ Selecione uma publicação na barra lateral.')
# elif not selected_year:
#     st.info('⬅️ Selecione o ano na barra lateral.')
# # Não exibe 'clique em gerar' se o botão estiver desabilitado
# elif selected_publication_code and selected_year:
#     st.info("⬅️ Clique em 'Gerar Relatório' na barra lateral.")


# # --- Rodapé da Sidebar com Fórmulas ---
# st.sidebar.markdown('---')
# st.sidebar.caption('Fórmulas (Baseadas na Query):')
# # ... (resto das captions como antes) ...
# st.sidebar.caption('- Fornecimento = QTYREXP_0 + Outras Qtds (QTYOTH_0)')
# st.sidebar.caption('- Vendas = Fornecimento - Devoluções (QTYRDEV_0)')
# st.sidebar.caption('- % Não Vendidos = (Fornecimento - Vendas) / Fornecimento * 100')
# st.sidebar.caption('- Qtd Não Vendidos = Fornecimento - Vendas')
# st.sidebar.caption('- Var. Vendas Cópias = Vendas Ano Atual - Vendas Ano Anterior (Alinhado por Data)')
# st.sidebar.caption('- Var. Vendas % = (Var. Vendas Cópias / Vendas Ano Anterior) * 100')
