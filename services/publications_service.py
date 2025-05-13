import logging

import pandas as pd
import streamlit as st

from core.database import db

logger = logging.getLogger(__name__)


class PublicationsService:
    """
    Service class for managing publications (editors).
    """

    def __init__(self):
        pass

    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_publications_by_supplier(schema: str, supplier_code: str) -> dict:
        """
        Searches for publications associated with a supplier code (BPSNUM_0).
        Args:
            schema (str): The database schema to query.
            supplier_code (str): The supplier code to filter publications.
        Returns:
            dict: A dictionary with publication names as keys and their codes as values.
        """

        if not supplier_code:
            return {}

        # Define the database connection
        if not db:
            logger.error('Database connection is not established.')
            st.error('Database connection is not established.')
            return {}

        logger.info(f'Buscando publicações para o fornecedor: {supplier_code}')

        query = f"""
        SELECT
            CODPUB_0 AS CodigoPub,
            DESPUB_0 AS NomePub
        FROM
            {schema}.ZPUBLIC
        WHERE
            DISTVSP_0 = 2
            AND BPSREF_0 = :sup_code
        ORDER BY
            NomePub;
        """
        params = {'sup_code': supplier_code}

        try:
            df_pubs = db.run_query(query, params)

            if df_pubs.empty:
                logger.warning(f'Nenhuma publicação encontrada para o fornecedor {supplier_code}.')
                return {}
            else:
                # Cria o dicionário {Nome/Descrição: Codigo}
                publication_dict = pd.Series(df_pubs.CodigoPub.values, index=df_pubs.NomePub).to_dict()
                logger.info(f'Encontradas {len(publication_dict)} publicações para o fornecedor {supplier_code}.')
                return publication_dict
        except Exception as e:
            logger.error(f'Erro ao buscar publicações para o fornecedor {supplier_code}: {e}', exc_info=True)
            st.error(f'Erro ao carregar publicações do fornecedor: {e}')
            return {}
