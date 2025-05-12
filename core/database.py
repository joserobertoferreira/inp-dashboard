# core/database.py
import logging

import pandas as pd
import sqlalchemy as sa
import streamlit as st

from utils.generics import Generics

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_engine():
    """
    Create and return a SQLAlchemy engine for database connection.
    Cache the engine resource to avoid recreating it for every interaction for 1 hour.
    """
    try:
        config = st.secrets['database']
        driver_name = config['driver']

        # Check if the driver is compatible with the OS
        error_message, driver_name = Generics.check_odbc_driver(driver_name)

        if error_message:
            logger.error(error_message)
            st.error(error_message)
            return None

        # Build the connection string
        conn_str = sa.engine.URL.create(
            drivername='mssql+pyodbc',
            host=config['server'],
            database=config['database'],
            username=config.get('username'),
            password=config.get('password'),
            query={
                'driver': driver_name,
                # 'Encrypt': config['encrypt'],
                # "TrustServerCertificate": "yes",
                # "Trusted_Connection": config.get("trusted_connection", "no") # Se usar Windows Auth
            },
        )
        logger.info(f'String de conexão criada: {conn_str}')
        logger.info('Criando nova engine de conexão com o banco de dados.')
        engine = sa.create_engine(conn_str, fast_executemany=True)

        # Teste rápido de conexão (opcional mas recomendado)
        with engine.connect():
            logger.info('Conexão com o banco de dados estabelecida com sucesso.')
        return engine

    except KeyError as e:
        logger.error(f"Erro ao acessar segredos do banco: Chave '{e}' não encontrada em secrets.toml")
        st.error(f"Configuração do banco de dados incompleta. Verifique a chave '{e}' em .streamlit/secrets.toml.")
        return None
    except Exception as e:
        logger.error(f'Erro ao conectar ao banco de dados: {e}', exc_info=True)
        st.error(f'Não foi possível conectar ao banco de dados: {e}')
        return None


@st.cache_data(ttl=600)
def run_query(query: str, params: dict = None) -> pd.DataFrame:
    """
    Executes an SQL query on the database and returns the result as a Pandas DataFrame.
    This function caches the results for 10 minutes to improve performance.

    Args:
        query (str): The SQL query string to be executed.
        params (dict, optional): Dictionary of parameters for the query. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame with the query results or an empty DataFrame in case of an error.
    """
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()  # Retorna DF vazio se não há conexão

    logger.info(f'Executando query: {query[:100]}...')  # Log truncado da query
    try:
        with engine.connect() as connection:
            # Usar text() para queries parametrizadas com segurança (evita SQL Injection)
            sql_text = sa.text(query)
            df = pd.read_sql(sql_text, connection, params=params)
            logger.info(f'Query executada com sucesso. Retornadas {len(df)} linhas.')
            return df
    except Exception as e:
        logger.error(f'Erro ao executar query: {e}\nQuery: {query}\nParams: {params}', exc_info=True)
        st.error(f'Erro ao executar a consulta no banco de dados: {e}')
        return pd.DataFrame()  # Retorna DF vazio em caso de erro
