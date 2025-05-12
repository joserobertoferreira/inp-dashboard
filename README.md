# Dashboard de Consultas SQL Server

Este projeto utiliza Streamlit para criar um dashboard interativo que exibe resultados de consultas em um banco de dados SQL Server legado.

## ✨ Funcionalidades Atuais

- **Comparativo de Vendas Anual:** Permite selecionar uma publicação e um ano, exibindo uma tabela comparativa das vendas por edição contra o ano anterior, incluindo totais, médias e variações.

## 🚀 Como Executar Localmente

1.  **Pré-requisitos:**

    - Python 3.8+
    - Pip (gerenciador de pacotes Python)
    - Acesso ao banco de dados SQL Server legado.
    - Driver ODBC para SQL Server instalado na sua máquina (ex: [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)).

2.  **Clone o Repositório:**

    ```bash
    git clone <url-do-seu-repositorio>
    cd seu_projeto_dashboard
    ```

3.  **Crie e Ative um Ambiente Virtual:** (Recomendado)

    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/macOS
    source venv/bin/activate
    ```

4.  **Instale as Dependências:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure as Credenciais do Banco:**

    - Crie o arquivo `.streamlit/secrets.toml` (se ainda não existir).
    - Copie o conteúdo do exemplo abaixo e preencha com suas credenciais **reais**.
    - **IMPORTANTE:** Não adicione este arquivo ao Git se ele contiver senhas reais. Adicione `.streamlit/secrets.toml` ao seu arquivo `.gitignore`.

    ```toml
    # .streamlit/secrets.toml (Exemplo)
    [database]
    driver = "{ODBC Driver 17 for SQL Server}" # Confirme o nome do seu driver
    server = "SEU_SERVIDOR"
    database = "SEU_BANCO_DE_DADOS"
    username = "SEU_USUARIO"
    password = "SUA_SENHA"
    # trusted_connection = "yes" # Se usar Autenticação Windows
    ```

6.  **Execute a Aplicação Streamlit:**

    ```bash
    streamlit run app.py
    ```

    A aplicação abrirá automaticamente no seu navegador padrão.

## 🏗️ Estrutura do Projeto
