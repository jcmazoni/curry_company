import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲",
    layout='centered'

)
#image_path="C:/Users/jcmaz/Downloads/Python/venv/"
image=Image.open('logo.jpg')

st.sidebar.image(image, width=120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Delivery Mais Rápido da India')
st.sidebar.markdown( """---""")

st.write(" Curry Company Growth Dashboard")

st.markdown(
        """
        Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
        
        ### Como utilizar esse Growth Dashboard ?
        
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamento.
            - Visão Tatica: Indicadores semanais de crescimento.
            - Visão Geográfica: Insights de geolocalização.
        
        -   ------------------------------------------------------------        
        - Visão Entregador:
            - Acompanhamento dos indicadores semanais de crescimento.
        
        -   ------------------------------------------------------------        
        - Visão Restaurantes:
            - Indicadores semanais de crescimento dos restaurantes
        
        ### Perguntas e Ajuda
        - Time de Desenvolvimento Data Science
        E-mail: jcmazoni@gmail.com
""")