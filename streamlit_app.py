import os
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import calendar
from pathlib import Path

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Configurar diretórios
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(DATA_DIR, 'capas')

# Criar diretórios necessários
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_dados_frequencia():
    """
    Carrega os dados de frequência usando Pandas.
    """
    try:
        # Usar pandas para ler o arquivo xlsx
        df = pd.read_excel(os.path.join(DATA_DIR, 'lista_frequencia_ma.xlsx'), engine='openpyxl')
        
        if df.empty:
            print("Aviso: Nenhum dado encontrado no arquivo de frequência")
            return pd.DataFrame()
            
        return df
    except Exception as e:
        print(f"Erro ao carregar dados de frequência: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def carregar_participantes():
    """
    Carrega a lista de participantes usando Pandas.
    """
    try:
        return pd.read_excel(os.path.join(DATA_DIR, 'participantes_momentos.xlsx'))
    except Exception as e:
        print(f"Erro ao carregar lista de participantes: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_segundas_feiras():
    """
    Carrega a lista de segundas-feiras do Excel.
    """
    try:
        # Carregar o arquivo Excel
        df = pd.read_excel(os.path.join(DATA_DIR, 'segundas_feiras.xlsx'))
        
        # Converter a coluna de datas para datetime
        df['Datas'] = pd.to_datetime(df['Datas'], format='%d/%m/%y')
        
        return df
        
    except Exception as e:
        print(f"Erro ao carregar segundas-feiras: {str(e)}")
        return pd.DataFrame()

def salvar_frequencia(data_registro, momento, df_freq):
    """
    Salva os dados de frequência usando Pandas.
    """
    try:
        # Carregar dados existentes
        df_atual = carregar_dados_frequencia()
        
        # Carregar segundas-feiras para validação
        segundas = carregar_segundas_feiras()
        
        # Converter a data de registro para o formato dd/mm/yy
        data_registro_dt = datetime.strptime(data_registro, '%d/%m/%Y')
        data_registro_curta = data_registro_dt.strftime('%d/%m/%y')
        
        # Adicionar colunas necessárias ao DataFrame
        df_novos = df_freq.copy()
        df_novos['Data'] = data_registro  # Mantém o formato original dd/mm/yyyy no DataFrame
        
        # Converter momento para número
        momento_num = 1 if momento == '1º Momento' else 2
        df_novos['Momento'] = momento_num
        
        # Validar apenas se a data está na lista de segundas (usando formato curto)
        df_novos['Data Correta'] = 'Sim' if data_registro_curta in segundas['Datas'].dt.strftime('%d/%m/%y').values else 'Não'
        
        # Concatenar com dados existentes
        df_final = pd.concat([df_atual, df_novos])
        
        # Salvar de volta para Excel
        df_final.to_excel(os.path.join(DATA_DIR, 'lista_frequencia_ma.xlsx'), sheet_name='2025', index=False)
        
        # Limpar cache para forçar recarregamento dos dados
        carregar_dados_frequencia.clear()
        
        st.sidebar.success('Frequência registrada com sucesso!')
            
    except Exception as e:
        st.error(f"Erro ao salvar frequência: {str(e)}")

def create_monthly_percentage_chart(df_subset, momento_label):
    """
    Cria um gráfico de barras empilhadas mostrando o percentual de frequência por mês.
    """
    try:
        # Criar uma cópia do DataFrame para evitar SettingWithCopyWarning
        df = df_subset.copy()
        
        # Converter a coluna de data para datetime se ainda não estiver
        if not pd.api.types.is_datetime64_any_dtype(df['Data']):
            df['Data'] = pd.to_datetime(df['Data'])
        
        # Criar coluna de Mês/Ano
        df['Mês/Ano'] = df['Data'].dt.strftime('%m/%Y')
        
        # Calcular percentuais por mês
        monthly_stats = df.groupby('Mês/Ano').agg({
            'Frequência': lambda x: (x == 'Presente').mean() * 100
        }).round(1)
        
        # Ordenar os meses
        monthly_stats = monthly_stats.reindex(sorted(monthly_stats.index))
        
        # Calcular percentual de ausência
        monthly_stats['Ausência'] = 100 - monthly_stats['Frequência']
        
        # Criar figura
        fig = go.Figure()
        
        # Adicionar barra de presença
        fig.add_trace(go.Bar(
            name='Presente',
            x=monthly_stats.index,
            y=monthly_stats['Frequência'],
            marker_color='#2E8B57',  # Verde
            text=[f'<b>{val}%</b>' for val in monthly_stats['Frequência']],
            textposition='auto',
            hovertemplate='Mês/Ano: %{x}<br>Presença: %{y:.1f}%<extra></extra>'
        ))
        
        # Adicionar barra de ausência
        fig.add_trace(go.Bar(
            name='Ausente',
            x=monthly_stats.index,
            y=monthly_stats['Ausência'],
            marker_color='#FF4B4B',  # Vermelho
            text=[f'<b>{val}%</b>' for val in monthly_stats['Ausência']],
            textposition='auto',
            hovertemplate='Mês/Ano: %{x}<br>Ausência: %{y:.1f}%<extra></extra>'
        ))
        
        # Atualizar layout
        fig.update_layout(
            title=dict(
                text=f'Percentual de Frequência por Mês - {momento_label}',
                font=dict(size=20, family="Arial Black")
            ),
            barmode='stack',
            xaxis=dict(
                title="",
                tickfont=dict(family="Arial", size=12),
                tickangle=90,  # Texto na vertical
                tickmode='array',
                ticktext=[f'<b>{x}</b>' for x in monthly_stats.index],
                tickvals=monthly_stats.index
            ),
            yaxis=dict(
                title=dict(
                    text="Percentual (%)",
                    font=dict(size=14, family="Arial")
                ),
                tickfont=dict(family="Arial", size=12),
                tickformat='.1f',
                ticksuffix='%',
                range=[0, 100]
            ),
            font=dict(family="Arial", size=12),
            height=400,
            plot_bgcolor='#F5F5DC',  # Fundo bege
            paper_bgcolor='white',
            bargap=0.2,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {str(e)}")
        return None

def plot_presence_type_distribution(df_subset, momento_label):
    """
    Cria um gráfico de barras mostrando a distribuição dos tipos de presença.
    """
    try:
        # Criar uma cópia do DataFrame para evitar SettingWithCopyWarning
        df = df_subset.copy()
        
        # Definir ordem desejada dos tipos de presença
        ordem_tipos = ['Presencial', 'Online', 'Ausente']
        
        # Calcular a contagem e percentual de cada tipo de presença
        presence_counts = df['Tipo de presença'].value_counts().reindex(ordem_tipos).fillna(0)
        total = presence_counts.sum()
        presence_percentages = (presence_counts / total * 100).round(1)
        
        # Definir cores para cada tipo de presença
        color_map = {
            'Presencial': '#2E8B57',  # Verde
            'Online': '#4682B4',      # Azul
            'Ausente': '#FF4B4B'      # Vermelho
        }
        
        # Criar lista de cores na ordem dos dados
        colors = [color_map[tipo] for tipo in ordem_tipos]
        
        # Criar gráfico
        fig = go.Figure()
        
        # Adicionar barras com percentuais
        fig.add_trace(go.Bar(
            x=ordem_tipos,
            y=presence_percentages,
            text=[f'<b>{val}%</b>' for val in presence_percentages],
            textposition='auto',
            marker_color=colors,
            hovertemplate='%{x}<br>Percentual: %{y:.1f}%<br>Quantidade: %{customdata} registros<extra></extra>',
            customdata=presence_counts.values,
            showlegend=False
        ))
        
        fig.update_layout(
            title=dict(
                text=f'Distribuição de Tipo de Presença - {momento_label}',
                font=dict(size=20, family="Arial Black")
            ),
            xaxis=dict(
                title="",
                ticktext=[
                    f'<span style="color: {color_map["Presencial"]}"><b>Presencial</b></span>',
                    f'<span style="color: {color_map["Online"]}"><b>Online</b></span>',
                    f'<span style="color: {color_map["Ausente"]}"><b>Ausente</b></span>'
                ],
                tickvals=ordem_tipos,
                tickfont=dict(family="Arial", size=12),
                tickangle=90  # Texto na vertical
            ),
            yaxis=dict(
                title=dict(
                    text="Percentual (%)",
                    font=dict(size=14, family="Arial")
                ),
                tickfont=dict(family="Arial", size=12),
                tickformat='.1f',
                ticksuffix='%'
            ),
            font=dict(family="Arial", size=12),
            height=400,
            plot_bgcolor='#F5F5DC',  # Fundo bege
            paper_bgcolor='white',
            bargap=0.2,
            margin=dict(t=100, b=50)  # Ajustar margens
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {str(e)}")
        return None

def create_pie_chart(df_subset, momento_label):
    """
    Cria um gráfico de pizza mostrando a distribuição dos tipos de presença.
    """
    try:
        # Criar uma cópia do DataFrame para evitar SettingWithCopyWarning
        df = df_subset.copy()
        
        # Calcular contagem por tipo de presença
        tipo_presenca_counts = df['Tipo de presença'].value_counts()
        total = tipo_presenca_counts.sum()
        tipo_presenca_percentual = (tipo_presenca_counts / total * 100).round(1)
        
        # Definir cores para cada tipo de presença
        color_map = {
            'Presencial': '#2E8B57',  # Verde
            'Online': '#4682B4',      # Azul
            'Ausente': '#FF4B4B'      # Vermelho
        }
        
        # Criar lista de cores na ordem dos dados
        colors = [color_map.get(tipo, '#808080') for tipo in tipo_presenca_counts.index]
        
        # Criar texto personalizado para o hover
        hover_text = [
            f'{tipo}<br>Percentual: {pct:.1f}%<br>Quantidade: {count} registros'
            for tipo, pct, count in zip(
                tipo_presenca_counts.index,
                tipo_presenca_percentual,
                tipo_presenca_counts
            )
        ]
        
        # Criar gráfico
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            labels=tipo_presenca_counts.index,
            values=tipo_presenca_counts.values,
            hole=0.4,
            marker_colors=colors,
            text=[f'<b>{val:.1f}%</b>' for val in tipo_presenca_percentual],
            textposition='auto',
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_text,
            textangle=90  # Texto na vertical
        ))
        
        # Atualizar layout
        fig.update_layout(
            title=dict(
                text=f'Distribuição de Tipo de Presença - {momento_label}',
                font=dict(size=20, family="Arial Black")
            ),
            font=dict(family="Arial", size=12),
            height=400,
            plot_bgcolor='#F5F5DC',  # Fundo bege
            paper_bgcolor='white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Erro ao gerar gráfico: {str(e)}")
        return None

def design_login():
    """Define o layout da interface de login."""
    col1, col2 = st.columns(2)
    with col1:
        st.sidebar.image(os.path.join(DATA_DIR, "dema.jpg"), width=100)
    with col2:
        st.sidebar.header('📊 Frequência do Momento Áureo')
    st.sidebar.markdown("---")

def import_warning():
    """Define o aviso de importação."""
    try:
        df = carregar_segundas_feiras()
        if df.empty:
            st.sidebar.warning("Não foi possível carregar as datas das segundas-feiras")
            return
            
        data_hoje = pd.Timestamp(datetime.now().date())
        
        # Criar cópias para evitar SettingWithCopyWarning
        df_antes = df[df['Datas'] < data_hoje].copy()
        df_depois = df[df['Datas'] > data_hoje].copy()
        
        # Formatar datas
        df_antes['Datas'] = df_antes['Datas'].dt.strftime('%d/%m/%Y')
        df_depois['Datas'] = df_depois['Datas'].dt.strftime('%d/%m/%Y')
        
        # Verificar se hoje é dia do Momento Áureo
        hoje_str = data_hoje.strftime('%d/%m/%Y')
        datas_str = df['Datas'].dt.strftime('%d/%m/%Y').tolist()
        
        if hoje_str not in datas_str:
            st.sidebar.error('Lembrando que hoje não é um dia de Momento Áureo.')
        else:
            st.sidebar.success('Hoje é um dia de Momento Áureo! Registre abaixo as frequências.')
            
    except Exception as e:
        st.sidebar.error(f"Erro ao carregar datas: {str(e)}")

def frequencia_reg():
    if "page_configured" not in st.session_state:
        st.set_page_config(page_title="Registrar frequência reunião", layout="centered")
        st.session_state["page_configured"] = True
    
    option_freq = st.sidebar.selectbox('Selecione uma opção:',
                                     ['Selecione', 
                                      'Lançar frequência na Segunda-Feira',
                                      'Lançar frequência em outra data'])

    if option_freq == 'Lançar frequência na Segunda-Feira':
        lancar_frequencia_dia()
    elif option_freq == 'Lançar frequência em outra data':
        lancar_frequencia_data()

def lancar_frequencia_dia():
    st.title('Lançar frequência na Segunda-Feira')
    st.markdown("---")
    
    df_segundas = carregar_segundas_feiras()
    if df_segundas.empty:
        st.error("Não foi possível carregar as datas")
        return
        
    data_hoje = pd.Timestamp(datetime.now().date())
    hoje_str = data_hoje.strftime('%d/%m/%Y')
    datas_str = df_segundas['Datas'].dt.strftime('%d/%m/%Y').tolist()
    
    if hoje_str not in datas_str:
        st.error('Hoje não é um dia de Momento Áureo.')
        return
    
    option_momento = st.sidebar.selectbox('Selecione o momento:', 
                                ['Selecione',
                                 '1º Momento', 
                                 '2º Momento'])
    
    if option_momento == '1º Momento':
        pri_momento(hoje_str)
    elif option_momento == '2º Momento':
        sec_momento(hoje_str)

def lancar_frequencia_data():
    """Define o layout para lançar frequência em uma data específica."""
    st.title("Lançar frequência em outra data")
    st.markdown("---")
    
    try:
        # Carregar datas disponíveis
        df_segundas = carregar_segundas_feiras()
        if df_segundas.empty:
            st.error("Não foi possível carregar as datas disponíveis")
            return
            
        # Data inicial de 2025
        data_inicial = pd.Timestamp('2025-01-01')
        
        # Filtrar e ordenar datas a partir de 2025
        datas_futuras = df_segundas[df_segundas['Datas'] >= data_inicial].copy()
        datas_futuras = datas_futuras.sort_values('Datas')
        
        if datas_futuras.empty:
            st.error("Não há datas disponíveis a partir de 2025")
            return
            
        # Seleção da data - mostrar as datas formatadas para dd/mm/yyyy
        datas_formatadas = datas_futuras['Datas'].dt.strftime('%d/%m/%Y').tolist()
        data_selecionada = st.sidebar.selectbox(
            'Selecione a data:', 
            ['Selecione'] + datas_formatadas
        )
        
        # Só mostra a seleção do momento se uma data foi selecionada
        if data_selecionada and data_selecionada != 'Selecione':
            option_momento = st.sidebar.selectbox('Selecione o momento:', 
                                    ['Selecione',
                                     '1º Momento', 
                                     '2º Momento'],
                                    key='momento_outra_data')  # Chave única para evitar conflito
            
            if option_momento == '1º Momento':
                pri_momento(data_selecionada)
            elif option_momento == '2º Momento':
                sec_momento(data_selecionada)
        
        # Mostrar aviso se hoje não é dia do Momento Áureo
        data_hoje = pd.Timestamp(datetime.now().date())
        hoje_str = data_hoje.strftime('%d/%m/%Y')
        datas_str = df_segundas['Datas'].dt.strftime('%d/%m/%Y').tolist()
        
        if hoje_str not in datas_str:
            st.warning("Hoje não é um dia de Momento Áureo")
                    
    except Exception as e:
        st.error(f"Erro ao processar as datas: {str(e)}")
        print(f"Erro detalhado: {str(e)}")

def pri_momento(data_especifica=None):
    titulo = 'Lançar Frequência - Corrente - 18h às 19h - 1º Momento'
    if data_especifica:
        titulo += f' - Data: {data_especifica}'
    st.title(titulo)
    st.markdown("---")

    participantes = carregar_participantes()
    if participantes.empty:
        st.error("Não foi possível carregar a lista de participantes")
        return

    participantes = participantes.sort_values(by='1_momento')
    registros = []

    for i, participante in participantes.iterrows():
        if participante['1_momento'] and not pd.isnull(participante['1_momento']):
            st.subheader(participante['1_momento'])
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                presente = st.checkbox('Presente', key=f'p_{i}')
            
            with col2:
                ausente = st.checkbox('Ausente', key=f'a_{i}')
                if ausente and presente:
                    st.error('Não é possível estar presente e ausente ao mesmo tempo')
            
            with col3:
                tipo_presenca = None
                if presente and not ausente:
                    tipo_presenca = st.radio(
                        "Tipo de presença:",
                        ["Presencial", "Online"],
                        horizontal=True,
                        key=f't_{i}'
                    )
            
            # Preparar registro
            if presente and not ausente and tipo_presenca:
                registros.append({
                    'Nome': participante['1_momento'],
                    'Frequência': 'Presente',
                    'Tipo de presença': tipo_presenca
                })
            elif ausente and not presente:
                registros.append({
                    'Nome': participante['1_momento'],
                    'Frequência': 'Ausente',
                    'Tipo de presença': 'Ausente'
                })
            
            st.markdown("---")

    st.sidebar.warning('Lembre-se de marcar a presença de todos os participantes antes de enviar.')
    enviar = st.sidebar.button('Enviar')

    if enviar and registros:
        data_registro = data_especifica if data_especifica else datetime.now().strftime('%d/%m/%Y')
        df_freq = pd.DataFrame(registros)
        salvar_frequencia(data_registro, '1º Momento', df_freq)

def sec_momento(data_especifica=None):
    titulo = 'Lançar Frequência - Corrente - 19h às 20h - 2º Momento'
    if data_especifica:
        titulo += f' - Data: {data_especifica}'
    st.title(titulo)
    st.markdown("---")

    participantes = carregar_participantes()
    if participantes.empty:
        st.error("Não foi possível carregar a lista de participantes")
        return

    participantes = participantes.sort_values(by='2_momento')
    registros = []

    for i, participante in participantes.iterrows():
        if participante['2_momento'] and not pd.isnull(participante['2_momento']):
            st.subheader(participante['2_momento'])
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                presente = st.checkbox('Presente', key=f'p2_{i}')
            
            with col2:
                ausente = st.checkbox('Ausente', key=f'a2_{i}')
                if ausente and presente:
                    st.error('Não é possível estar presente e ausente ao mesmo tempo')
            
            with col3:
                tipo_presenca = None
                if presente and not ausente:
                    tipo_presenca = st.radio(
                        "Tipo de presença:",
                        ["Presencial", "Online"],
                        horizontal=True,
                        key=f't2_{i}'
                    )
            
            # Preparar registro
            if presente and not ausente and tipo_presenca:
                registros.append({
                    'Nome': participante['2_momento'],
                    'Frequência': 'Presente',
                    'Tipo de presença': tipo_presenca
                })
            elif ausente and not presente:
                registros.append({
                    'Nome': participante['2_momento'],
                    'Frequência': 'Ausente',
                    'Tipo de presença': 'Ausente'
                })
            
            st.markdown("---")

    st.sidebar.warning('Lembre-se de marcar a presença de todos os participantes antes de enviar.')
    enviar = st.sidebar.button('Enviar')

    if enviar and registros:
        data_registro = data_especifica if data_especifica else datetime.now().strftime('%d/%m/%Y')
        df_freq = pd.DataFrame(registros)
        salvar_frequencia(data_registro, '2º Momento', df_freq)

def analise_dados():
    st.title("Análise de Dados de Frequência")
    
    # Carrega os dados históricos
    df = carregar_dados_frequencia()
    
    # Filtra para considerar somente os registros com 'Data Correta' = "Sim"
    df = df[df['Data'].dt.year == 2024]
    
    if df.empty:
        st.warning("Não há dados para análise.")
        return
    
    # Sidebar: seleção do modo de análise
    modo_analise = st.sidebar.selectbox(
        "Selecione o modo de análise:",
        ["Análise de todos participantes", "Filtrar por Nome"]
    )
    
    if modo_analise == "Análise de todos participantes":
        st.header("Análise de todos participantes")
        
        # Criar tabs para os diferentes momentos
        tab1, tab2, tab3 = st.tabs(["1º Momento", "2º Momento", "Indicadores 2024"])
        
        # --- 1º Momento ---
        with tab1:
            df_m1 = df[df['Momento'] == 1].copy()
            if df_m1.empty:
                st.info("Não há registros para o 1º Momento.")
            else:
                st.subheader("Percentual de Frequência por Mês")
                fig_monthly_m1 = create_monthly_percentage_chart(df_m1, "1º Momento")
                if fig_monthly_m1:
                    st.plotly_chart(fig_monthly_m1, use_container_width=True, key="monthly_m1_tab1")
                
                st.subheader("Distribuição de Tipo de Presença")
                fig_tipo_m1 = plot_presence_type_distribution(df_m1, "1º Momento")
                if fig_tipo_m1:
                    st.plotly_chart(fig_tipo_m1, use_container_width=True, key="presence_m1_tab1")
        
        # --- 2º Momento ---
        with tab2:
            df_m2 = df[
                (df['Momento'] == 2) & 
                (df['Data'].dt.month >= 4)
            ].copy()
            
            if df_m2.empty:
                st.warning('Talvez a pessoa não participe do momento.')
                st.info("Não há registros para o 2º Momento.")
            else:
                st.subheader("Percentual de Frequência por Mês")
                fig_monthly_m2 = create_monthly_percentage_chart(df_m2, "2º Momento")
                if fig_monthly_m2:
                    st.plotly_chart(fig_monthly_m2, use_container_width=True, key="monthly_m2_tab2")
                
                st.subheader("Distribuição de Tipo de Presença")
                fig_tipo_m2 = plot_presence_type_distribution(df_m2, "2º Momento")
                if fig_tipo_m2:
                    st.plotly_chart(fig_tipo_m2, use_container_width=True, key="presence_m2_tab2")
        
        # --- Indicadores Anuais 2024 ---
        with tab3:
            st.subheader("Indicadores Anuais - 2024")
            
            # Filtrar dados por momento
            df_m1 = df[df['Momento'] == 1].copy()
            df_m2 = df[
                (df['Momento'] == 2) & 
                (df['Data'].dt.month >= 4)
            ].copy()
            
            # Criar três colunas para os indicadores
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Percentual de Presença Total**")
                total_presenca = (
                    df_m1['Frequência'].eq('Presente').sum() +
                    df_m2['Frequência'].eq('Presente').sum()
                )
                total_registros = len(df_m1) + len(df_m2)
                percentual_presenca = (total_presenca / total_registros * 100) if total_registros > 0 else 0
                st.metric("", f"{percentual_presenca:.1f}%")
            
            with col2:
                st.markdown("**Presença 1º Momento**")
                presenca_m1 = df_m1['Frequência'].eq('Presente').mean() * 100
                st.metric("", f"{presenca_m1:.1f}%")
            
            with col3:
                st.markdown("**Presença 2º Momento**")
                presenca_m2 = df_m2['Frequência'].eq('Presente').mean() * 100
                st.metric("", f"{presenca_m2:.1f}%")
            
    elif modo_analise == "Filtrar por Nome":
        # Sidebar: seleção do Nome usando unique()
        nomes = sorted(df['Nome'].unique())
        nome_selecionado = st.sidebar.selectbox("Selecione o Nome:", nomes)
        
        if nome_selecionado:
            st.header(f"Análise para {nome_selecionado}")
            
            # Adicionar filtros na sidebar
            st.sidebar.markdown("### Filtros")
            
            # Seletor de momento
            momento_selecionado = st.sidebar.radio(
                "Selecione o Momento:",
                ["Geral", "1º Momento", "2º Momento"],
                horizontal=True
            )
            
            # Seletor de ano
            anos_disponiveis = sorted(df['Data'].dt.year.unique())
            ano_selecionado = st.sidebar.selectbox(
                "Selecione o Ano:",
                anos_disponiveis,
                index=len(anos_disponiveis)-1
            )
            
            # Filtrar meses disponíveis para o ano selecionado
            df_ano = df[df['Data'].dt.year == ano_selecionado]
            meses_disponiveis = sorted(df_ano['Data'].dt.month.unique())
            
            # Slider de meses
            mes_inicio, mes_fim = st.sidebar.select_slider(
                "Selecione o Intervalo de Meses:",
                options=meses_disponiveis,
                value=(meses_disponiveis[0], meses_disponiveis[-1]),
                format_func=lambda x: [
                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
                ][x-1]
            )
            
            # Filtrar dados baseado na seleção
            df_pessoa = df[
                (df['Nome'] == nome_selecionado) &
                (df['Data'].dt.year == ano_selecionado) &
                (df['Data'].dt.month.between(mes_inicio, mes_fim))
            ].copy()
            
            # Aplicar filtro de momento se necessário
            if momento_selecionado == "1º Momento":
                df_pessoa = df_pessoa[df_pessoa['Momento'] == 1]
            elif momento_selecionado == "2º Momento":
                df_pessoa = df_pessoa[
                    (df_pessoa['Momento'] == 2) & 
                    (df_pessoa['Data'].dt.month >= 4)
                ]
            
            if df_pessoa.empty:
                st.warning("Não há dados para o período selecionado.")
            else:
                # Título do período
                meses_pt = [
                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
                ]
                mes_inicio_nome = meses_pt[mes_inicio-1]
                mes_fim_nome = meses_pt[mes_fim-1]
                
                titulo = f"Indicadores do Período ({mes_inicio_nome} a {mes_fim_nome} de {ano_selecionado})"
                if momento_selecionado != "Geral":
                    titulo += f" - {momento_selecionado}"
                st.subheader(titulo)
                
                # Métricas principais
                total_presenca = df_pessoa['Frequência'].eq('Presente').sum()
                total_registros = len(df_pessoa)
                percentual_presenca = (total_presenca / total_registros * 100) if total_registros > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Percentual de Presença", f"{percentual_presenca:.1f}%", f"{total_registros} registros totais")
                
                tipo_presenca_counts = df_pessoa['Tipo de presença'].value_counts()
                total = tipo_presenca_counts.sum()
                
                with col2:
                    presencial_count = tipo_presenca_counts.get('Presencial', 0)
                    online_count = tipo_presenca_counts.get('Online', 0)
                    presencial_online = presencial_count + online_count
                    percentual_presencial_online = (presencial_online / total * 100) if total > 0 else 0
                    st.metric("Presencial + Online", f"{percentual_presencial_online:.1f}%", f"{presencial_online} registros")
                
                with col3:
                    ausente_count = tipo_presenca_counts.get('Ausente', 0)
                    percentual_ausente = (ausente_count / total * 100) if total > 0 else 0
                    st.metric("Ausente", f"{percentual_ausente:.1f}%", f"{ausente_count} registros")
                
                # Gráficos
                st.markdown("#### Frequência Mensal")
                fig_monthly = create_monthly_percentage_chart(df_pessoa, momento_selecionado)
                if fig_monthly:
                    st.plotly_chart(fig_monthly, use_container_width=True)
                st.markdown("#### Tipos de Presença")
                fig_tipo = plot_presence_type_distribution(df_pessoa, momento_selecionado)
                if fig_tipo:
                    st.plotly_chart(fig_tipo, use_container_width=True)


def livros():
    st.title("Livros")
    st.markdown("### Lista de Livros para Estudo")
    
    # Criar diretório data se não existir
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Criar arquivo Excel se não existir
    arquivo_livros = os.path.join(DATA_DIR, 'livros.xlsx')
    if not os.path.exists(arquivo_livros):
        df_inicial = pd.DataFrame(columns=['Nome do livro', 'Autor', 'Ano', 'Capa'])
        df_inicial.to_excel(arquivo_livros, index=False)
    
    # Carregar dados existentes
    try:
        df_livros = pd.read_excel(arquivo_livros, engine='openpyxl')
    except Exception as e:
        st.error(f"Erro ao carregar arquivo de livros: {str(e)}")
        df_livros = pd.DataFrame(columns=['Nome do livro', 'Autor', 'Ano', 'Capa'])
    
    # Formulário na sidebar
    with st.sidebar:
        st.markdown("### Adicionar Novo Livro")
        with st.form(key='livros'):
            livro_nome = st.text_input('Nome do livro')
            livro_autor = st.text_input('Autor')
            livro_ano = st.number_input('Ano', min_value=1900, max_value=2100, value=2024)
            livro_capa = st.file_uploader('Upload da Capa', type=['png', 'jpg', 'jpeg'])
        
            submit = st.form_submit_button('Adicionar Livro')
            
            if submit and livro_nome and livro_autor:  # Validação básica
                try:
                    # Salvar imagem se fornecida
                    imagem_path = ''
                    if livro_capa is not None:
                        # Criar diretório para imagens se não existir
                        img_dir = os.path.join(DATA_DIR, 'capas')
                        if not os.path.exists(img_dir):
                            os.makedirs(img_dir)
                        
                        # Salvar imagem
                        imagem_path = os.path.join(img_dir, livro_capa.name)
                        with open(imagem_path, "wb") as f:
                            f.write(livro_capa.getbuffer())
                
                    # Adicionar novo livro
                    novo_livro = pd.DataFrame({
                        'Nome do livro': [livro_nome],
                        'Autor': [livro_autor],
                        'Ano': [livro_ano],
                        'Capa': [imagem_path if imagem_path else '']
                    })
                    
                    df_livros = pd.concat([df_livros, novo_livro], ignore_index=True)
                    df_livros.to_excel(arquivo_livros, index=False)
                    st.success('Livro adicionado com sucesso!')
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar livro: {str(e)}")
        
        # Seção para remover livros
        if not df_livros.empty:
            st.markdown("### Remover Livro")
            with st.form(key='remover_livro'):
                # Criar lista de opções com nome e autor
                opcoes_livros = [f"{row['Nome do livro']} ({row['Autor']})" for idx, row in df_livros.iterrows()]
                livro_selecionado = st.selectbox('Selecione o livro para remover:', opcoes_livros)
                confirmar = st.form_submit_button('Remover Livro')
                
                if confirmar:
                    try:
                        # Encontrar índice do livro selecionado
                        idx_remover = opcoes_livros.index(livro_selecionado)
                        
                        # Remover arquivo de imagem se existir
                        caminho_imagem = df_livros.iloc[idx_remover]['Capa']
                        if caminho_imagem and os.path.exists(caminho_imagem):
                            os.remove(caminho_imagem)
                        
                        # Remover linha do DataFrame
                        df_livros = df_livros.drop(df_livros.index[idx_remover])
                        
                        # Salvar DataFrame atualizado
                        df_livros.to_excel(arquivo_livros, index=False)
                        st.success('Livro removido com sucesso!')
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao remover livro: {str(e)}")
    
    # Mostrar lista de livros no conteúdo principal
    if df_livros.empty:
        st.info('Não há livros cadastrados. Use o formulário na barra lateral para adicionar.')
    else:
        # Criar grid para exibição dos livros
        for i in range(0, len(df_livros), 3):  # Mostrar 3 livros por linha
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(df_livros):
                    with cols[j]:
                        st.markdown("---")
                        if df_livros.iloc[i + j]['Capa']:
                            try:
                                st.image(df_livros.iloc[i + j]['Capa'], width=150)
                            except:
                                st.markdown("📚")  # Emoji como fallback
                        else:
                            st.markdown("📚")
                        
                        st.markdown(f"**{df_livros.iloc[i + j]['Nome do livro']}**")
                        st.markdown(f"_{df_livros.iloc[i + j]['Autor']}_")
                        st.markdown(f"Ano: {int(df_livros.iloc[i + j]['Ano'])}")

def login():
    """
    Função principal de login que gerencia a autenticação e navegação.
    """
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        design_login()
    else:
        menu = ["Lançar Frequência", "Análise de Dados", "Livros"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Lançar Frequência":
            frequencia_reg()
        elif choice == "Análise de Dados":
            analise_dados()
        elif choice == "Livros":
            livros()

def verificar_momento_aureo():
    """Verifica se hoje é um dia de Momento Áureo."""
    try:
        df_segundas = carregar_segundas_feiras()
        if df_segundas.empty:
            return False
            
        # Data de hoje
        data_hoje = pd.Timestamp(datetime.now().date())
        
        # Verificar se a data de hoje está nas datas do Momento Áureo
        return any(df_segundas['Datas'].dt.date == data_hoje.date())
        
    except Exception as e:
        print(f"Erro ao verificar Momento Áureo: {str(e)}")
        return False

# Iniciar a aplicação
if "page_configured" not in st.session_state:
    st.set_page_config(page_title="Frequência do Momento Áureo", layout="centered")
    st.session_state["page_configured"] = True

if __name__ == "__main__":
    login()

st.sidebar.title('Funções do App')

option = st.sidebar.selectbox('Selecione uma opção:',
                              ['Selecione', 
                               'Lançar frequência', 
                               'Análise de dados de frequência',
                               'Livros'])

if option == 'Selecione':
    st.title('Bem-vindo ao App de Frequência do Momento Áureo!')
    st.write('Este projeto tem como objetivo registrar a frequência do Momento Áureo.')
elif option == 'Lançar frequência':
    frequencia_reg()
elif option == 'Análise de dados de frequência':
    analise_dados()
elif option == 'Livros':
    livros()

import_warning()
