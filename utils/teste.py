from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def test_sqlalchemy():
    # Configurações do banco de dados
    username = 'MINP'  # substitua pelo seu usuário
    password = 'on-2022'  # substitua pela sua senha
    host = '10.19.69.36\\SAGEX3'  # substitua pelo host (ex: localhost ou endereço IP)
    database = 'x3v12db'  # substitua pelo nome do seu banco de dados

    # String de conexão com o SQL Server
    connection_string = f'mssql+pyodbc://{username}:{password}@{host}/{database}?driver=ODBC+Driver+17+for+SQL+Server'

    # Cria a engine de conexão
    engine = create_engine(connection_string)

    # Cria uma sessão
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Conectando ao banco e executando um SELECT simples
        with engine.connect() as connection:
            result = connection.execute(
                text('SELECT TOP 5 USR_0,NOMUSR_0 FROM MINP.AUTILIS WHERE ENAFLG_0=2')
            )  # Substitua 'sua_tabela' pelo nome de uma tabela válida
            for row in result:
                print(row)  # Imprime os dados da tabela
    except Exception as e:
        print(f'Erro na conexão ou execução da query: {e}')
    finally:
        session.close()
