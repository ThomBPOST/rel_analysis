import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_echarts import st_echarts



st.set_page_config(layout="wide")

st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Sélectionner un tableau:", ["Aperçu des données", "Nombre de reliquat par CTI", "Raisons des reliquats par CTI"])


st.title("Reliquat - Analysis")

uploaded_file = st.sidebar.file_uploader("Télécharger un fichier CSV", type=["csv"])

if uploaded_file is not None:
    # Load the CSV file
    df_cleaned = pd.read_csv(uploaded_file, encoding='cp1252', sep=',', quotechar='"', on_bad_lines="skip")



    if option == "Aperçu des données":
        st.write("Aperçu des données:")
        st.write(df_cleaned)



        st.write(df_cleaned.describe())





    #############################################


    # Nombre de reliquat par CTI
    elif option == "Nombre de reliquat par CTI":

        grouped_data_cti = df_cleaned.groupby('transport_center')['nbr'].sum().reset_index()

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


    #######



        df_grouped = df_cleaned.groupby('name_mail_center')[['reliquat_letters', 'reliquat_parcels', 'reliquat_ZZA_ENA', 'reliquat_restmail', 'reliquat_parcelsretours']].sum().reset_index()

        st.header("Types de reliquats par mail center")


        df_melted = df_grouped.melt(id_vars="name_mail_center", var_name="Type", value_name="Count")


        st.bar_chart(df_melted.pivot(index='name_mail_center', columns='Type', values='Count'))

        st.markdown("""
        - **reliquat_letters**: Nombre de lettres en reliquat
        - **reliquat_parcels**: Nombre de colis en reliquat
        - **reliquat_ZZA_ENA**: Nombre de ZZA/ENA en reliquat
        - **reliquat_restmail**: Nombre de restmails en reliquat
        - **reliquat_parcelsretours**: Nombre de retours de colis en reliquat
        """)


    #######


    # Affiche le CTI et le type de relicat au cours de 2023 / 2024

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




    #############################################

    # RAISON RELIQUAT

    # Raisons des reliquats par CTI
    elif option == "Raisons des reliquats par CTI":
        df_count = df_cleaned.groupby(['transport_center', 'reason']).size().unstack(fill_value=0)

        st.header("Raisons des reliquats par CTI")
        st.bar_chart(df_count)

        st.markdown("""
        - **C**: Capacité
        - **T**: Trop tard
        - **A**: Autre
        """)


    #######

        df_count = df_cleaned.groupby(['name_mail_center', 'reason']).size().unstack(fill_value=0)

        st.header("Raisons des reliquats par mail center")
        st.bar_chart(df_count)

        st.markdown("""
        - **C**: Capacité
        - **T**: Trop tard
        - **A**: Autre
        """)

    #######

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





    #######


        st.header("Évolution des raisons des reliquats par mail center dans le temps")

        mail_center_list = df_cleaned['name_mail_center'].unique()
        selected_mail_center = st.selectbox("Sélectionnez un mail center pour l'évolution dans le temps", mail_center_list)
        
        reason_list = df_cleaned['reason'].unique()
        selected_reason = st.selectbox("Sélectionnez la raison du reliquat", reason_list, key="reason_mail_center")

        df_time_reason_mail_center = df_cleaned[(df_cleaned['name_mail_center'] == selected_mail_center) & 
                                                (df_cleaned['reason'] == selected_reason)]
        df_time_reason_grouped_mail_center = df_time_reason_mail_center.groupby('date').size().reset_index(name='count')

        st.subheader(f"Évolution de la raison '{selected_reason}' pour le mail center : {selected_mail_center}")

        st.line_chart(df_time_reason_grouped_mail_center.set_index('date')['count'], height=300, width=700, use_container_width=True)


    #############################################





