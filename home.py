import numpy as np
import pandas as pd
import streamlit as st

st.success(f'Bem-vindo, {st.session_state.user}!')
st.title('INP - Report Management System')
st.subheader('Home')
st.write('Welcome to the INP - Report Management System!')

st.header('1. Agrupamento Visual com MultiIndex (Pandas)')

# Criar dados de exemplo
data = {
    ('Vendas', 'Produto A'): np.random.randint(50, 100, 5),
    ('Vendas', 'Produto B'): np.random.randint(30, 80, 5),
    ('Marketing', 'Cliques'): np.random.randint(1000, 5000, 5),
    ('Marketing', 'Custo'): np.random.rand(5) * 100,
    ('Satisfação', 'Nota'): np.random.randint(1, 5, 5),
}
df_multi = pd.DataFrame(data)
df_multi.columns = pd.MultiIndex.from_tuples(list(data.keys()), names=['Categoria', 'Métrica'])

st.write('DataFrame com MultiIndex:')
st.dataframe(df_multi)

st.write('Com `st.table` (renderização mais simples):')
st.table(df_multi)
