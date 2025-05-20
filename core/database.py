import logging
from contextlib import contextmanager
from typing import Generator, Optional

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from utils.generics import Generics

# Configurar logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database session manager."""

    def __init__(self, url: str, echo: bool = False):
        """Initialize the database session manager."""
        self.engine = create_engine(url, echo=echo)
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
        )

    # close connection
    def close(self):
        """Dispose of the engine connections."""
        if self.engine:
            self.engine.dispose()
            logger.info('Database engine disposed.')

    @contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """Provides a database session within a context."""
        if not self.SessionLocal:
            logger.error('SessionLocal is not initialized.')
            raise RuntimeError('Erro ao conectar ao banco de dados. Verifique os logs.')

        db_session: Optional[Session] = None
        try:
            db_session = self.SessionLocal()
            logger.debug(f'Sessão de banco de dados {id(db_session)} criada e sendo fornecida.')
            yield db_session
        except Exception as e:  # Captura exceções dentro do bloco 'with' que usa esta sessão
            logger.error(f'Exceção dentro do contexto da sessão de banco de dados {id(db_session)}: {e}', exc_info=True)
            raise
        finally:
            if db_session:
                logger.debug(f'Fechando sessão de banco de dados {id(db_session)}.')
                db_session.close()

    def commit_rollback(self, session: Session):  # noqa: PLR6301
        """Commits the session or rolls back in case of an error."""
        try:
            session.commit()
            logger.debug('Session committed successfully.')
        except Exception as e:
            session.rollback()
            logger.error(f'Session rollback due to error: {e}', exc_info=True)
            raise

    def run_query(self, query: str, params: Optional[dict] = None) -> pd.DataFrame:
        """
        Executes an SQL query on the database and returns the result as a Pandas DataFrame.
        This function caches the results for 10 minutes to improve performance.

        Args:
            query (str): The SQL query string to be executed.
            params (dict, optional): Dictionary of parameters for the query. Defaults to None.

        Returns:
            pd.DataFrame: DataFrame with the query results or an empty DataFrame in case of an error.
        """
        if not self.engine:
            logger.error('Database engine is not initialized.')
            st.error('Erro ao conectar ao banco de dados. Verifique os logs.')
            return pd.DataFrame()

        logger.debug(f'Executing Core query: {query} with params: {params}')
        logger.info(f'Executando query: {query[:50]}...')  # Log truncado da query

        try:
            with self.engine.connect() as connection:
                # Usar text() para queries parametrizadas com segurança (evita SQL Injection)
                sql_text = connection.execute(text(query), params if params else {})
                df = pd.DataFrame(sql_text.fetchall(), columns=sql_text.keys())  # type: ignore
                logger.info(f'Query executada com sucesso. Retornadas {len(df)} linhas.')
                return df
        except SQLAlchemyError as e:
            logger.error(f'Erro ao executar query com SQLAlchemy Core: {e}', exc_info=True)
            st.error(f'Erro de banco de dados ao executar a query (Core): {e}')
            return pd.DataFrame()
        except Exception as e:
            logger.error(f'Erro inesperado ao executar query (Core): {e}', exc_info=True)
            st.error(f'Erro inesperado durante a consulta ao banco (Core): {e}')
            return pd.DataFrame()


# Initialize the database session manager
db = None

DB_CONNECTION_STRING = Generics().build_connection_string(config=st.secrets['database'])

if DB_CONNECTION_STRING:
    try:
        # Passe echo=True para ver as queries SQL geradas, False para produção
        db = DatabaseManager(url=DB_CONNECTION_STRING, echo=True)  # type: ignore
        logger.info('DatabaseSessionManager initialized successfully.')
    except ValueError as ve:  # Erro específico da nossa validação de URL
        logger.error(f'Configuration Error: {ve}')
        st.error(f'Erro de Configuração do Banco: {ve}')
    except SQLAlchemyError as sa_err:  # Erros da criação do engine
        logger.error(f'SQLAlchemy Engine Creation Error: {sa_err}', exc_info=True)
        st.error(f'Erro ao conectar ao banco (Engine): {sa_err}')
    except Exception as e:  # Outros erros inesperados
        logger.error(f'Unexpected error initializing DatabaseSessionManager: {e}', exc_info=True)
        st.error(f'Erro inesperado na inicialização do banco: {e}')
else:
    # Mensagem de erro já emitida se DB_CONNECTION_STRING não pôde ser construído
    st.error('Configuração do banco de dados ausente ou incompleta em st.secrets. Verifique os logs.')
