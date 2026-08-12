import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Mapa de Estaciones de Policía")

mapa = folium.Map(
    location=[14.0723, -87.1921],
    zoom_start=12
)

folium.Marker(
    [14.0723, -87.1921],
    popup="Estación de Policía"
).add_to(mapa)

st_folium(mapa, width=700, height=500)

 
