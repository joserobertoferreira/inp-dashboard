import datetime
import logging
import math

import numpy as np
import pandas as pd
import streamlit as st

from core.database import db
from utils.comparison_table_data import ComparisonTableData

logger = logging.getLogger(__name__)


class SalesBoardsService:
    """
    Service class for handling sales boards data.
    This class is responsible for fetching and processing sales data from the database.
    """

    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_sales_data(schema: str, publication: str, year: int) -> pd.DataFrame:
        """
        Fetches sales data from the database for the specified publication and years.
        This function MUST be adapted with the correct SQL query for your database.
        """

        if not db:  # Verifica se db e seu engine foram inicializados
            st.error('Gerenciador do banco não disponível para buscar dados de vendas.')
            logger.error('Gerenciador do banco não disponível para buscar dados de vendas.')
            return pd.DataFrame()

        end_date = datetime.date(year, 12, 31).strftime('%Y-%m-%d')
        start_date = datetime.date(year - 1, 1, 1).strftime('%Y-%m-%d')
        logger.info(
            f'Buscar dados de vendas para Pub: {publication}, Ano Anterior: {start_date[:4]}, Ano Atual: {end_date[:4]}'
        )

        query = f"""
        SELECT
            YEAR(a.DISDAT_0) as Year,
            a.NUMEDI_0 as Issue,
            a.DISDAT_0 as Date,
            a.QTYRREC_0 as Supply,
            ((a.QTYREXP_0+ISNULL(CONVERT(int,b.QTY_0),0))-a.QTYRDEV_0) as Sales,
            ISNULL(c.OUT,0) as Outlet
        FROM {schema}.ZITMINP a WITH (NOLOCK)
        LEFT JOIN (SELECT x.ITMREF_0,SUM(CASE WHEN y.INVTYP_0=2 THEN x.QTY_0*-1 ELSE x.QTY_0 END) AS QTY_0
                FROM {schema}.SINVOICED x WITH (NOLOCK)
                INNER JOIN {schema}.SINVOICE y WITH (NOLOCK) ON y.NUM_0=x.NUM_0
                WHERE x.CPY_0='INP'
                AND x.BPCINV_0 NOT IN (SELECT VALEUR_0 FROM {schema}.ADOVAL WITH (NOLOCK) WHERE PARAM_0='BPCINV')
                GROUP BY x.ITMREF_0) b ON b.ITMREF_0=a.ITMREF_0
        LEFT JOIN (SELECT ITMREF_0,COUNT(1) AS OUT FROM {schema}.ZBPCEST GROUP BY ITMREF_0) c ON c.ITMREF_0=a.ITMREF_0
        WHERE a.DISTVSP_0=2
        AND a.PERNUM_0>1
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
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # Converter colunas numéricas, tratando possíveis erros se não forem numéricas
            for col in ['Year', 'Supply', 'Sales', 'Outlet']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Remover linhas onde a conversão falhou (dados inválidos)
            original_len = len(df)
            df = df.dropna(subset=['Date', 'Year', 'Supply', 'Sales', 'Issue', 'Outlet'])
            if len(df) < original_len:
                logger.warning(
                    f'{original_len - len(df)} linhas removidas devido a valores '
                    f'nulos/inválidos após conversão de tipos.'
                )

            # Calcular coluna Unsolds
            df['Unsolds'] = np.where(
                df['Supply'] > 0,
                np.ceil(((df['Supply'] - df['Sales']) / df['Supply']) * 100).astype(int),
                0,
            )

        except Exception as e:
            logger.error(f'Erro durante a conversão de tipos de dados: {e}', exc_info=True)
            st.error(f'Erro ao processar os tipos de dados recebidos do banco: {e}')
            return pd.DataFrame()

        if df.empty:
            logger.warning(f'Dados vazios após limpeza/conversão de tipos para os parâmetros: {params}')

        return df

    @staticmethod
    def calculate_metrics(df: pd.DataFrame, year: int) -> dict[str, int]:  # noqa: PLR0914
        """
        Process the dataframe to calculate metrics for the specified year.
        Args:
            df (pd.DataFrame): DataFrame containing sales data.
            year (int): Year for which to calculate metrics.
        Returns:
            dict: dictionary with calculated metrics.
        """

        cols = df.columns.tolist()
        df_processed = df[cols].copy()

        # Calcular Totais
        total_supply = df_processed['Supply'].sum()
        total_sales = df_processed['Sales'].sum()
        total_outlet = df_processed['Outlet'].sum()
        total_unsold_perc = np.nan
        if total_supply > 0:
            total_unsold_calc = (total_supply - total_sales) / total_supply
            total_unsold_perc = math.ceil(total_unsold_calc * 100) if pd.notnull(total_unsold_calc) else np.nan

        # Calcular Médias
        avg_supply = df_processed['Supply'].mean()
        avg_sales = df_processed['Sales'].mean()
        avg_outlet = df_processed['Outlet'].mean()
        avg_unsold_perc = np.nan

        # Checar se avg_supply não é NaN e é maior que 0 antes de calcular
        if pd.notnull(avg_supply) and avg_supply > 0:
            # Também precisamos garantir que avg_sales não seja NaN para o cálculo
            if pd.notnull(avg_sales):
                avg_unsold_calc = (avg_supply - avg_sales) / avg_supply
                avg_unsold_perc = math.ceil(avg_unsold_calc * 100) if pd.notnull(avg_unsold_calc) else np.nan

        return_metrics = {
            'total_supply': int(total_supply),
            'total_sales': int(total_sales),
            'total_outlet': int(total_outlet),
            'total_unsold': int(total_unsold_perc),
            'avg_supply': int(avg_supply),
            'avg_sales': int(avg_sales),
            'avg_outlet': int(avg_outlet),
            'avg_unsold': int(avg_unsold_perc),
        }

        return return_metrics

    @staticmethod
    def create_comparison_table(  # noqa: PLR0912, PLR0914, PLR0915
        df_data: pd.DataFrame, year_current: int
    ) -> tuple[pd.DataFrame, dict[str, int], dict[str, int]]:
        """
        Create a comparison table for the sales data.
        Args:
            df_data (pd.DataFrame): DataFrame containing sales data.
            year_current (int): Current year for comparison.
            Returns:
                tuple: Two DataFrames for the previous year and current year.
        """

        if df_data.empty:
            empty_df = pd.DataFrame()
            st.warning('Não há dados processados para exibir a tabela de comparação.')
            return empty_df, {}, {}

        # Split the DataFrame into two parts: previous year and current year
        df_prev_year = df_data[df_data['Year'] == year_current - 1].copy().reset_index(drop=True)
        df_current_year = df_data[df_data['Year'] == year_current].copy().reset_index(drop=True)

        prev_metrics = SalesBoardsService.calculate_metrics(df_prev_year, year_current - 1)
        curr_metrics = SalesBoardsService.calculate_metrics(df_current_year, year_current)

        df_full = pd.merge(
            df_prev_year, df_current_year, left_index=True, right_index=True, how='outer', suffixes=('_prev', '_curr')
        )

        df_full['Copies_var'] = pd.NA
        df_full['%_var'] = pd.NA

        prev_suffix = (year_current - 1) - 2000
        curr_suffix = year_current - 2000

        original_base_metrics = ['Issue', 'Date', 'Supply', 'Sales', 'Unsolds', 'Outlet']

        # Rename columns for clarity
        rename_map = {}

        for metric in original_base_metrics:
            rename_map[f'{metric}_prev'] = f'{metric}_{prev_suffix}'
            rename_map[f'{metric}_curr'] = f'{metric}_{curr_suffix}'

        df_full = df_full.rename(columns=rename_map)

        unsold_prev_column = f'Unsolds_{prev_suffix}'
        unsold_curr_column = f'Unsolds_{curr_suffix}'
        sales_prev_column = f'Sales_{prev_suffix}'
        sales_curr_column = f'Sales_{curr_suffix}'

        # Ensure numeric types for sales columns
        if sales_prev_column in df_full.columns:
            df_full[sales_prev_column] = pd.to_numeric(df_full[sales_prev_column], errors='coerce')
        if sales_curr_column in df_full.columns:
            df_full[sales_curr_column] = pd.to_numeric(df_full[sales_curr_column], errors='coerce')

        # Calculate differences
        for index, row in df_full.iterrows():
            sales_prev = row[sales_prev_column]
            sales_curr = row[sales_curr_column]

            if pd.notna(sales_prev) and pd.notna(sales_curr):
                # Calculate the difference in copies
                copies_diff = sales_curr - sales_prev
                df_full.at[index, 'Copies_var'] = copies_diff

                # Calculate the percentage difference
                if sales_prev != 0:
                    percent_diff = copies_diff / sales_prev  # * 100
                else:
                    percent_diff = 0.0

                if pd.notna(percent_diff) and np.isfinite(percent_diff):
                    df_full.at[index, '%_var'] = percent_diff
                else:
                    df_full.at[index, '%_var'] = pd.NA

            else:
                # Store the results in the new columns
                df_full.at[index, 'Copies_var'] = pd.NA
                df_full.at[index, '%_var'] = pd.NA

        df_full[unsold_prev_column] /= 100
        df_full[unsold_curr_column] /= 100

        return df_full, prev_metrics, curr_metrics

    @staticmethod
    def display_comparison_table_html(table_data: ComparisonTableData):
        """
        Constrói e exibe a tabela de comparação em HTML usando st.markdown.
        """
        SalesBoardsService._display_comparison_table_html_impl(table_data)

    @staticmethod
    def _display_comparison_table_html_impl(table_data):
        # Estilos CSS para a tabela
        table_style = """
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
                font-size: 0.9em;
            }
            th, td {
                border: 1px solid #5681d0;
                text-align: center;
                padding: 8px;
            }
            th {
                background-color: #1a1a3d;
            }
            .header-year {
                font-weight: bold;
                font-size: 1.1em;
            }
            .sub-header {
                font-style: italic;
            }
            .total-avg-label {
                text-align: left;
                font-weight: bold;
            }
            .variation-header {
                font-weight: bold;
            }
        </style>
        """
        st.markdown(table_style, unsafe_allow_html=True)

        xpto = """
            <table>
                <thead>
                    <tr>
                        <th colspan="6" class="header-year">1999</th>
                        <th colspan="6" class="header-year">2000</th>
                        <th colspan="2" class="variation-header">Variations</th>
                    </tr>
                    <tr>
                        <th colspan="1" class="sub-header"></th>
                        <th colspan="5" class="sub-header">Per Issue</th>
                        <th colspan="1" class="sub-header"></th>
                        <th colspan="5" class="sub-header">Per Issue</th>
                        <th colspan="2" class="sub-header">Sales</th>
                    </tr>
                    <tr>
                        <th>Issue</th><th>Date</th><th>Supply</th><th>Sales</th><th>% Unsold</th><th>Out</th>
                        <th>Issue</th><th>Date</th><th>Supply</th><th>Sales</th><th>% Unsold</th><th>Out</th>
                        <th>Copies</th><th>%</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>261</td>
                        <td>2024-02-28 00:00:00</td>
                        <td>2000</td>
                        <td>226</td>
                        <td>89%</td>
                        <td>747</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                    </tr>
                </tbody>
            </table>
        """

        st.markdown(xpto, unsafe_allow_html=True)

        html_table = SalesBoardsService._build_comparison_table_html(table_data)

        st.markdown(html_table, unsafe_allow_html=True)

    @staticmethod
    def _build_comparison_table_html(table_data):  # noqa: PLR0914
        # Unpack for readability
        (
            comparison_rows,
            total_prev,
            total_curr,
            avg_prev,
            avg_curr,
            var_total_sales_copies,
            var_total_sales_perc,
            var_avg_sales_copies,
            var_avg_sales_perc,
            previous_year,
            current_year,
        ) = (
            table_data.comparison_rows,
            table_data.total_prev,
            table_data.total_curr,
            table_data.avg_prev,
            table_data.avg_curr,
            table_data.var_total_sales_copies,
            table_data.var_total_sales_perc,
            table_data.var_avg_sales_copies,
            table_data.var_avg_sales_perc,
            table_data.previous_year,
            table_data.current_year,
        )

        html_table = f"""
        <table>
            <thead>
                <tr>
                    <th colspan="6" class="header-year">{previous_year}</th>
                    <th colspan="6" class="header-year">{current_year}</th>
                    <th colspan="2" class="variation-header">Variations</th>
                </tr>
                <tr>
                    <th colspan="1" class="sub-header"></th>
                    <th colspan="5" class="sub-header">Per Issue</th>
                    <th colspan="1" class="sub-header"></th>
                    <th colspan="5" class="sub-header">Per Issue</th>
                    <th colspan="2" class="sub-header">Sales</th>
                </tr>
                <tr>
                    <th>Issue</th><th>Date</th><th>Supply</th><th>Sales</th><th>% Unsold</th><th>Out</th>
                    <th>Issue</th><th>Date</th><th>Supply</th><th>Sales</th><th>% Unsold</th><th>Out</th>
                    <th>Copies</th><th>%</th>
                </tr>
            </thead>
            <tbody>

        """

        for row in comparison_rows:
            html_table += f"""
                <tr>
                    <td>{row['issue_prev']}</td>
                    <td>{row['date_prev']}</td>
                    <td>{row['supply_prev']}</td>
                    <td>{row['sales_prev']}</td>
                    <td>{row['unsold_prev']}</td>
                    <td>{row['out_prev']}</td>
                    <td>{row['issue_curr']}</td>
                    <td>{row['date_curr']}</td>
                    <td>{row['supply_curr']}</td>
                    <td>{row['sales_curr']}</td>
                    <td>{row['unsold_curr']}</td>
                    <td>{row['out_curr']}</td>
                    <td>{row['var_copies']}</td>
                    <td>{row['var_perc']}</td>
                </tr>
            """

        html_table += """
                <tr>
                    <td colspan="14"
                        style="
                            border-left: 1px solid #5681d0;
                            border-right: 1px solid #5681d0;
                            background-color: #1a1a3d;
                            height: 2px;
                        ">
                    </td>
                </tr>
            """

        def safe_fmt(val, key, percent=False):
            if pd.notnull(val.get(key, None)):
                if percent:
                    return f'{val[key]:.0f}%'
                return f'{val[key]:.0f}'
            return '-'

        total_prev_unsold_display = safe_fmt(total_prev, '% Unsold', percent=True)
        total_curr_unsold_display = safe_fmt(total_curr, '% Unsold', percent=True)
        total_prev_supply_display = safe_fmt(total_prev, 'Fornecimento')
        total_prev_sales_display = safe_fmt(total_prev, 'Vendas')
        total_prev_outlet_display = safe_fmt(total_prev, 'Outlet')
        total_curr_supply_display = safe_fmt(total_curr, 'Fornecimento')
        total_curr_sales_display = safe_fmt(total_curr, 'Vendas')
        total_curr_outlet_display = safe_fmt(total_curr, 'Outlet')

        html_table += f"""
                <tr style="font-weight: bold;">
                    <td class="total-avg-label" colspan="2">{total_prev.get('Edicao', '-')}</td>
                    <td>{total_prev_supply_display}</td>
                    <td>{total_prev_sales_display}</td>
                    <td>{total_prev_unsold_display}</td>
                    <td>{total_prev_outlet_display}</td>
                    <td class="total-avg-label" colspan="2">{total_curr.get('Edicao', '-')}</td>
                    <td>{total_curr_supply_display}</td>
                    <td>{total_curr_sales_display}</td>
                    <td>{total_curr_unsold_display}</td>
                    <td>{total_curr_outlet_display}</td>
                    <td>{var_total_sales_copies}</td>
                    <td>{var_total_sales_perc}</td>
                </tr>
        """

        html_table += """
                <tr>
                    <td colspan="14"
                        style="
                            border-left: 1px solid #5681d0;
                            border-right: 1px solid #5681d0;
                            background-color: #1a1a3d;
                            height: 2px;
                        ">
                    </td>
                </tr>
            """

        avg_prev_unsold_display = safe_fmt(avg_prev, '% Unsold', percent=True)
        avg_curr_unsold_display = safe_fmt(avg_curr, '% Unsold', percent=True)
        avg_prev_supply_display = safe_fmt(avg_prev, 'Fornecimento')
        avg_prev_sales_display = safe_fmt(avg_prev, 'Vendas')
        avg_prev_outlet_display = safe_fmt(avg_prev, 'Outlet')
        avg_curr_supply_display = safe_fmt(avg_curr, 'Fornecimento')
        avg_curr_sales_display = safe_fmt(avg_curr, 'Vendas')
        avg_curr_outlet_display = safe_fmt(avg_curr, 'Outlet')

        html_table += f"""
                <tr style="font-weight: bold;">
                    <td class="total-avg-label" colspan="2">{avg_prev.get('Edicao', '-')}</td>
                    <td>{avg_prev_supply_display}</td>
                    <td>{avg_prev_sales_display}</td>
                    <td>{avg_prev_unsold_display}</td>
                    <td>{avg_prev_outlet_display}</td>
                    <td class="total-avg-label" colspan="2">{avg_curr.get('Edicao', '-')}</td>
                    <td>{avg_curr_supply_display}</td>
                    <td>{avg_curr_sales_display}</td>
                    <td>{avg_curr_unsold_display}</td>
                    <td>{avg_curr_outlet_display}</td>
                    <td>{var_avg_sales_copies}</td>
                    <td>{var_avg_sales_perc}</td>
                </tr>
        """

        html_table += """
            </tbody>
        </table>
        """

        return html_table
