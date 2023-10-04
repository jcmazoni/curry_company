# Importaçao de Biblioteca

import pandas as pd

# Biblioteca relacionada a contrução de graficos
import plotly.express as px 

import streamlit as st
from datetime import datetime
from PIL import Image

import re
from haversine import haversine
import folium

st.set_page_config( page_title='Visão Entregadores', page_icon='🚚', layout='wide')

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
# VISÃO DOS ENTREGADORES - Construção dos Graficos
#========================================================================

#========================================================================
# BARRA LATERAL DO STREAMLIT 
#========================================================================
st.header('Marketplace - Visão Entregadores')

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
        st.title('Overwall Colunas')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            
            # - A maior idade dos entregadores.
            maior_idade = data1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior de Idade',maior_idade)

        with col2:
            
            # - A menor idade dos entregadores.
            menor_idade = data1.loc[:,'Delivery_person_Age'].min()
            col2.metric('A Menor idade', menor_idade)

        with col3:
            
            # 2. A pior e a melhor condição de veículos.
            melhor_condicao = data1.loc[:,'Vehicle_condition'].max()
            col3.metric('A melhor condição Veiculo', melhor_condicao)
            
        with col4:
            #st.subheader('Pior condição do Veiculo') 
            pior_condicao = data1.loc[:,'Vehicle_condition'].min()
            col4.metric('A Pior condição', pior_condicao)

    with st.container():
        st.markdown("""---""")
        st.title('Avalizações')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### Avaliações média por Entregadores') 

            cols = ['Delivery_person_ID', 'Delivery_person_Ratings']
            media = (round(data1.loc[:, cols].groupby(['Delivery_person_ID']).mean().reset_index(),3))
            st.dataframe(media)

        with col2:
            st.subheader('Avaliação média por Trânsito') 
            # 4. A avaliação média e o desvio padrão por tipo de tráfego.

            cols = ['Delivery_person_Ratings', 'Road_traffic_density']
            avaliacao = data1.loc[:, cols].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings': ['mean','std']})

            # Renomeando as colunas
            avaliacao.columns = ['- Média -','- Desvio Padrão -']

            # Resetando os index
            avaliacao.reset_index()

            st.dataframe(avaliacao)


            st.subheader('Avaliação média por Clima') 

            # 5. A avaliação média e o desvio padrão por condições climáticas.
            cols = ['Delivery_person_Ratings', 'Weatherconditions']
            clima = data1.loc[:, cols].groupby(['Weatherconditions']).agg({'Delivery_person_Ratings': ['mean','std']})

            # Renomeando as colunas
            clima.columns = ['- Média -','- Desvio Padrão -']

            # Resetando os index
            clima.reset_index()
            st.dataframe(clima)


    
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('#### Top Entregadores Mais Rápidos')


            # 6. A média dos 10 entregadores mais rápidos por cidade.

            cols = ['Delivery_person_ID', 'Time_taken(min)', 'City']
            df1 = data1.loc[:, cols].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'],ascending=True).reset_index()

            metropolitano = df1.loc[df1['City'] == 'Metropolitian', :].head(10)
            urbano = df1.loc[df1['City'] == 'Urban', :].head(10)
            semiurbano = df1.loc[df1['City'] == 'Semi-Urban', :].head(10)

            df_aux = pd.concat([metropolitano, urbano, semiurbano]).reset_index(drop=True)
            st.dataframe(df_aux)

        with col2:
            st.markdown(' #### Top Entregadores Mais Lentos')

            # 7. A média dos 10 entregadores mais lentos por cidade.

            cols = ['Delivery_person_ID', 'Time_taken(min)', 'City']
            df1 = data1.loc[:, cols].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'],ascending=False).reset_index()

            metropolitano = df1.loc[df1['City'] == 'Metropolitian', :].head(10)
            urbano = df1.loc[df1['City'] == 'Urban', :].head(10)
            semiurbano = df1.loc[df1['City'] == 'Semi-Urban', :].head(10)

            df_aux = pd.concat([metropolitano, urbano, semiurbano]).reset_index(drop=True)
            st.dataframe(df_aux)













