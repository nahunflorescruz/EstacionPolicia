
import streamlit as st
import folium
import pandas as pd
import math
from streamlit_folium import st_folium


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Estaciones de Policía",
    page_icon="🚔",
    layout="wide"
)


# ============================================================
# TÍTULO
# ============================================================

st.title("🚔 Buscador de Estaciones de Policía")

st.write(
    "Ingresa tu ubicación para encontrar las estaciones "
    "de policía más cercanas."
)


# ============================================================
# DATOS DE LAS ESTACIONES
# ============================================================

police_stations_honduras = [

    {
        "name": "Estación de Policía • Loarque",
        "plus_code": "2QVQ+9HX",
        "latitude": 14.0434875,
        "longitude": -87.211015625
    },

    {
        "name": "Posta Policial La Rosa",
        "plus_code": "3Q8G+7QV",
        "latitude": 14.0657375,
        "longitude": -87.223078125
    },

    {
        "name": "Estación de Policía • Las Casitas",
        "plus_code": "3P3V+CX5",
        "latitude": 14.0535125,
        "longitude": -87.255015625
    },

    {
        "name": "Estación de Policía • Vista Hermosa",
        "plus_code": "3QH7+PQC",
        "latitude": 14.0793125,
        "longitude": -87.235609375
    }
]


# ============================================================
# FUNCIÓN PARA CALCULAR DISTANCIA
# ============================================================

def calcular_distancia(lat1, lon1, lat2, lon2):

    R = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)

    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ============================================================
# FUNCIÓN PARA CALCULAR TIEMPO
# ============================================================

def get_estimated_travel_time(distance_km, mode):

    if mode == "Carro":
        speed = 40

    elif mode == "Bicicleta":
        speed = 15

    elif mode == "Caminando":
        speed = 5

    else:
        return "N/A"

    time_hours = distance_km / speed

    if time_hours < 1:

        minutes = round(time_hours * 60)

        return f"{minutes} minutos"

    else:

        return f"{round(time_hours, 1)} horas"


# ============================================================
# PANEL LATERAL
# ============================================================

st.sidebar.header("📍 Mi ubicación")


latitude = st.sidebar.number_input(
    "Latitud",
    value=14.0833,
    min_value=-90.0,
    max_value=90.0,
    format="%.6f"
)


longitude = st.sidebar.number_input(
    "Longitud",
    value=-87.2000,
    min_value=-180.0,
    max_value=180.0,
    format="%.6f"
)


# ============================================================
# MEDIO DE TRANSPORTE
# ============================================================

mode = st.sidebar.selectbox(
    "🚗 Medio de transporte",
    [
        "Carro",
        "Bicicleta",
        "Caminando"
    ]
)


# ============================================================
# BOTÓN
# ============================================================

buscar = st.sidebar.button(
    "🔍 Buscar estaciones",
    use_container_width=True
)


# ============================================================
# BUSCAR ESTACIONES
# ============================================================

if buscar:

    # --------------------------------------------------------
    # UBICACIÓN DEL USUARIO
    # --------------------------------------------------------

    user_lat = latitude
    user_lon = longitude

    user_coords = (
        user_lat,
        user_lon
    )

    station_distances = []


    # --------------------------------------------------------
    # CALCULAR DISTANCIAS
    # --------------------------------------------------------

    for station in police_stations_honduras:

        distance = calcular_distancia(
            user_lat,
            user_lon,
            station["latitude"],
            station["longitude"]
        )

        estimated_time = get_estimated_travel_time(
            distance,
            mode
        )

        station_distances.append({

            "Estación": station["name"],

            "Código Plus": station["plus_code"],

            "Latitud": station["latitude"],

            "Longitud": station["longitude"],

            "Distancia (km)": round(
                distance,
                2
            ),

            "Tiempo estimado": estimated_time

        })


    # --------------------------------------------------------
    # DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(
        station_distances
    )


    df = df.sort_values(
        by="Distancia (km)"
    ).reset_index(drop=True)


    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    st.subheader("🚔 Estaciones más cercanas")


    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # ESTACIÓN MÁS CERCANA
    # ========================================================

    nearest = df.iloc[0]


    st.success(
        f"🚔 La estación más cercana es: "
        f"**{nearest['Estación']}**"
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Distancia",
            f"{nearest['Distancia (km)']} km"
        )


    with col2:

        st.metric(
            "Tiempo estimado",
            nearest["Tiempo estimado"]
        )


    with col3:

        st.metric(
            "Transporte",
            mode
        )


    # ========================================================
    # MAPA
    # ========================================================

    st.subheader("🗺️ Mapa de estaciones")


    mapa = folium.Map(

        location=user_coords,

        zoom_start=14
    )


    # --------------------------------------------------------
    # UBICACIÓN DEL USUARIO
    # --------------------------------------------------------

    folium.Marker(

        location=user_coords,

        popup=folium.Popup(

            f"""
            <b>📍 Mi ubicación</b><br><br>

            Latitud: {latitude}<br>

            Longitud: {longitude}
            """,

            max_width=300
        ),

        tooltip="Mi ubicación",

        icon=folium.Icon(

            color="red",

            icon="user"
        )

    ).add_to(mapa)


    # --------------------------------------------------------
    # ESTACIONES
    # --------------------------------------------------------

    for _, row in df.iterrows():

        popup = f"""

        <b>🚔 {row['Estación']}</b><br><br>

        <b>Código Plus:</b>
        {row['Código Plus']}<br><br>

        <b>Latitud:</b>
        {row['Latitud']}<br>

        <b>Longitud:</b>
        {row['Longitud']}<br><br>

        <b>Distancia:</b>
        {row['Distancia (km)']} km<br>

        <b>Tiempo:</b>
        {row['Tiempo estimado']}

        """


        folium.Marker(

            location=[
                row["Latitud"],
                row["Longitud"]
            ],

            popup=folium.Popup(
                popup,
                max_width=350
            ),

            tooltip=row["Estación"],

            icon=folium.Icon(
                color="blue",
                icon="home"
            )

        ).add_to(mapa)


    # ========================================================
    # MOSTRAR MAPA
    # ========================================================

    st_folium(
        mapa,
        width=1200,
        height=600
    )


else:

    st.info(
        "👈 Introduce tu latitud y longitud "
        "y presiona **Buscar estaciones**."
    )
