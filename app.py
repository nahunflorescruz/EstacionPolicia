import ipywidgets as widgets
from IPython.display import display, HTML
from geopy.distance import great_circle
import folium
import pandas as pd

# La lista de estaciones de policía (asegúrate de que esta lista esté definida en tu entorno)
# Puedes copiar la definición de 'police_stations_honduras' de la celda 0a0b98e8 si la necesitas.
# Por ejemplo:
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

# Crear widgets de entrada para latitud y longitud
latitude_input = widgets.FloatText(
    value=14.0833, # Valor predeterminado cerca de Tegucigalpa
    description='Latitud:',
    disabled=False
)

longitude_input = widgets.FloatText(
    value=-87.2000, # Valor predeterminado cerca de Tegucigalpa
    description='Longitud:',
    disabled=False
)

# Dropdown para el modo de transporte
travel_mode_selector = widgets.Dropdown(
    options=['Carro', 'Bicicleta', 'Caminando'],
    value='Carro',
    description='Modo de viaje:',
    disabled=False,
)

# Crear botón para calcular y mostrar
search_button = widgets.Button(description='Buscar Estaciones Cercanas')

# Crear un widget de salida para mostrar los resultados
output = widgets.Output()

# Función para estimar el tiempo de viaje (simulada)
def get_estimated_travel_time(distance_km, mode):
    if mode == 'Carro':
        # Suponiendo una velocidad promedio de 60 km/h
        time_hours = distance_km / 60
    elif mode == 'Bicicleta':
        # Suponiendo una velocidad promedio de 15 km/h
        time_hours = distance_km / 15
    elif mode == 'Caminando':
        # Suponiendo una velocidad promedio de 5 km/h
        time_hours = distance_km / 5
    else:
        return "N/A"

    if time_hours < 1:
        return f"{round(time_hours * 60)} min"
    else:
        return f"{round(time_hours, 1)} horas"

# Función que se ejecuta al presionar el botón
def on_search_button_clicked(b):
    with output:
        output.clear_output()
        user_lat = latitude_input.value
        user_lon = longitude_input.value
        selected_mode = travel_mode_selector.value

        # Validar si las coordenadas son válidas (simple validación)
        if not (-90 <= user_lat <= 90 and -180 <= user_lon <= 180):
            print("Por favor, introduce coordenadas válidas (Latitud entre -90 y 90, Longitud entre -180 y 180).")
            return

        user_coords = (user_lat, user_lon)
        station_distances = []

        # Calcular distancias a todas las estaciones de policía
        for station in police_stations_honduras:
            station_coords = (station['latitude'], station['longitude'])
            distance = great_circle(user_coords, station_coords).km
            estimated_time = get_estimated_travel_time(distance, selected_mode)
            station_distances.append({
                'name': station['name'],
                'latitude': station['latitude'],
                'longitude': station['longitude'],
                'distance_km': round(distance, 2),
                f'tiempo_est_{selected_mode}': estimated_time
            })

        # Ordenar por distancia
        df_closest_stations = pd.DataFrame(station_distances)
        df_closest_stations_sorted = df_closest_stations.sort_values(by='distance_km').reset_index(drop=True)

        print(f"\nEstaciones de policía más cercanas a ({user_lat}, {user_lon}) por {selected_mode}:")
        display(df_closest_stations_sorted)

        # Crear mapa interactivo con Folium
        m = folium.Map(location=user_coords, zoom_start=10)

        # Añadir marcador para la ubicación del usuario
        folium.Marker(
            location=user_coords,
            popup='Tu Ubicación',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

        # Añadir marcadores para las estaciones de policía
        for idx, row in df_closest_stations_sorted.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"{row['name']} ({row['distance_km']} km) - Tiempo est. ({selected_mode}): {row[f'tiempo_est_{selected_mode}']}",
                icon=folium.Icon(color='blue', icon='flag')
            ).add_to(m)

        # Mostrar el mapa
        display(m)

# Asignar la función al evento de clic del botón
search_button.on_click(on_search_button_clicked)

# Mostrar los widgets
display(latitude_input, longitude_input, travel_mode_selector, search_button, output)
