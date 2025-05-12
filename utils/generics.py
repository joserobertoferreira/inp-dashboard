import platform


class Generics:
    def __init__(self):
        pass

    @staticmethod
    def check_odbc_driver(driver_name):
        """
        Verifica se o driver ODBC é suportado no sistema operacional atual.
        :param driver_name: Nome do driver ODBC a ser verificado.
        :return: None se o driver for suportado, ou uma mensagem de erro se não for.
        """
        os_name = platform.system()
        error_message = None
        supported_drivers = {'ODBC Driver 17 for SQL Server', 'ODBC Driver 18 for SQL Server'}

        if os_name == 'Windows':
            if driver_name not in supported_drivers:
                error_message = f"Driver '{driver_name}' não é suportado no Windows."
            else:
                driver_name = driver_name.replace(' ', '+')
        elif os_name == 'Linux' and driver_name not in supported_drivers:
            error_message = f"Driver '{driver_name}' não é suportado no Linux."
        elif os_name == 'Darwin' and driver_name not in supported_drivers:
            error_message = f"Driver '{driver_name}' não é suportado no macOS."
        elif os_name not in {'Windows', 'Linux', 'Darwin'}:
            error_message = f"Sistema operacional '{os_name}' não suportado."

        return error_message, driver_name
