# Importaçao de Biblioteca

import pandas as pd
import numpy as np

# Biblioteca relacionada a contrução de graficos
import plotly.express as px 
import plotly.graph_objects as go

import streamlit as st
from datetime import datetime
from PIL import Image

import re
from haversine import haversine
import folium

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

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
# VISÃO DOS RESTAURANTE - Construção dos Graficos
#========================================================================

#========================================================================
# BARRA LATERAL DO STREAMLIT 
#========================================================================
st.header('Marketplace - Visão Restaurantes')

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
tab1, tab2, tab3 = st.tabs (['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overwall Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            # 1. A quantidade de entregadores únicos.
            delivery_unique = data1.loc[:,'Delivery_person_ID'].nunique()
            col1.metric('Entregadores Unicos', delivery_unique)
        with col2:
            #st.markdown('##### Coluna 2')
            cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
            data1['Distancia'] = data1.loc[:, cols].apply( lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)

            distancia_media = round(data1['Distancia'].mean(),2)
            col2.metric('A Distancia média das entregas é', distancia_media )
            

        with col3:
            # O tempo médio de entrega durantes os Festivais.

            cols = ['Time_taken(min)', 'Festival']
            tempo = data1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean','std']})

            # Renomeando as colunas
            tempo.columns = ['- Média -','- Desvio Padrão -']
            tempo = tempo.reset_index()

            linhas_selecionadas = tempo['Festival'] == 'Yes'
            tempo = round(tempo.loc[linhas_selecionadas, '- Média -'],2)

            # Resetando os index
            col3.metric('Tempo Médio com os Festivais',tempo)


        with col4:
            
            # O Desvio padrão das entrega durantes os Festivais.

            cols = ['Time_taken(min)', 'Festival']
            tempo = data1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean','std']})

            # Renomeando as colunas
            tempo.columns = ['- Média -','- Desvio Padrão -']
            tempo = tempo.reset_index()

            linhas_selecionadas = tempo['Festival'] == 'Yes'
            tempo = round(tempo.loc[linhas_selecionadas, '- Desvio Padrão -'],2)

            # Resetando os index
            col4.metric('STD Entrega nos Festivais',tempo)
        with col5:
            # O tempo médio de entrega durantes os Festivais.

            cols = ['Time_taken(min)', 'Festival']
            tempo = data1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean','std']})

            # Renomeando as colunas
            tempo.columns = ['- Média -','- Desvio Padrão -']
            tempo = tempo.reset_index()

            linhas_selecionadas = tempo['Festival'] == 'No'
            tempo = round(tempo.loc[linhas_selecionadas, '- Média -'],2)

            # Resetando os index
            col5.metric('Tempo Médio sem Festivais',tempo)
        with col6:
            # O Desvio padrão das entrega durantes os Festivais.

            cols = ['Time_taken(min)', 'Festival']
            tempo = data1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean','std']})

            # Renomeando as colunas
            tempo.columns = ['- Média -','- Desvio Padrão -']
            tempo = tempo.reset_index()

            linhas_selecionadas = tempo['Festival'] == 'No'
            tempo = round(tempo.loc[linhas_selecionadas, '- Desvio Padrão -'],2)

            # Resetando os index
            col6.metric('STD Entrega sem Festivais',tempo)


    with st.container():
        st.markdown("""---""")
        st.title('Tempo médio de entrega por Cidade')

        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
        data1['Distancia'] = data1.loc[:, cols].apply( lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)

        distancia_media = data1.loc[:, ['City', 'Distancia']].groupby('City').mean().reset_index()

        fig = go.Figure(data=[go.Pie(labels=distancia_media['City'], values=distancia_media['Distancia'], pull=[0, 0.1, 0])])
        st.plotly_chart(fig)


    with st.container():
        st.markdown("""---""")
        st.title('Distribuição dos Tempos')

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### col1')

            # 3. O tempo médio e o desvio padrão de entrega por cidade.

            cols = ['City', 'Time_taken(min)']
            tempo = data1.loc[:, cols].groupby(['City']).agg({'Time_taken(min)': ['mean','std']})

            # Renomeando as colunas
            tempo.columns = ['Media','- Desvio Padrão -']

            # Resetando os index
            tempo = tempo.reset_index()

            fig = go.Figure()
            fig.add_trace(go.Bar( name='Control',
                                  x=tempo['City'],
                                  y=tempo['Media'],
                                  error_y=dict(type='data', array=tempo['- Desvio Padrão -'] ) ) )
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)

        with col2:
            # 5. O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego.

            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            tempo = data1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean','std']})

            # Renomeando as colunas
            tempo.columns = ['Media','Desvio_Padrao']

            # Resetando os index
            tempo= tempo.reset_index()

            fig = px.sunburst(tempo, path=['City', 'Road_traffic_density'], values='Media',
                              color='Desvio_Padrao', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(tempo['Desvio_Padrao']))
            st.plotly_chart(fig)
                    
    with st.container():
        st.markdown("""---""")
        st.title('Distribuição de Distância')
        # 4. O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.

        cols = ['City', 'Time_taken(min)', 'Type_of_order']
        tempo = data1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean','std']})

        # Renomeando as colunas
        tempo.columns = ['- Média -','- Desvio Padrão -']

        # Resetando os index
        tempo.reset_index()

        st.dataframe(tempo)
            


















