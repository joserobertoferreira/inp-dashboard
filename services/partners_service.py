import logging

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from core.database import db
from models.partner import Partner

logger = logging.getLogger(__name__)


class PartnersService:
    """
    Service class for managing partners (customers and suppliers).

    Returns:
        - A dictionary containing the list of partners.
    """

    def __init__():
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
            st.error('Database connection is not established.')
            return {}

        logger.info('Buscando lista de fornecedores (Editores)...')
        query = f"""
        SELECT
            BPRNUM_0 AS CodigoFornecedor,
            BPRNAM_0 AS NomeFornecedor
        FROM
            {schema}.BPARTNER
        WHERE
            ZEDITOR_0 = 2 AND
            BPSFLG_0 = 2 AND
            EXISTS (SELECT 1 FROM {schema}.ZPUBLIC WHERE DISTVSP_0=2 AND BPSREF_0=BPARTNER.BPRNUM_0)
        ORDER BY
            NomeFornecedor;
        """

        try:
            df_suppliers = db.run_query(query)

            if df_suppliers.empty:
                logger.warning('Nenhum fornecedor (editor) encontrado')
                return {}
            else:
                # Cria o dicionário {NomeFornecedor: CodigoFornecedor}
                supplier_dict = pd.Series(
                    df_suppliers.CodigoFornecedor.values, index=df_suppliers.NomeFornecedor
                ).to_dict()
                logger.info(f'Encontrados {len(supplier_dict)} fornecedores.')
                return supplier_dict
        except Exception as e:
            logger.error(f'Erro ao buscar fornecedores: {e}', exc_info=True)
            st.error(f'Erro ao carregar a lista de fornecedores: {e}')
            return {}

    @staticmethod
    def fetch_suppliers() -> dict:
        if not db:
            st.error('Gerenciador do banco não disponível.')
            return {}

        logger.info('(Service ORM) Buscando fornecedores via ORM...')
        try:
            # Usa o context manager para a sessão ORM
            with db.get_db() as session:
                suppliers = (
                    session.query(Partner.bp.label('CodigoFornecedor'), Partner.partnerNames[0].label('NomeFornecedor'))
                    .filter(Partner.isSupplier == 2)  # noqa: PLR2004
                    .order_by(Partner.partnerNames[0], Partner.partnerNames[1])
                    .all()
                )

                if not suppliers:
                    logger.warning('Nenhum fornecedor encontrado (ORM).')
                    return {}

                supplier_dict = {s.NomeFornecedor: s.CodigoFornecedor for s in suppliers}
                logger.info(f'Encontrados {len(supplier_dict)} fornecedores (ORM).')
                return supplier_dict
        except SQLAlchemyError as e:
            st.error(f'Erro de banco de dados (ORM) ao buscar fornecedores: {e}')
            logger.error(f'Erro ORM ao buscar fornecedores: {e}', exc_info=True)
            return {}
        except Exception as e:  # Captura outras exceções, como ConnectionError se o db_manager for None
            st.error(f'Erro inesperado (ORM) ao buscar fornecedores: {e}')
            logger.error(f'Erro inesperado ORM ao buscar fornecedores: {e}', exc_info=True)
            return {}
