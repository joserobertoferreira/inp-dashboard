import logging

from pwdlib import PasswordHash

from services.user_service import UserService

logger = logging.getLogger(__name__)


class AuthenticationService:
    """
    Authentication service for handling user login and registration.
    """

    # Password hashing context
    pwd_context = PasswordHash.recommended()

    @staticmethod
    def login(username: str, password: str) -> dict[str, str]:
        """
        Authenticates a user by checking the username and password.
        :param username: Username of the user
        :param password: Password of the user
        :return: A dictionary containing user information if authentication is successful
        """

        result = {}

        return_user = UserService.get_by_username_email(username.upper(), None)

        if not return_user:
            logger.warning(f'User {username} not found during login attempt.')
        else:
            logger.info(f'User {return_user.get("username")} found in database.')

            db_password = str(return_user.get('password', '')).strip()
            user_id_str = return_user.get('id', None)
            user_id = int(user_id_str) if user_id_str else None
            password_ok = False

            if len(db_password) == 0:
                logger.warning(f'User {username} has no password set.')

                hash = AuthenticationService.pwd_context.hash(password)

                try:
                    if user_id is not None:
                        if UserService.set_user_password(user_id=user_id, new_password_hash=hash):
                            logger.info(f'Password set for user {username}.')
                            return_user.pop('password', None)
                            result = return_user
                        else:
                            logger.error(f'Failed to set password for user {username}.')
                    else:
                        logger.error(f'User {username} has no id set.')
                except Exception as e:
                    logger.error(f'Error updating user {username}: {e}')
            else:
                password_ok = AuthenticationService.pwd_context.verify(password, db_password)
                if password_ok:
                    return_user.pop('password', None)
                    result = return_user

        return result

    # @staticmethod
    # def register(db_session: Session, register_data: RegisterInput):
    #     """
    #     Registers a new user in the system.
    #     :param db_session: Database session
    #     :param register_data: Registration data containing username, email, and password
    #     :return: UserType object containing user information
    #     """
    #     # Check if username or email already exists
    #     user_exists = UserRepository.get_by_username_email(db_session, register_data.username, register_data.email)

    #     if user_exists:
    #         raise ValueError('Username or email already exists')

    #     # Check if password is valid and strong enough
    #     if not register_data.password:
    #         raise ValueError('Password is required')

    #     validator = PasswordValidatorService()

    #     is_valid, warning = validator.validate_username(register_data.username)

    #     if not is_valid:
    #         raise PasswordValidationError(
    #             message='Username does not meet complexity requirements',
    #             field=warning,
    #         )

    #     if validator.is_password_similar_to_username(password=register_data.password, username=register_data.username):
    #         raise ValueError('Password is too similar to username')

    #     is_valid, suggestions, warning = validator.validate_password(register_data.password)

    #     if not is_valid:
    #         raise PasswordValidationError(
    #             message='Password does not meet complexity requirements',
    #             field=suggestions,
    #             details=warning,
    #         )

    #     user = User()
    #     user.username = register_data.username
    #     user.email = register_data.email
    #     user.is_active = register_data.is_active
    #     user.is_superuser = False
    #     user.date_joined = datetime.date.today()
    #     user.last_login = settings.DEFAULT_LEGACY_DATETIME
    #     user.password = AuthenticationService.pwd_context.hash(register_data.password)

    #     new_user = UserRepository.create_user(db, user)

    #     return UserType(
    #         user_id=new_user.id,
    #         username=new_user.username,
    #         email=new_user.email,
    #         date_joined=new_user.date_joined,
    #         last_login=new_user.last_login,
    #         is_active=new_user.is_active,
    #         is_superuser=new_user.is_superuser,
    #     )
