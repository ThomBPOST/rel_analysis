import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import altair as alt
from streamlit_echarts import st_echarts

st.set_page_config(layout="wide")

st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Sélectionner un tableau:", ["Nombre de reliquat par CTI", "Raisons des reliquats par CTI", "Aperçu des données"])

st.title("Reliquat - Analysis")

uploaded_file = st.sidebar.file_uploader("Télécharger le fichier .csv reliquat", type=["csv"])

@st.cache_data
def load_and_process_data(file_content, start_date, end_date):
    from io import StringIO
    df_cleaned = pd.read_csv(StringIO(file_content), encoding='cp1252', sep=',', quotechar='"', on_bad_lines="skip")
    df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], format='%d/%m/%Y', errors='coerce')
    df_cleaned = df_cleaned.dropna(subset=['date'])
    
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    filtered_data = df_cleaned[(df_cleaned['date'] >= start_date) & (df_cleaned['date'] <= end_date)]
    grouped_data_cti = filtered_data.groupby('transport_center')['nbr'].sum().reset_index()
    
    return grouped_data_cti

if uploaded_file is not None:
    file_content = uploaded_file.getvalue().decode("cp1252")

    if option == "Aperçu des données":
        df_cleaned = pd.read_csv(uploaded_file, encoding='cp1252', sep=',', quotechar='"', on_bad_lines="skip")
        st.write("Aperçu des données:")
        st.write(df_cleaned)

    elif option == "Nombre de reliquat par CTI":
        df_cleaned = pd.read_csv(uploaded_file, encoding='cp1252', sep=',', quotechar='"', on_bad_lines="skip")
        df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], format='%d/%m/%Y', errors='coerce')
        df_cleaned = df_cleaned.dropna(subset=['date'])

        min_date = df_cleaned['date'].min().date()
        max_date = df_cleaned['date'].max().date()

        start_date, end_date = st.slider(
            "Sélectionner la période",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)
        )

        grouped_data_cti = load_and_process_data(file_content, start_date, end_date)

        x_data_cti = grouped_data_cti['transport_center'].tolist()
        y_data_cti = grouped_data_cti['nbr'].tolist()

        options_cti = {
            "xAxis": {
                "type": "category",
                "data": x_data_cti,
                "axisLabel": {
                    "rotate": 0, 
                    "fontSize": 20,  
                }
            },
            "yAxis": {"type": "value"},
            "grid": {
                "left": "5%",
                "right": "5%",
                "bottom": "15%",  
                "containLabel": True
            },
            "series": [{"data": y_data_cti, "type": "bar"}],
        }
        st.header("Nombre de reliquat par CTI")
        st_echarts(options=options_cti, height="700px")

        df_grouped = df_cleaned.groupby('name_mail_center')[['reliquat_letters', 'reliquat_parcels', 'reliquat_ZZA_ENA', 'reliquat_restmail', 'reliquat_parcelsretours']].sum().reset_index()
        rows_to_exclude = ["1099 - NEW BRUSSEL X", "2099 - NEW ANTWERPEN X", "4099 - LIEGE X", "6099 - CHARLEROI X", "9099 - GENT X"]
        df_grouped = df_grouped[~df_grouped['name_mail_center'].isin(rows_to_exclude)]
        df_grouped['total_reliquats'] = df_grouped[['reliquat_letters', 'reliquat_parcels', 'reliquat_ZZA_ENA', 'reliquat_restmail', 'reliquat_parcelsretours']].sum(axis=1)
        df_grouped = df_grouped.sort_values(by='total_reliquats', ascending=False).reset_index(drop=True)
        df_melted = df_grouped.melt(id_vars=["name_mail_center"], value_vars=['reliquat_letters', 'reliquat_parcels', 'reliquat_ZZA_ENA', 'reliquat_restmail', 'reliquat_parcelsretours'], var_name="Type", value_name="Count")
        df_pivot = df_melted.pivot(index='name_mail_center', columns='Type', values='Count')

        st.header("Types de reliquats par mail center")
        st.bar_chart(df_pivot)

        st.markdown("""
        - **reliquat_letters**: Nombre de lettres en reliquat
        - **reliquat_parcels**: Nombre de colis en reliquat
        - **reliquat_ZZA_ENA**: Nombre de ZZA/ENA en reliquat
        - **reliquat_restmail**: Nombre de restmails en reliquat
        - **reliquat_parcelsretours**: Nombre de retours de colis en reliquat
        """)

        df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], format='%d/%m/%Y')
        grouped_data_time_cti = df_cleaned.groupby(['date', 'transport_center']).sum().reset_index()

        st.header("Évolution des reliquats par CTI dans le temps")

        cti_list = grouped_data_time_cti['transport_center'].unique()
        selected_cti = st.selectbox("Sélectionnez un CTI", cti_list)
        
        reliquat_types = ['reliquat_letters', 'reliquat_parcels', 'reliquat_ZZA_ENA', 'reliquat_restmail', 'reliquat_parcelsretours']
        selected_reliquat = st.selectbox("Sélectionnez le type de reliquat", reliquat_types)

        df_cti = grouped_data_time_cti[grouped_data_time_cti['transport_center'] == selected_cti]

        st.subheader(f"Évolution du {selected_reliquat} pour le CTI : {selected_cti}")

        st.line_chart(df_cti.set_index('date')[selected_reliquat], height=300, width=700, use_container_width=True)

    elif option == "Raisons des reliquats par CTI":
        df_cleaned = pd.read_csv(uploaded_file, encoding='cp1252', sep=',', quotechar='"', on_bad_lines="skip")
        df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], format='%d/%m/%Y', errors='coerce')
        df_cleaned = df_cleaned.dropna(subset=['date'])
        
        df_count = df_cleaned.groupby(['transport_center', 'reason']).size().unstack(fill_value=0)

        st.header("Raisons des reliquats par CTI")
        st.bar_chart(df_count)

        st.markdown("""
        - **C**: Capacité
        - **T**: Trop tard
        - **A**: Autre
        """)

        df_count = df_cleaned.groupby(['name_mail_center', 'reason']).size().unstack(fill_value=0)

        st.header("Raisons des reliquats par mail center")
        st.bar_chart(df_count)

        st.markdown("""
        - **C**: Capacité
        - **T**: Trop tard
        - **A**: Autre
        """)

        st.header("Évolution des raisons des reliquats par CTI dans le temps")

        cti_list = df_cleaned['transport_center'].unique()
        selected_cti = st.selectbox("Sélectionnez un CTI pour l'évolution dans le temps", cti_list)
        
        reason_list = df_cleaned['reason'].unique()
        selected_reason = st.selectbox("Sélectionnez la raison du reliquat", reason_list, key="reason_cti")

        df_time_reason_cti = df_cleaned[(df_cleaned['transport_center'] == selected_cti) & 
                                        (df_cleaned['reason'] == selected_reason)]
        df_time_reason_grouped_cti = df_time_reason_cti.groupby('date').size().reset_index(name='count')

        st.subheader(f"Évolution de la raison '{selected_reason}' pour le CTI : {selected_cti}")

        st.line_chart(df_time_reason_grouped_cti.set_index('date')['count'], height=300, width=700, use_container_width=True)

        st.header("Évolution des raisons des reliquats par mail center dans le temps")

        mail_center_list = df_cleaned['name_mail_center'].unique()
        selected_mail_center = st.selectbox("Sélectionnez un mail center pour l'évolution dans le temps", mail_center_list)
        
        selected_reason = st.selectbox("Sélectionnez la raison du reliquat", reason_list, key="reason_mail_center")

        df_time_reason_mail_center = df_cleaned[(df_cleaned['name_mail_center'] == selected_mail_center) & 
                                                (df_cleaned['reason'] == selected_reason)]
        df_time_reason_grouped_mail_center = df_time_reason_mail_center.groupby('date').size().reset_index(name='count')

        st.subheader(f"Évolution de la raison '{selected_reason}' pour le mail center : {selected_mail_center}")

        st.line_chart(df_time_reason_grouped_mail_center.set_index('date')['count'], height=300, width=700, use_container_width=True)
