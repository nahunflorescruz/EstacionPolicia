import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import great_circle

# Configuración inicial de la página
st.set_page_config(page_title="Estaciones de Policía", layout="wide")

st.title("📍 Buscador de Estaciones de Policía Cercanas")

# Lista de estaciones de policía en Honduras
police_stations_honduras = [
    {
        'name': 'Estación Central de Tegucigalpa',
        'latitude': 14.0833,
        'longitude': -87.2000
    },
    {
        'name': 'Comisaría de San Pedro Sula',
        'latitude': 15.5000,
        'longitude': -88.0167
    },
    {
        'name': 'Jefatura de La Ceiba',
        'latitude': 15.7700,
        'longitude': -86.7800
    },
    {
        'name': 'Puesto Policial de Comayagua',
        'latitude': 14.4500,
        'longitude': -87.6400
    },
    {
        'name': 'Unidad Policial de Choluteca',
        'latitude': 13.3000,
        'longitude': -87.2000
    },
    {
        'name': 'Delegación Policial de Danlí',
        'latitude': 14.0300,
        'longitude': -86.5800
    }
]

# Función para estimar el tiempo de viaje
def get_estimated_travel_time(distance_km, mode):
    if mode == 'Carro':
        time_hours = distance_km / 60
    elif mode == 'Bicicleta':
        time_hours = distance_km / 15
    elif mode == 'Caminando':
        time_hours = distance_km / 5
    else:
        return "N/A"

    if time_hours < 1:
        return f"{round(time_hours * 60)} min"
    else:
        return f"{round(time_hours, 1)} horas"

# Entradas de usuario usando los widgets nativos de Streamlit
col1, col2, col3 = st.columns(3)

with col1:
    user_lat = st.number_input('Latitud:', value=14.0833, format="%.4f")
with col2:
    user_lon = st.number_input('Longitud:', value=-87.2000, format="%.4f")
with col3:
    selected_mode = st.selectbox('Modo de viaje:', ['Carro', 'Bicicleta', 'Caminando'])

# Botón para ejecutar la búsqueda
if st.button('🔎 Buscar Estaciones Cercanas', use_container_width=True):
    # Validar coordenadas
    if not (-90 <= user_lat <= 90 and -180 <= user_lon <= 180):
        st.error("Por favor, introduce coordenadas válidas (Latitud entre -90 y 90, Longitud entre -180 y 180).")
    else:
        user_coords = (user_lat, user_lon)
        station_distances = []

        # Calcular distancias
        for station in police_stations_honduras:
            station_coords = (station['latitude'], station['longitude'])
            distance = great_circle(user_coords, station_coords).km
            estimated_time = get_estimated_travel_time(distance, selected_mode)
            station_distances.append({
                'Nombre': station['name'],
                'Latitud': station['latitude'],
                'Longitud': station['longitude'],
                'Distancia (km)': round(distance, 2),
                f'Tiempo est. ({selected_mode})': estimated_time
            })

        # Ordenar por distancia
        df_closest_stations = pd.DataFrame(station_distances)
        df_sorted = df_closest_stations.sort_values(by='Distancia (km)').reset_index(drop=True)

        st.subheader(f"Resultados para ({user_lat}, {user_lon}) viajando en {selected_mode}:")
        
        # Mostrar la tabla de resultados
        st.dataframe(df_sorted, use_container_width=True)

        # Crear mapa interactivo con Folium
        m = folium.Map(location=user_coords, zoom_start=9)

        # Marcador para el usuario
        folium.Marker(
            location=user_coords,
            popup='Tu Ubicación',
            tooltip='Tu Ubicación',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

        # Marcadores para las estaciones
        for idx, row in df_sorted.iterrows():
            folium.Marker(
                location=[row['Latitud'], row['Longitud']],
                popup=f"{row['Nombre']} ({row['Distancia (km)']} km) - Tiempo: {row[f'Tiempo est. ({selected_mode})']}",
                tooltip=row['Nombre'],
                icon=folium.Icon(color='blue', icon='flag')
            ).add_to(m)

        # Renderizar el mapa en Streamlit
        st_folium(m, width=1000, height=500)
