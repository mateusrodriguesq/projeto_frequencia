import os
from datetime import datetime

import pandas as pd
import streamlit as st

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


if "page_configured" not in st.session_state:
    st.set_page_config(page_title="Frequência do Momento Áureo", layout="centered")
    st.session_state["page_configured"] = True

def design_login():
    """Define o layout da interface de login."""
    col1, col2 = st.columns(2)
    with col1:
        st.sidebar.image("data/dema.jpg", width=120)
    with col2:
        st.sidebar.header('📊 Frequência do Momento Áureo')
    st.sidebar.markdown("---")

def import_warning():
    df = pd.read_excel('data/segundas_feiras.xlsx')
    data_hoje = datetime.now()
    df['Datas'] = pd.to_datetime(df['Datas'], format='mixed', dayfirst=True)
    df_antes_hoje = df[df['Datas'] < data_hoje]  # antes
    df_depois_hoje = df[df['Datas'] > data_hoje]  # depois

    df_antes_hoje.loc[:, 'Datas'] = df_antes_hoje['Datas'].dt.strftime('%d/%m/%Y')
    df_depois_hoje.loc[:, 'Datas'] = df_depois_hoje['Datas'].dt.strftime('%d/%m/%Y')

    if data_hoje not in df['Datas'].values:
        st.sidebar.error('Lembrando que hoje não é um dia de Momento Áureo.')
    else:
        st.sidebar.success('Hoje é um dia de Momento Áureo! Registre abaixo as frequências.')

def frequencia_reg():
    if "page_configured" not in st.session_state:
        st.set_page_config(page_title="Registrar frequência reunião", layout="centered")
        st.session_state["page_configured"] = True
    option_freq = st.sidebar.selectbox('Selecione uma opção:',
                                  ['Selecione', '1⁰ Momento', '2⁰ Momento'])

    if option_freq == '1⁰ Momento':
        pri_momento()
    elif option_freq == '2⁰ Momento':
        sec_momento()


def pri_momento():
    st.title('Lançar Frequência - Corrente - 6h as 7h - 1º Momento')
    st.markdown("---")
    participantes = pd.read_excel('data/participantes_momentos.xlsx')
    participantes = participantes.sort_values(by='1_momento')
    for i, participante in participantes.iterrows():
        if pd.notna(participante['1_momento']):
            st.subheader(participante['1_momento'])
            st.write('Defina a presença abaixo:')
            colu1, colu2 = st.columns(2)
            with colu1:
                presente = st.checkbox('Presente', key=f'presente_{i}')
                if presente:
                    st.write('Defina o tipo de presença abaixo:')
                    coll1, coll2 = st.columns(2)
                    with coll1:
                        presencial_bool = st.checkbox('Presencial', key=f'presencial_{i}')
                    with coll2:
                        online_bool = st.checkbox('Online', key=f'online_{i}')
                    if presencial_bool and online_bool:
                        st.warning('Presencial e Online não podem ser selecionados juntos')
                    st.markdown("---")
            with colu2:
                ausente = st.checkbox('Ausente', key=f'ausente_{i}')
                if presente and ausente:
                    st.warning('Presença e ausência não podem ser selecionados juntos')
                st.markdown("---")
    enviar = st.sidebar.button('Enviar')
    if enviar:
        lista_2025 = pd.read_excel('data/lista_frequencia_ma.xlsx', sheet_name='2025')
        for i, participante in participantes.iterrows():
            if pd.notna(participante['1_momento']):
                nome = participante['1_momento']
                data_hoje = datetime.now().strftime('%d/%m/%Y')
                momento = 1
                if st.session_state.get(f'presente_{i}', False):
                    frequencia = 'Presente'
                    tipo_presenca = 'Presencial' if st.session_state.get(f'presencial_{i}', False) else 'Online'
                else:
                    frequencia = 'Ausente'
                    tipo_presenca = 'Ausente'
                new_row = pd.DataFrame([{'Data': data_hoje, 'Nome': nome, 'Momento': momento, 'Frequência': frequencia, 'Tipo de presença': tipo_presenca}])
                lista_2025 = pd.concat([lista_2025, new_row], ignore_index=True)
        lista_2025.to_excel('data/lista_frequencia_ma.xlsx', sheet_name='2025', index=False)
        st.sidebar.success('Frequência registrada com sucesso!')

def sec_momento():
    st.title('Lançar Frequência - Corrente - 7:15h as 8h - 2º Momento')
    st.markdown("---")
    participantes_2 = pd.read_excel('data/participantes_momentos.xlsx')
    participantes_2 = participantes_2.sort_values(by='2_momento')
    for j, participante in participantes_2.iterrows():
        if pd.notna(participante['2_momento']):
            st.subheader(participante['2_momento'])
            st.write('Defina a presença abaixo:')
            colu1, colu2 = st.columns(2)
            with colu1:
                presente = st.checkbox('Presente', key=f'presente_{j}')
                if presente:
                    st.write('Defina o tipo de presença abaixo:')
                    coll1, coll2 = st.columns(2)
                    with coll1:
                        presencial_bool = st.checkbox('Presencial', key=f'presencial_{j}')
                    with coll2:
                        online_bool = st.checkbox('Online', key=f'online_{j}')
                    if presencial_bool and online_bool:
                        st.warning('Presencial e Online não podem ser selecionados juntos')
                    st.markdown("---")
            with colu2:
                ausente = st.checkbox('Ausente', key=f'ausente_{j}')
                if presente and ausente:
                    st.warning('Presença e ausência não podem ser selecionados juntos')
                st.markdown("---")
    enviar = st.sidebar.button('Enviar')
    if enviar:
        lista_2025 = pd.read_excel('data/lista_frequencia_ma.xlsx', sheet_name='2025')
        for j, participante in participantes_2.iterrows():
            if pd.notna(participante['2_momento']):
                nome = participante['2_momento']
                data_hoje = datetime.now().strftime('%d/%m/%Y')
                momento = 2
                if st.session_state.get(f'presente_{j}', False):
                    frequencia = 'Presente'
                    tipo_presenca = 'Presencial' if st.session_state.get(f'presencial_{j}', False) else 'Online'
                else:
                    frequencia = 'Ausente'
                    tipo_presenca = 'Ausente'
                new_row = pd.DataFrame([{'Data': data_hoje, 'Nome': nome, 'Momento': momento, 'Frequência': frequencia, 'Tipo de presença': tipo_presenca}])
                lista_2025 = pd.concat([lista_2025, new_row], ignore_index=True)
        lista_2025.to_excel('data/lista_frequencia_ma.xlsx', sheet_name='2025', index=False)
        st.sidebar.success('Frequência registrada com sucesso!')

def login_text():
    st.title('Bem-vindo ao App de Frequência do Momento Áureo!')
    st.write('Este projeto tem como objetivo registrar a frequência do Momento Áureo.')

def analise_dados():
    st.title('Análise de dados de frequência')
    st.markdown("---")
    st.warning('Página em desenvolvimento')

def login():
    design_login()
    st.sidebar.title('Funções do App')
    import_warning()

    option = st.sidebar.selectbox('Selecione uma opção:',
                                  ['Selecione', 'Lançar frequência', 'Análise de dados de frequência'])

    if option == 'Selecione':
        login_text()
    elif option == 'Lançar frequência':
        frequencia_reg()
    elif option == 'Análise de dados de frequência':
        analise_dados()



login()
