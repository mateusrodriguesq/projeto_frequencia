


from datetime import datetime
import openpyxl
import pandas as pd
import streamlit as st
from datetime import datetime


def gerar_segundas_feiras():
    """
    Gera um DataFrame com todas as datas que caem em uma segunda-feira
    no formato dd/mm/yy entre 2022 e 2030.
    """
    # Definir a data inicial e final
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2040, 12, 31)

    # Gerar todas as segundas-feiras no intervalo
    mondays = pd.date_range(start=start_date, end=end_date, freq='W-MON')

    # Criar um DataFrame com o formato desejado
    df_mondays = pd.DataFrame({'Datas': mondays.strftime('%d/%m/%Y')})
    st.write(df_mondays)
    df_mondays.to_excel('data/segundas_feiras.xlsx', index=False)
