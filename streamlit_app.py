import os
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.express as px

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


if "page_configured" not in st.session_state:
    st.set_page_config(page_title="Frequência do Momento Áureo", layout="centered")
    st.session_state["page_configured"] = True

def design_login():
    """Define o layout da interface de login."""
    col1, col2 = st.columns(2)
    with col1:
        st.sidebar.image("data/dema.jpg", width=125)
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
    st.title('Lançar Frequência - Corrente - 6h às 7h - 1º Momento')
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
    st.sidebar.warning('Lembre-se de marcar a presença de todos os participantes antes de enviar.')
    enviar = st.sidebar.button('Enviar')

    if enviar:
        lista_2025 = pd.read_excel('data/lista_frequencia_ma.xlsx', sheet_name='2025')
        segundas_feiras = pd.read_excel('data/segundas_feiras.xlsx')
        datas_validas = set(segundas_feiras['Datas'].astype(str))

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

                data_correta = 'Sim' if data_hoje in datas_validas else 'Não'

                new_row = pd.DataFrame([{
                    'Data': data_hoje,
                    'Nome': nome,
                    'Momento': momento,
                    'Frequência': frequencia,
                    'Tipo de presença': tipo_presenca,
                    'Data Correta': data_correta
                }])

                lista_2025 = pd.concat([lista_2025, new_row], ignore_index=True)

        lista_2025.to_excel('data/lista_frequencia_ma.xlsx', sheet_name='2025', index=False)
        st.sidebar.success('Frequência registrada com sucesso!')


def sec_momento():
    st.title('Lançar Frequência - Corrente - 7:15h às 8h - 2º Momento')
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
    st.sidebar.warning('Lembre-se de marcar a presença de todos os participantes antes de enviar.')
    enviar = st.sidebar.button('Enviar')

    if enviar:
        lista_2025 = pd.read_excel('data/lista_frequencia_ma.xlsx', sheet_name='2025')
        segundas_feiras = pd.read_excel('data/segundas_feiras.xlsx')
        datas_validas = set(segundas_feiras['Datas'].astype(str))

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

                data_correta = 'Sim' if data_hoje in datas_validas else 'Não'

                new_row = pd.DataFrame([{
                    'Data': data_hoje,
                    'Nome': nome,
                    'Momento': momento,
                    'Frequência': frequencia,
                    'Tipo de presença': tipo_presenca,
                    'Data Correta': data_correta
                }])

                lista_2025 = pd.concat([lista_2025, new_row], ignore_index=True)

        lista_2025.to_excel('data/lista_frequencia_ma.xlsx', sheet_name='2025', index=False)
        st.sidebar.success('Frequência registrada com sucesso!')


def login_text():
    st.title('Bem-vindo ao App de Frequência do Momento Áureo!')
    st.write('Este projeto tem como objetivo registrar a frequência do Momento Áureo.')


def analise_dados():
    st.title("Análise de Dados de Frequência")
    st.markdown("---")

    # Carrega os dados históricos
    df = pd.read_excel('data/historico_22_23_24.xlsx', sheet_name='historico')

    # Converte a coluna 'Data' para datetime sem especificar o formato,
    # assim ambos os formatos (ex.: "2024-12-23 00:00:00" e "06/02/2025") serão interpretados.
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')

    # Padroniza a coluna 'Data' para o formato "dd/mm/YYYY"
    df['Data'] = df['Data'].dt.strftime('%d/%m/%Y')

    # Cria uma coluna auxiliar com a data em formato datetime para operações de agrupamento e filtros
    df['Data_dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')

    # Filtra para considerar somente os registros com 'Data Correta' = "Sim"
    df = df[df['Data Correta'] == "Sim"]

    if df.empty:
        st.warning("Não há dados com 'Data Correta' = Sim para análise.")
        return

    # Filtra os dados de 2024 para os indicadores anuais (usando a coluna auxiliar Data_dt)
    df_2024 = df[df['Data_dt'].dt.year == 2024]

    # Sidebar: seleção do modo de análise
    modo_analise = st.sidebar.selectbox(
        "Selecione o modo de análise:",
        ["Análise de todos participantes", "Filtrar por Nome"]
    )

    # Função para criar o gráfico de barras com o percentual de frequência por mês
    def plot_monthly_percentage(df_subset, momento_label):
        df_subset = df_subset.copy()
        # Usa a coluna auxiliar Data_dt para extrair o mês no formato "YYYY-MM"
        df_subset['Mes'] = df_subset['Data_dt'].dt.to_period('M').astype(str)
        # Conta quantos registros há por mês e por Frequência
        monthly_counts = df_subset.groupby(['Mes', 'Frequência']).size().reset_index(name='Count')
        # Conta o total de registros por mês
        monthly_totals = df_subset.groupby('Mes').size().reset_index(name='Total')
        # Junta os dados e calcula a porcentagem
        monthly = monthly_counts.merge(monthly_totals, on='Mes')
        monthly['Percent'] = monthly['Count'] / monthly['Total'] * 100
        fig = px.bar(
            monthly,
            x='Mes',
            y='Percent',
            color='Frequência',
            barmode='group',
            title=f"Percentual de Frequência por Mês ({momento_label})",
            labels={"Mes": "Mês", "Percent": "Percentual (%)"}
        )
        # Exibe o valor percentual em cima de cada coluna (duas casas decimais e %)
        fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        return fig

    # Função para criar o gráfico de distribuição do Tipo de Presença (ordenado do maior para o menor)
    def plot_tipo_presenca(df_subset, momento_label):
        # Agrupa e ordena os dados por 'Tipo de presença'
        df_tipo = df_subset.groupby('Tipo de presença').size().reset_index(name='Count')
        df_tipo = df_tipo.sort_values(by='Count', ascending=False)
        total = df_tipo['Count'].sum() if df_tipo['Count'].sum() != 0 else 1
        df_tipo['Percent'] = df_tipo['Count'] / total * 100
        fig = px.bar(
            df_tipo,
            x='Tipo de presença',
            y='Count',
            color='Tipo de presença',
            title=f"Distribuição de Tipo de Presença ({momento_label})",
            labels={"Count": "Quantidade"}
        )
        # Exibe o valor percentual em cima de cada barra (duas casas decimais e %)
        fig.update_traces(text=df_tipo['Percent'].apply(lambda x: f'{x:.2f}%'), textposition='outside')
        return fig

    if modo_analise == "Análise de todos participantes":
        st.header("Análise de todos participantes")

        # Cria três abas: 1º Momento, 2º Momento e Indicadores Anuais 2024
        tab1, tab2, tab3 = st.tabs(["1º Momento", "2º Momento", "Indicadores 2024"])

        # --- Aba: 1º Momento ---
        with tab1:
            df_m1 = df[df['Momento'] == 1]
            if df_m1.empty:
                st.info("Não há registros para o 1º Momento.")
            else:
                st.subheader("Percentual de Frequência por Mês")
                fig_monthly_m1 = plot_monthly_percentage(df_m1, "1º Momento")
                st.plotly_chart(fig_monthly_m1, use_container_width=True)

                st.subheader("Distribuição de Tipo de Presença")
                fig_tipo_m1 = plot_tipo_presenca(df_m1, "1º Momento")
                st.plotly_chart(fig_tipo_m1, use_container_width=True)

        # --- Aba: 2º Momento ---
        with tab2:
            df_m2 = df[df['Momento'] == 2]
            if df_m2.empty:
                st.info("Não há registros para o 2º Momento.")
            else:
                st.subheader("Percentual de Frequência por Mês")
                fig_monthly_m2 = plot_monthly_percentage(df_m2, "2º Momento")
                st.plotly_chart(fig_monthly_m2, use_container_width=True)

                st.subheader("Distribuição de Tipo de Presença")
                fig_tipo_m2 = plot_tipo_presenca(df_m2, "2º Momento")
                st.plotly_chart(fig_tipo_m2, use_container_width=True)

        # --- Aba: Indicadores Anuais 2024 ---
        with tab3:
            st.subheader("Indicadores Anuais - 2024")
            if df_2024.empty:
                st.info("Não há registros para o ano de 2024.")
            else:
                total_2024 = df_2024.shape[0]
                presentes_2024 = df_2024[df_2024['Frequência'] == "Presente"].shape[0]
                percentual_presenca_2024 = round(presentes_2024 / total_2024 * 100, 2)
                st.metric("Percentual de Presença (2024)", f"{percentual_presenca_2024}%")

                # Percentual por Momento
                df_2024_m1 = df_2024[df_2024['Momento'] == 1]
                df_2024_m2 = df_2024[df_2024['Momento'] == 2]
                if not df_2024_m1.empty:
                    pres_m1 = df_2024_m1[df_2024_m1['Frequência'] == "Presente"].shape[0]
                    perc_m1 = round(pres_m1 / df_2024_m1.shape[0] * 100, 2)
                    st.metric("Presença 2024 - 1º Momento", f"{perc_m1}%")
                if not df_2024_m2.empty:
                    pres_m2 = df_2024_m2[df_2024_m2['Frequência'] == "Presente"].shape[0]
                    perc_m2 = round(pres_m2 / df_2024_m2.shape[0] * 100, 2)
                    st.metric("Presença 2024 - 2º Momento", f"{perc_m2}%")

                st.markdown("### Distribuição do Tipo de Presença (Presencial vs Online) - 2024")
                df_pres_2024 = df_2024[df_2024['Frequência'] == "Presente"]
                if df_pres_2024.empty:
                    st.info("Não há registros de 'Presente' para análise do tipo de presença em 2024.")
                else:
                    df_tipo_2024 = df_pres_2024.groupby('Tipo de presença').size().reset_index(name='Count')
                    df_tipo_2024 = df_tipo_2024.sort_values(by='Count', ascending=False)
                    fig_pie = px.pie(
                        df_tipo_2024,
                        names='Tipo de presença',
                        values='Count',
                        title="Distribuição de Tipo de Presença (2024)",
                        hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

    elif modo_analise == "Filtrar por Nome":
        # Sidebar: seleção do Nome
        nomes = sorted(df['Nome'].dropna().unique().tolist())
        nome_selecionado = st.sidebar.selectbox("Selecione o Nome:", nomes)

        df_nome = df[df['Nome'] == nome_selecionado]
        if df_nome.empty:
            st.info("Nenhum registro para este nome.")
        else:
            st.header(f"Análise para {nome_selecionado}")
            # Cria três abas: 1º Momento, 2º Momento e Indicadores Anuais 2024 para o Nome
            tab1, tab2, tab3 = st.tabs(["1º Momento", "2º Momento", "Indicadores 2024"])

            # --- Aba: 1º Momento ---
            with tab1:
                df_nome_m1 = df_nome[df_nome['Momento'] == 1]
                if df_nome_m1.empty:
                    st.info("Não há registros para o 1º Momento.")
                else:
                    st.subheader("Percentual de Frequência por Mês")
                    fig_monthly_nome_m1 = plot_monthly_percentage(df_nome_m1, "1º Momento")
                    st.plotly_chart(fig_monthly_nome_m1, use_container_width=True)

                    st.subheader("Distribuição de Tipo de Presença")
                    fig_tipo_nome_m1 = plot_tipo_presenca(df_nome_m1, "1º Momento")
                    st.plotly_chart(fig_tipo_nome_m1, use_container_width=True)

            # --- Aba: 2º Momento ---
            with tab2:
                df_nome_m2 = df_nome[df_nome['Momento'] == 2]
                if df_nome_m2.empty:
                    st.info("Não há registros para o 2º Momento.")
                else:
                    st.subheader("Percentual de Frequência por Mês")
                    fig_monthly_nome_m2 = plot_monthly_percentage(df_nome_m2, "2º Momento")
                    st.plotly_chart(fig_monthly_nome_m2, use_container_width=True)

                    st.subheader("Distribuição de Tipo de Presença")
                    fig_tipo_nome_m2 = plot_tipo_presenca(df_nome_m2, "2º Momento")
                    st.plotly_chart(fig_tipo_nome_m2, use_container_width=True)

            # --- Aba: Indicadores Anuais 2024 para o Nome ---
            with tab3:
                st.subheader("Indicadores Anuais - 2024")
                df_nome_2024 = df_nome[df_nome['Data_dt'].dt.year == 2024]
                if df_nome_2024.empty:
                    st.info("Não há registros para 2024 para este nome.")
                else:
                    total = df_nome_2024.shape[0]
                    presentes = df_nome_2024[df_nome_2024['Frequência'] == "Presente"].shape[0]
                    percentual = round(presentes / total * 100, 2)
                    st.metric("Percentual de Presença (2024)", f"{percentual}%")

                    st.markdown("### Distribuição do Tipo de Presença (Presencial vs Online)")
                    df_tipo_nome_2024 = df_nome_2024[df_nome_2024['Frequência'] == "Presente"].groupby(
                        'Tipo de presença').size().reset_index(name='Count')
                    df_tipo_nome_2024 = df_tipo_nome_2024.sort_values(by='Count', ascending=False)
                    if df_tipo_nome_2024.empty:
                        st.info("Não há registros de 'Presente' para este nome em 2024.")
                    else:
                        fig_pie_nome = px.pie(
                            df_tipo_nome_2024,
                            names='Tipo de presença',
                            values='Count',
                            title="Distribuição de Tipo de Presença (2024)",
                            hole=0.4
                        )
                        st.plotly_chart(fig_pie_nome, use_container_width=True)


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
