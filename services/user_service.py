import logging
from typing import Optional

import streamlit as st
from sqlalchemy import update as sql_update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select

from core.database import db
from models.users import Users

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for managing users.
    """

    def __init__(self):
        pass

    @staticmethod
    def fetch_users_for_auth() -> dict:
        """
        Fetches users from the database formatted for streamlit-authenticator.
        Uses USR_0 as username, NOMUSR_0 as name, and PASSE_0 as password.
        Returns:
            dict: A dictionary suitable for the 'credentials' -> 'usernames' section
                  of streamlit-authenticator's config.
        """
        if not db:
            logger.error('Database connection is not established.')
            st.error('Gerenciador do banco não disponível.')
            return {}

        logger.info('(Service ORM) Buscando fornecedores via ORM...')
        try:
            # Usa o context manager para a sessão ORM
            with db.get_db() as session:
                users = (
                    session.query(
                        Users.username.label('username'), Users.name.label('name'), Users.password.label('password')
                    )
                    .filter(Users.ENAFLG_0 == 2)  # noqa: PLR2004
                    .order_by(Users.username)
                    .all()
                )

                if not users:
                    logger.warning('Nenhum utilizador encontrado (ORM).')
                    return {}

                user_dict = {u.username: {'name': u.name, 'password': u.password} for u in users}
                logger.info(f'Encontrados {len(user_dict)} utilizadores (ORM).')
                return user_dict
        except SQLAlchemyError as e:
            st.error(f'Erro de banco de dados (ORM) ao buscar utilizadores: {e}')
            logger.error(f'Erro ORM ao buscar utilizadores: {e}', exc_info=True)
            return {}
        except Exception as e:  # Captura outras exceções, como ConnectionError se o db_manager for None
            st.error(f'Erro inesperado (ORM) ao buscar utilizadores: {e}')
            logger.error(f'Erro inesperado ORM ao buscar utilizadores: {e}', exc_info=True)
            return {}

    @staticmethod
    def update(user_id: int, user_data: dict) -> None:
        """
        Update user data in the database.
        :param user_id: ID of the user to update
        :param user_data_changes: Dictionary of {column_name: value} to update
        """

        if not db:
            st.error('Gerenciador do banco não disponível.')
            return

        if not user_data:
            logger.warning('No data provided for update.')
            return

        with db.get_db() as session:
            try:
                query = (
                    sql_update(Users)
                    .where(Users.id == user_id)
                    .values(**user_data)
                    .execution_options(synchronize_session='fetch')
                )

                result = session.execute(query)
                if result.rowcount == 0:
                    logger.warning(f'User with ID {user_id} not found or no changes made.')

                db.commit_rollback(session)
            except SQLAlchemyError as e:
                # db.commit_rollback(session, success=False) ou session.rollback()
                session.rollback()
                st.error(f'Erro de banco de dados (ORM) ao atualizar utilizador {user_id}: {e}')
                logger.error(f'Erro ORM ao atualizar utilizador {user_id}: {e}', exc_info=True)
            except Exception as e:
                session.rollback()
                st.error(f'Erro inesperado (ORM) ao atualizar utilizador {user_id}: {e}')
                logger.error(f'Erro inesperado ORM ao atualizar utilizador {user_id}: {e}', exc_info=True)

    @staticmethod
    def set_user_password(user_id: int, new_password_hash: str) -> bool:
        """
        Sets or updates the user's password hash in the database.
        :param user_id: ID of the user.
        :param new_password_hash: The new hashed password.
        :return: True if successful, False otherwise.
        """
        if not db:
            st.error('Gerenciador do banco não disponível.')
            logger.error('Database manager not available for password update.')
            return False

        logger.info(f'Attempting to set password for user_id: {user_id}')
        with db.get_db() as session:
            try:
                user_to_update = session.get(Users, user_id)
                if user_to_update:
                    user_to_update.password = new_password_hash
                    session.commit()
                    logger.info(f'Password updated successfully for user_id: {user_id}')
                    return True
                else:
                    logger.warning(f'User with ID {user_id} not found for password update.')
                    return False
            except SQLAlchemyError as e:
                session.rollback()
                st.error(f'Erro de banco de dados (ORM) ao atualizar senha do utilizador {user_id}: {e}')
                logger.error(f'Erro ORM ao atualizar senha do utilizador {user_id}: {e}', exc_info=True)
                return False
            except Exception as e:
                session.rollback()
                st.error(f'Erro inesperado (ORM) ao atualizar senha do utilizador {user_id}: {e}')
                logger.error(f'Erro inesperado ORM ao atualizar senha do utilizador {user_id}: {e}', exc_info=True)
                return False

    @staticmethod
    def get_by_username_email(username: Optional[str], email: Optional[str]) -> dict[str, str]:
        """fetch user by username or email"""

        user = {}

        if not db:
            st.error('Gerenciador do banco não disponível.')
            return user

        logger.info(f'(Service ORM) Autenticando utilizador {username} via ORM...')
        try:
            with db.get_db() as session:
                if username is not None and email is not None:
                    result = (
                        session.query(Users.id, Users.username, Users.name, Users.email, Users.password)
                        .filter(Users.ENAFLG_0 == 2, Users.username == username, Users.email == email)  # noqa: PLR2004
                        .first()
                    )  # noqa: PLR2004
                elif username is not None:
                    result = (
                        session.query(Users.id, Users.username, Users.name, Users.email, Users.password)
                        .filter(Users.ENAFLG_0 == 2, Users.username == username)  # noqa: PLR2004
                        .first()
                    )  # noqa: PLR2004
                elif email is not None:
                    result = (
                        session.query(Users.id, Users.username, Users.name, Users.email, Users.password)
                        .filter(Users.ENAFLG_0 == 2, Users.email == email)  # noqa: PLR2004
                        .first()
                    )

                if result is not None:
                    user = dict(result._asdict())
        except SQLAlchemyError as e:
            st.error(f'Erro de banco de dados (ORM) ao autenticar utilizador {username}: {e}')
            logger.error(f'Erro ORM ao autenticar utilizador {username}: {e}', exc_info=True)
        except Exception as e:  # Captura outras exceções, como ConnectionError se o db_manager for None
            st.error(f'Erro inesperado (ORM) ao buscar utilizador {username}: {e}')
            logger.error(f'Erro inesperado ORM ao buscar utilizador {username}: {e}', exc_info=True)

        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Users]:
        """fetch user by id"""

        logger.info(f'(Service ORM) Buscando utilizador {user_id} via ORM...')
        try:
            with db.get_db() as session:
                stmt = select(Users).where(Users.id == user_id)
                result = session.execute(stmt)
                user = result.scalars().first()
                return user
        except SQLAlchemyError as e:
            st.error(f'Erro de banco de dados (ORM) ao buscar utilizador {user_id}: {e}')
            logger.error(f'Erro ORM ao buscar utilizador {user_id}: {e}', exc_info=True)
        except Exception as e:
            st.error(f'Erro inesperado (ORM) ao buscar utilizador {user_id}: {e}')
            logger.error(f'Erro inesperado ORM ao buscar utilizador {user_id}: {e}', exc_info=True)
