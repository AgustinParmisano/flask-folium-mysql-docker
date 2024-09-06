import os
from flask import Flask, render_template, request
import folium
import mysql.connector
from folium.plugins import MarkerCluster

app = Flask(__name__)

# Configuración de la conexión a la base de datos MySQL usando variables de entorno
db_config = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'user'),
    'password': os.environ.get('MYSQL_PASSWORD', 'password'),
    'database': os.environ.get('MYSQL_DB', 'mapdb')
}

def crear_mapa_buenos_aires():
    m = folium.Map(location=[-34.6037, -58.3816], zoom_start=11)
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    cursor.execute("SELECT latitud, longitud, nombre FROM puntos WHERE ciudad = 'Buenos Aires'")
    puntos = cursor.fetchall()

    marker_cluster = MarkerCluster().add_to(m)

    for punto in puntos:
        folium.Marker(
            location=[punto[0], punto[1]],
            popup=punto[2],
            tooltip=punto[2]
        ).add_to(marker_cluster)

    cursor.close()
    conn.close()

    return m

@app.route('/')
def index():
    return render_template('base.html', titulo='Página Principal', contenido='Bienvenido a la página principal')

@app.route('/mapa_buenos_aires')
def mapa_buenos_aires():
    return render_template('base.html', titulo='Mapa de Buenos Aires', mostrar_mapa=True)

@app.route('/otra_pagina')
def otra_pagina():
    return render_template('base.html', titulo='Otra Página', contenido='Contenido de otra página')

@app.route('/mapa_iframe')
def mapa_iframe():
    mapa = crear_mapa_buenos_aires()
    return mapa._repr_html_()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)