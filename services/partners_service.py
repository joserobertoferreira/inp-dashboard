import logging

import pandas as pd
import streamlit as st

from core.database import db

logger = logging.getLogger(__name__)


class PartnersService:
    """
    Service class for managing partners (customers and suppliers).

    Returns:
        - A dictionary containing the list of partners.
    """

    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=3600)
    def fetch_raw_suppliers(schema: str) -> dict:
        """
        Fetches the list of suppliers (editors) from the database.
        Args:
            schema (str): The database schema to query.
        Returns:
            dict: A dictionary with supplier names as keys and their codes as values.
        """

        # Define the database connection
        if not db:
            logger.error('Database connection is not established.')
            st.error('Gerenciador do banco não disponível.')
            return {}

        logger.info('Buscar lista de fornecedores (Editores)...')
        query = f"""
        SELECT
            BPRNUM_0 AS Fornecedor,
            BPRNAM_0 AS Nome
        FROM
            {schema}.BPARTNER
        WHERE
            ZEDITOR_0 = 2 AND
            BPSFLG_0 = 2 AND
            EXISTS (SELECT 1 FROM {schema}.ZPUBLIC WHERE DISTVSP_0=2 AND BPSREF_0=BPARTNER.BPRNUM_0)
        ORDER BY
            BPRNAM_0;
        """

        try:
            df_suppliers = db.run_query(query)

            if df_suppliers.empty:
                logger.warning('Nenhum fornecedor (editor) encontrado')
                return {}
            else:
                # Cria o dicionário {Nome: Fornecedor}
                supplier_dict = pd.Series(df_suppliers.Fornecedor.values, index=df_suppliers.Nome).to_dict()
                logger.info(f'Encontrados {len(supplier_dict)} fornecedores.')
                return supplier_dict
        except Exception as e:
            logger.error(f'Erro ao buscar fornecedores: {e}', exc_info=True)
            st.error(f'Erro ao carregar a lista de fornecedores: {e}')
            return {}
