import datetime
import logging
import math

import numpy as np
import pandas as pd
import streamlit as st

from core.database import db
from services.partners_service import PartnersService
from services.publications_service import PublicationsService

logger = logging.getLogger(__name__)

# --- Page configuration ---
st.set_page_config(page_title='Resultado Vendas', layout='wide')
st.title('📊 Relatório Resultado de Vendas Anual')
st.markdown('Compare os resultados de vendas de uma publicação entre o ano selecionado e o ano anterior.')


# --- Funções de Lógica do Relatório ---


def fetch_sales_data(schema: str, publication: str, year: int) -> pd.DataFrame:
    """
    Fetches sales data from the database for the specified publication and years.
    This function MUST be adapted with the correct SQL query for your database.
    """
    if not db:
        st.error('Gerenciador do banco não disponível para buscar dados de vendas.')
        return pd.DataFrame()

    end_date = datetime.date(year, 12, 31).strftime('%Y-%m-%d')
    start_date = datetime.date(year - 1, 1, 1).strftime('%Y-%m-%d')
    logger.info(
        f'Buscando dados de vendas para Pub: {publication}, Ano Anterior: {start_date[:4]}, Ano Atual: {end_date[:4]}'
    )

    query = f"""
    SELECT
        YEAR(a.DISDAT_0) as Ano,
        a.NUMEDI_0 as Edicao,
        a.DISDAT_0 as Data,
        a.QTYRREC_0 as Fornecimento,
        ((a.QTYREXP_0+ISNULL(CONVERT(int,b.QTY_0),0))-a.QTYRDEV_0) as Vendas,
        a.QTYRDEV_0 as Devolucoes,
        a.QTYREXP_0,ISNULL(b.QTY_0,0) AS QTYOTH_0
    FROM {schema}.ZITMINP a WITH (NOLOCK)
    LEFT JOIN (SELECT x.ITMREF_0,SUM(CASE WHEN y.INVTYP_0=2 THEN x.QTY_0*-1 ELSE x.QTY_0 END) AS QTY_0
            FROM {schema}.SINVOICED x WITH (NOLOCK)
            INNER JOIN {schema}.SINVOICE y WITH (NOLOCK) ON y.NUM_0=x.NUM_0
            WHERE x.CPY_0='INP'
            AND x.BPCINV_0 NOT IN (SELECT VALEUR_0 FROM {schema}.ADOVAL WITH (NOLOCK) WHERE PARAM_0='BPCINV')
            GROUP BY x.ITMREF_0) b ON b.ITMREF_0=a.ITMREF_0
    WHERE a.DISTVSP_0=2
    AND a.CODPUB_0=:pub_param
    AND a.DISDAT_0 BETWEEN :start_date AND :end_date
    ORDER BY a.DISDAT_0,a.NUMEDI_0
    """
    params = {'pub_param': publication, 'start_date': start_date, 'end_date': end_date}

    df = db.run_query(query, params)

    if df.empty:
        logger.warning(f'Nenhum dado retornado do banco para os parâmetros: {params}')
        return pd.DataFrame()

    logger.info(f'Dados brutos recebidos do banco ({len(df)} linhas). Colunas: {df.columns.tolist()}')

    # Garantir tipos de dados corretos (especialmente Data)
    try:
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        # Converter colunas numéricas, tratando possíveis erros se não forem numéricas
        for col in ['Ano', 'Fornecimento', 'Vendas', 'Devolucoes']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remover linhas onde a conversão falhou (dados inválidos)
        original_len = len(df)
        df = df.dropna(subset=['Data', 'Ano', 'Fornecimento', 'Vendas', 'Edicao', 'Devolucoes'])
        if len(df) < original_len:
            logger.warning(
                f'{original_len - len(df)} linhas removidas devido a valores nulos/inválidos após conversão de tipos.'
            )

    except Exception as e:
        logger.error(f'Erro durante a conversão de tipos de dados: {e}', exc_info=True)
        st.error(f'Erro ao processar os tipos de dados recebidos do banco: {e}')
        return pd.DataFrame()

    if df.empty:
        logger.warning(f'Dados vazios após limpeza/conversão de tipos para os parâmetros: {params}')

    return df


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas adicionais como '% não vendidos' e quantidade não vendida."""
    if df.empty:
        return df

    # Check if columns exists before calculating
    required_cols = {'Fornecimento', 'Vendas', 'Devolucoes'}

    if not required_cols.issubset(df.columns):
        logger.error("Colunas 'Devolucoes' ou 'Vendas' não encontradas no DataFrame para calcular métricas.")
        st.error(
            "Erro interno: Colunas essenciais ('Devolucoes', 'Vendas', 'Fornecimento') não encontradas após buscar dados."  # noqa: E501
        )
        df['Nao_Vendidos_Qtd'] = 0
        df['Nao_Vendidos_Perc'] = 0.0
        return df

    logger.info('Calculando métricas: Nao_Vendidos_Qtd e Nao_Vendidos_Perc.')
    df['Nao_Vendidos_Qtd'] = df['Devolucoes']

    # Prevent division by zero
    df['Nao_Vendidos_Perc_Float'] = df.apply(
        lambda row: ((row['Fornecimento'] - row['Vendas']) / row['Fornecimento']) * 100
        if row['Fornecimento'] > 0
        else 0,
        axis=1,
    )

    df['Nao_Vendidos_Perc'] = df['Nao_Vendidos_Perc_Float'].round().astype(int).clip(lower=0, upper=100)
    df['Nao_Vendidos_Qtd'] = df['Nao_Vendidos_Qtd'].clip(lower=0)

    # Remove coluna temporária
    df = df.drop(columns=['Nao_Vendidos_Perc_Float'])

    logger.info('Métricas calculadas com sucesso.')

    if not df.empty:
        logger.debug(
            f'Exemplo de dados após calculate_metrics:\n{df[["Fornecimento", "Vendas", "Devolucoes", "Nao_Vendidos_Qtd", "Nao_Vendidos_Perc"]].head()}'  # noqa: E501
        )

    return df


def create_comparison_table(df_data: pd.DataFrame, year_current: int) -> pd.DataFrame:  # noqa: PLR0914, PLR0915
    """Cria a tabela de comparação formatada com multi-índice."""
    if df_data.empty:
        st.warning('Não há dados processados para exibir a tabela de comparação.')
        return

    logger.info('Iniciando a criação da tabela de comparação visual.')
    year_previous = year_current - 1

    # Separa DFs por ano
    df_curr = df_data[df_data['Ano'] == year_current].copy()
    df_prev = df_data[df_data['Ano'] == year_previous].copy()

    # Ordena por data individualmente e reseta o índice para alinhar por linha
    df_curr = df_curr.sort_values(by='Data').reset_index(drop=True)
    df_prev = df_prev.sort_values(by='Data').reset_index(drop=True)

    # Define as colunas que se repetem para cada ano
    cols_per_edition = ['Fornecimento', 'Vendas', 'Nao_Vendidos_Perc', 'Nao_Vendidos_Qtd']
    cols_identity = ['Edicao', 'Data']

    # Seleciona e renomeia colunas do ano anterior
    df_prev_display = df_prev[cols_identity + cols_per_edition].copy()
    df_prev_display.columns = ['Edição', 'Data'] + [f'{col}_Prev' for col in cols_per_edition]

    # Seleciona e renomeia colunas do ano atual
    df_curr_display = df_curr[cols_identity + cols_per_edition].copy()
    df_curr_display.columns = ['Edição', 'Data'] + [f'{col}_Curr' for col in cols_per_edition]

    # --- Cálculos de Variação (Alinhados por Índice/Linha) ---
    logger.info('Calculando variações alinhadas por linha.')
    df_concat_for_var = pd.concat(
        [
            df_prev[['Vendas']].rename(columns={'Vendas': 'Vendas_Prev'}),
            df_curr[['Edicao', 'Vendas']].rename(columns={'Vendas': 'Vendas_Curr'}),
        ],
        axis=1,
    )
    df_concat_for_var['Vendas_Prev'] = df_concat_for_var['Vendas_Prev'].fillna(0)
    df_concat_for_var['Vendas_Curr'] = df_concat_for_var['Vendas_Curr'].fillna(0)
    df_concat_for_var['Edicao'] = df_concat_for_var['Edicao'].fillna('N/A (Ano Ant.)')
    df_concat_for_var['Var_Vendas_Copias'] = df_concat_for_var['Vendas_Curr'] - df_concat_for_var['Vendas_Prev']
    df_concat_for_var['Var_Vendas_Perc'] = df_concat_for_var.apply(
        lambda row: ((row['Vendas_Curr'] - row['Vendas_Prev']) / row['Vendas_Prev']) * 100
        if row.get('Vendas_Prev') and row['Vendas_Prev'] > 0
        else float('inf')
        if row.get('Vendas_Curr') and row['Vendas_Curr'] > 0
        else 0,
        axis=1,
    )
    df_concat_for_var['Var_Vendas_Perc'] = df_concat_for_var['Var_Vendas_Perc'].replace(
        [float('inf'), -float('inf')], None
    )
    df_variation_display = df_concat_for_var[['Var_Vendas_Copias', 'Var_Vendas_Perc']].copy()
    df_variation_display.columns = ['Var_Cópias', 'Var_%']

    # --- Exibição com st.columns ---
    st.subheader(f'Comparativo: {year_previous} vs {year_current}')
    logger.info('Renderizando tabelas de comparação.')

    col1, col2, col3 = st.columns([3, 3, 2])  # Ajuste as larguras [Anterior, Atual, Variação]

    with col1:
        st.markdown(f'**Ano Anterior ({year_previous})**')
        if df_prev_display.empty:
            st.caption('Nenhum dado para o ano anterior.')
        else:
            st.dataframe(
                df_prev_display,
                column_config={
                    'Data': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
                    'Fornecimento_Prev': st.column_config.NumberColumn('Fornecimento', format='%d'),
                    'Vendas_Prev': st.column_config.NumberColumn('Vendas', format='%d'),
                    'Nao_Vendidos_Perc_Prev': st.column_config.NumberColumn('% Não Vendidos', format='%d%%'),
                    'Nao_Vendidos_Qtd_Prev': st.column_config.NumberColumn('Qtd Não Vendidos', format='%d'),
                },
                use_container_width=True,
                hide_index=True,
            )

    with col2:
        st.markdown(f'**Ano Atual ({year_current})**')
        if df_curr_display.empty:
            st.caption('Nenhum dado para o ano atual.')
        else:
            st.dataframe(
                df_curr_display,
                column_config={
                    'Data': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
                    'Fornecimento_Curr': st.column_config.NumberColumn('Fornecimento', format='%d'),
                    'Vendas_Curr': st.column_config.NumberColumn('Vendas', format='%d'),
                    'Nao_Vendidos_Perc_Curr': st.column_config.NumberColumn('% Não Vendidos', format='%d%%'),
                    'Nao_Vendidos_Qtd_Curr': st.column_config.NumberColumn('Qtd Não Vendidos', format='%d'),
                },
                use_container_width=True,
                hide_index=True,
            )

    with col3:
        st.markdown('**Variações (Vendas)**')
        if df_variation_display.empty:
            st.caption('Nenhum dado para exibir variações.')
        else:

            def highlight_negative(val):
                """Retorna 'color: red' para números negativos, senão string vazia."""
                color = 'red' if pd.notna(val) and isinstance(val, (int, float)) and val < 0 else ''
                return f'color: {color}'

            # Aplica o estilo e o formato
            df_variation_display.style.map(highlight_negative).format(
                {
                    'Var_Cópias': '{:,.0f}',  # Formato inteiro com vírgula
                    'Var_%': '{:.0f}%',  # Formato percentual com 1 decimal
                },
                na_rep='-',
            )

            st.dataframe(
                df_variation_display,  # A Edição aqui é a do Ano Atual
                column_config={
                    'Var_Cópias': st.column_config.NumberColumn('Cópias', format='%d'),  # Sinal de +/-
                    'Var_%': st.column_config.NumberColumn(
                        '%',
                        format='%d%%',
                        help="Variação percentual. Vazio ou 'inf' indica que vendas anteriores eram 0.",
                    ),
                },
                use_container_width=True,
                hide_index=True,
            )

    # --- Rodapé com Totais e Médias ---
    logger.info('Renderizando rodapé com totais e médias.')
    logger.info('Calculando e montando a tabela de resumo unificada.')

    # --- Cálculos ---
    # Função auxiliar para calcular percentual com teto e tratar divisão por zero/NaN
    def calculate_percentage_ceil(numerator, denominator):
        if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
            return np.nan
        # Calcula e aplica o teto
        percentage = (numerator / denominator) * 100
        return math.ceil(percentage) if not pd.isna(percentage) else np.nan

    # Valores Totais Ano Anterior
    total_forn_prev = round(df_prev_display['Fornecimento_Prev'].sum()) if not df_prev_display.empty else 0
    print(total_forn_prev, type(total_forn_prev))
    total_vend_prev = df_prev_display['Vendas_Prev'].sum() if not df_prev_display.empty else 0
    perc_total_vend_prev = calculate_percentage_ceil(total_vend_prev, total_forn_prev)

    # Valores Médios Ano Anterior
    media_forn_prev = df_prev_display['Fornecimento_Prev'].mean() if not df_prev_display.empty else 0
    media_vend_prev = df_prev_display['Vendas_Prev'].mean() if not df_prev_display.empty else 0
    # Para % da média, usamos os valores médios calculados
    perc_media_vend_prev = calculate_percentage_ceil(media_vend_prev, media_forn_prev)
    media_nao_vend_qtd_prev = df_prev_display['Nao_Vendidos_Qtd_Prev'].mean() if not df_prev_display.empty else 0

    # Valores Totais Ano Atual
    total_forn_curr = df_curr_display['Fornecimento_Curr'].sum() if not df_curr_display.empty else 0
    total_vend_curr = df_curr_display['Vendas_Curr'].sum() if not df_curr_display.empty else 0
    perc_total_vend_curr = calculate_percentage_ceil(total_vend_curr, total_forn_curr)

    # Valores Médios Ano Atual
    media_forn_curr = df_curr_display['Fornecimento_Curr'].mean() if not df_curr_display.empty else 0
    media_vend_curr = df_curr_display['Vendas_Curr'].mean() if not df_curr_display.empty else 0
    # Para % da média, usamos os valores médios calculados
    perc_media_vend_curr = calculate_percentage_ceil(media_vend_curr, media_forn_curr)
    media_nao_vend_qtd_curr = df_curr_display['Nao_Vendidos_Qtd_Curr'].mean() if not df_curr_display.empty else 0

    # Valores Médios Variação
    # Tratamento de NaN/None em 'Var_%' antes da média
    valid_var_perc = df_variation_display['Var_%'].dropna()
    media_var_copias = df_variation_display['Var_Cópias'].mean() if not df_variation_display.empty else 0
    media_var_perc = valid_var_perc.mean() if not valid_var_perc.empty else np.nan  # Média dos % válidos

    # --- Montagem do DataFrame de Resumo ---
    logger.info('Montando DataFrame de resumo com MultiIndex nas colunas.')

    # Chaves do dicionário serão tuplas: (Ano/Grupo, Métrica)
    summary_data = {
        # Ano Anterior (convertido para string)
        (str(year_previous), 'Fornecimento'): [total_forn_prev, media_forn_prev],
        (str(year_previous), 'Vendas'): [total_vend_prev, media_vend_prev],
        (str(year_previous), '% Venda'): [perc_total_vend_prev, perc_media_vend_prev],
        (str(year_previous), 'Qtd NV (Média)'): [np.nan, media_nao_vend_qtd_prev],
        # Ano Atual (convertido para string)
        (str(year_current), 'Fornecimento'): [total_forn_curr, media_forn_curr],
        (str(year_current), 'Vendas'): [total_vend_curr, media_vend_curr],
        (str(year_current), '% Venda'): [perc_total_vend_curr, perc_media_vend_curr],
        (str(year_current), 'Qtd NV (Média)'): [np.nan, media_nao_vend_qtd_curr],
        # Variação (já era string)
        ('Variação', 'Var Cópias (Média)'): [np.nan, media_var_copias],
        ('Variação', 'Var % (Média)'): [np.nan, media_var_perc],
    }

    # Cria o DataFrame. O Pandas criará automaticamente o MultiIndex a partir das tuplas.
    df_summary = pd.DataFrame(summary_data, index=['Total', 'Média'])
    # Opcional: Nomear os níveis do índice de coluna para clareza
    df_summary.columns.names = ['Período', 'Métrica']
    # Opcional: Nomear o índice da linha
    df_summary.index.name = 'Resumo'

    # --- Formatação e Exibição com MultiIndex ---
    logger.info('Formatando e exibindo tabela de resumo com MultiIndex.')
    st.dataframe(
        df_summary,
        column_config={
            'Fornecimento': st.column_config.NumberColumn('Fornecimento', format='%d'),
            'Vendas': st.column_config.NumberColumn('Vendas', format='%d'),
            '% Venda': st.column_config.NumberColumn('% Venda', format='%d%%'),
            'Qtd NV (Média)': st.column_config.NumberColumn('Qtd NV (Média)', format='%d'),
            'Var Cópias (Média)': st.column_config.NumberColumn('Var Cópias (Média)', format='%d'),
            'Var % (Média)': st.column_config.NumberColumn(
                'Var % (Média)',
                format='%d%%',
                help='Variação percentual média de vendas entre os anos.',
            ),
        },
        #     df_summary.style.format(
        #         {
        #             # O Styler aplicará a todas as colunas com essa métrica, independentemente do ano.
        #             'Fornecimento': '{:,.0f}'.replace(',', '.'),
        #             'Vendas': '{:,.0f}',
        #             '% Venda': '{:.0f}%',  # Percentual inteiro com %
        #             'Qtd NV (Média)': '{:,.1f}',  # Média com 1 decimal
        #             'Var Cópias (Média)': '{:,.1f}',  # Média com 1 decimal
        #             'Var % (Média)': '{:.1f}%',  # Média percentual com 1 decimal e %
        #         },
        #         na_rep='-',
        #     ),
        use_container_width=True,
    )

    logger.info('Tabela de resumo unificada renderizada.')

    return None


# --- Inputs ---
st.sidebar.header('Filtros do Relatório')

db_schema = st.secrets.get('database', {}).get('schema', 'X3')

# 1. Busca e Seleção de Fornecedor
suppliers = PartnersService
supplier_options = suppliers.fetch_raw_suppliers(db_schema)
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
        logger.debug(f'Fornecedor selecionado: {selected_supplier_name} (Código: {selected_supplier_code})')


# 2. Busca e Seleção de Publicação (Condicional ao Fornecedor)
publications = PublicationsService
publication_options = {}
selected_publication_name = None
selected_publication_code = None

if selected_supplier_code:  # Só busca se um fornecedor foi selecionado
    try:
        # Busca as publicações associadas ao fornecedor selecionado
        with st.spinner(f'Buscando publicações para {selected_supplier_name}...'):
            publication_options = publications.fetch_publications_by_supplier(db_schema, selected_supplier_code)

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
    # O botão fica desabilitado se não houver publicação e ano selecionados

    # Validação (redundante se o botão estiver desabilitado, mas bom ter)
    if not selected_supplier_code:
        st.warning('Por favor, selecione um fornecedor.')
    elif not selected_publication_code:
        st.warning('Por favor, selecione uma publicação.')
    elif not selected_year:
        st.warning('Por favor, selecione um ano.')
    else:
        # Todos os inputs estão ok, prossegue com a geração
        st.info(
            f'Gerando relatório para Fornecedor: {selected_supplier_name}, '
            f"Pub: '{selected_publication_name}' ({selected_year} vs {selected_year - 1})..."
        )

        # 1. Buscar os dados brutos (passando só publicação e ano)
        with st.spinner('Buscando dados de vendas...'):
            raw_data = fetch_sales_data(db_schema, selected_publication_code, selected_year)

        if raw_data.empty:
            st.error('Nenhum dado de venda encontrado para os filtros selecionados.')
        else:
            # 2. Calcular métricas
            with st.spinner('Calculando métricas...'):
                processed_data = calculate_metrics(raw_data)

            if processed_data.empty:
                st.warning('Os dados foram encontrados, mas ocorreram problemas no processamento.')
            else:
                # 3. Criar e exibir a tabela de comparação e rodapé
                with st.spinner('Montando a visualização...'):
                    create_comparison_table(processed_data, selected_year)

# Mensagem inicial ou de status na área principal
elif not selected_supplier_code:
    st.info('⬅️ Comece selecionando um fornecedor na barra lateral.')
elif not selected_publication_code:
    if selected_supplier_code and not publication_options:
        st.info(f'⬅️ Nenhuma publicação encontrada para {selected_supplier_name}. Verifique o fornecedor ou os dados.')
    else:
        st.info('⬅️ Selecione uma publicação na barra lateral.')
elif not selected_year:
    st.info('⬅️ Selecione o ano na barra lateral.')
# Não exibe 'clique em gerar' se o botão estiver desabilitado
elif selected_publication_code and selected_year:
    st.info("⬅️ Clique em 'Gerar Relatório' na barra lateral.")


# --- Rodapé da Sidebar com Fórmulas ---
st.sidebar.markdown('---')
st.sidebar.caption('Fórmulas (Baseadas na Query):')
# ... (resto das captions como antes) ...
st.sidebar.caption('- Fornecimento = QTYREXP_0 + Outras Qtds (QTYOTH_0)')
st.sidebar.caption('- Vendas = Fornecimento - Devoluções (QTYRDEV_0)')
st.sidebar.caption('- % Não Vendidos = (Fornecimento - Vendas) / Fornecimento * 100')
st.sidebar.caption('- Qtd Não Vendidos = Fornecimento - Vendas')
st.sidebar.caption('- Var. Vendas Cópias = Vendas Ano Atual - Vendas Ano Anterior (Alinhado por Data)')
st.sidebar.caption('- Var. Vendas % = (Var. Vendas Cópias / Vendas Ano Anterior) * 100')
