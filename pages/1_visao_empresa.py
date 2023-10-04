# Importaçao de Biblioteca

import pandas as pd

# Biblioteca relacionada a contrução de graficos
import plotly.express as px 

import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

import re
from haversine import haversine
import folium

st.set_page_config( page_title='Visão Empresa', page_icon='📊', layout='wide')

#  Importando o DATASET
data = pd.read_csv("dataset/train.csv")

#print(data.head())

#========================================================================
# LIMPEZA DE DADOS DO DATAFRAME
#========================================================================

# Fazendo a copia do Dataframe lido
data1 = data.copy()

# Remover espaco string
data1.loc[: , 'ID'] = data1.loc[:, 'ID'].str.strip()
data1.loc[: , 'Delivery_person_ID'] = data1.loc[:, 'Delivery_person_ID'].str.strip()
data1.loc[: , 'Road_traffic_density'] = data1.loc[:, 'Road_traffic_density'].str.strip()
data1.loc[: , 'Type_of_order'] = data1.loc[:, 'Type_of_order'].str.strip()
data1.loc[: , 'Type_of_vehicle'] = data1.loc[:, 'Type_of_vehicle'].str.strip()
data1.loc[: , 'City'] = data1.loc[:, 'City'].str.strip()
data1.loc[: , 'Festival'] = data1.loc[:, 'Festival'].str.strip()

# 1 - Convertendo linhas que estavam sujas como 'Nan ' para inteiro, excluindo todas que tenham Nan
# Excluir as linhas com a idade dos entregadores vazias
# Conceito de seleção condicional

linhas_selecionadas = (data1['Delivery_person_Age'] != 'NaN ')
data1  = data1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (data1['Road_traffic_density'] != 'NaN')
data1  = data1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (data1['City'] != 'NaN')
data1  = data1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (data1['Festival'] != 'NaN ')
data1  = data1.loc[linhas_selecionadas, :].copy()


# conversao de texto / categoria / string para numeros inteiros
data1['Delivery_person_Age'] = data1['Delivery_person_Age'].astype( int )

# 2 - Convertendo todas as colunas Rating de texto para numero decimal (float)

data1['Delivery_person_Ratings'] = data1['Delivery_person_Ratings'].astype(float)

# 3 - Convertendo a Coluna order_date de texto para data
data1['Order_Date'] = pd.to_datetime( data1['Order_Date'], format='%d-%m-%Y' )

# 4 - Convertendo multiple_deliveries de texto para numero inteiro (int)
linhas_selecionadas = (data1['multiple_deliveries'] != 'NaN ')
data1  = data1.loc[linhas_selecionadas, :].copy()
data1['multiple_deliveries'] = data1['multiple_deliveries'].astype( int )

# 5 - Removendo espaços dentro de Strings/textos/objects

# Lembrando que o comando len(data1) eu acho o quanto que minha lista deve percorrer

# Comando para remover o texto  de numeros

#data1 = data1.reset_index(drop = True)
#for i in range (len(data1)):
#    data1.loc[ i, 'Time_taken(min)'] = re.findall(r'\d+', data1.loc[i, 'Time_taken(min)'])

data1['Time_taken(min)'] = data1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1] )
data1['Time_taken(min)'] = data1['Time_taken(min)'].astype(int)

############################################ FIM DA LIMPEZA DO DATAFRAME ############################################

#========================================================================
# VISÃO DA EMPRESA - Construção dos Graficos
#========================================================================

#========================================================================
# BARRA LATERAL DO STREAMLIT 
#========================================================================
st.header('Marketplace - Visão Cliente')

#image_path = 'C:/Users/jcmaz/Downloads/Python/venv/logo.jpg'

image = Image.open('logo.jpg')

st.sidebar.image( image, width=170)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Delivery Mais Rápido da India')
st.sidebar.markdown( """---""")

st.sidebar.markdown('## Selecione uma Data Limite')

date_slider = st.sidebar.slider(
    'Até Qual Valor ?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY'
    )
#st.header(date_slider)

st.sidebar.markdown( """---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de Trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low')

st.sidebar.markdown( """---""")
st.sidebar.markdown('## Powered by Projeto01')


# Filtros de Data
linhas_selecionadas = data1['Order_Date'] < date_slider
data1 = data1.loc[linhas_selecionadas, :]

#st.dataframe(data1) 

# Filtros de Transito
linhas_selecionadas = data1['Road_traffic_density'].isin(traffic_options)
data1 = data1.loc[linhas_selecionadas, :]


#========================================================================
# LAYOUT NO STREAMLIT 
#========================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():    
        st.header('Pedidos por Dia')
        # 1. Quantidade de pedidos por dia.
        cols = ['ID', 'Order_Date']
        df_aux = data1.loc[:, cols].groupby(['Order_Date']).count().reset_index()

        fig = px.bar( df_aux, x='Order_Date', y='ID' )
        st.plotly_chart(fig, use_container_width=True )
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Trafego de Pedidos')
            # 3. Distribuição dos pedidos por tipo de tráfego.
            df_aux = data1.loc[:, ['ID','Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()

            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

            df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

            fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            #st.markdown('# Coluna 2')    
            # 4. Comparação do volume de pedidos por cidade e tipo de tráfego.
            st.header('Trafego Pedidos / Cidade')
            df_aux = data1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()

            df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Pedidos por Semana')
        data1['Week_of_year'] = data1['Order_Date'].dt.strftime( '%U' ) # O comando dt.strftime transforma a data para dias da semana
        df_aux = data1.loc[:, ['ID', 'Week_of_year']].groupby(['Week_of_year']).count().reset_index()
    
        fig = px.line(df_aux, x='Week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Pedidos por trafego')
        df_aux01 = data1.loc[:, ['ID', 'Week_of_year']].groupby(['Week_of_year']).count().reset_index()
        df_aux02 = data1.loc[:, ['Delivery_person_ID', 'Week_of_year']].groupby(['Week_of_year']).nunique().reset_index()

        df_aux = pd.merge(df_aux01, df_aux02, how='inner')
        df_aux['order_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        fig = px.line(df_aux, x='Week_of_year', y='order_delivery')
        st.plotly_chart(fig, use_container_width=True)



with tab3:
    st.markdown('# Mapa')
    
    df_aux = data1.loc[:, ['City','Road_traffic_density', 'Delivery_location_longitude', 'Delivery_location_latitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']]).add_to( map )

    folium_static( map, width=1024, height=600  )