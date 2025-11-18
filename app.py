import os
import csv
from flask import Flask, render_template, request, jsonify
import folium
import mysql.connector
from folium.plugins import MarkerCluster
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'csv', 'json'}

# Configuración de la conexión a la base de datos MySQL usando variables de entorno
db_config = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'user'),
    'password': os.environ.get('MYSQL_PASSWORD', 'password'),
    'database': os.environ.get('MYSQL_DB', 'mapdb')
}

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def leer_csv(archivo_path):
    """Lee un archivo CSV y retorna una lista de diccionarios"""
    datos = []
    try:
        with open(archivo_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                datos.append(row)
        return datos
    except Exception as e:
        print(f"Error al leer CSV: {e}")
        return []

def obtener_conexion():
    """Obtiene una conexión a la base de datos"""
    return mysql.connector.connect(**db_config)

def importar_edificios(capa, ciudad=None):
    """
    Importa edificios desde la base de datos y los agrega a la capa especificada.
    
    Args:
        capa: FeatureGroup de Folium donde se agregarán los edificios
        ciudad: (opcional) Filtrar por ciudad específica
    """
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        if ciudad:
            query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'edificio' AND ciudad = %s"
            cursor.execute(query, (ciudad,))
        else:
            query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'edificio'"
            cursor.execute(query)
        
        edificios = cursor.fetchall()
        
        marker_cluster_edificios = MarkerCluster().add_to(capa)
        
        for edificio in edificios:
            folium.Marker(
                location=[edificio[0], edificio[1]],
                popup=edificio[2],
                tooltip=edificio[2],
                icon=folium.Icon(color='blue', icon='building', prefix='fa')
            ).add_to(marker_cluster_edificios)
        
        cursor.close()
        conn.close()
        print(f"✓ {len(edificios)} edificios importados")
        return len(edificios)
    except Exception as e:
        print(f"✗ Error al importar edificios: {e}")
        return 0


def trazar_zona_alrededor_punto(lat, lon, nombre, radio_metros, capa, color='green', fill_opacity=0.2):
    """
    Traza una zona circular alrededor de un punto.
    
    Args:
        lat: Latitud del punto central
        lon: Longitud del punto central
        nombre: Nombre de la zona
        radio_metros: Radio en metros (5 cuadras ≈ 500 metros)
        capa: FeatureGroup de Folium donde se agregará la zona
        color: Color del borde de la zona
        fill_opacity: Opacidad del relleno (0-1)
    """
    folium.Circle(
        location=[lat, lon],
        radius=radio_metros,
        popup=f'{nombre} - Zona de {radio_metros}m',
        tooltip=nombre,
        color=color,
        fillColor=color,
        fillOpacity=fill_opacity,
        weight=3
    ).add_to(capa)
    
    # Agregar marcador en el centro
    folium.Marker(
        location=[lat, lon],
        popup=nombre,
        tooltip=nombre,
        icon=folium.Icon(color='darkgreen', icon='tree', prefix='fa')
    ).add_to(capa)


def importar_zonas_parques(capa, ciudad=None, cuadras_alrededor=5):
    """
    Importa parques desde la base de datos y traza zonas alrededor de ellos.
    
    Args:
        capa: FeatureGroup de Folium donde se agregarán las zonas
        ciudad: (opcional) Filtrar por ciudad específica
        cuadras_alrededor: Número de cuadras alrededor del parque (por defecto 5)
    """
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # Buscar parques (tipo 'parque' o puntos con nombre que contenga 'parque')
        if ciudad:
            query = """
                SELECT latitud, longitud, nombre, tipo 
                FROM puntos 
                WHERE (tipo = 'parque' OR LOWER(nombre) LIKE '%parque%') 
                AND ciudad = %s
            """
            cursor.execute(query, (ciudad,))
        else:
            query = """
                SELECT latitud, longitud, nombre, tipo 
                FROM puntos 
                WHERE tipo = 'parque' OR LOWER(nombre) LIKE '%parque%'
            """
            cursor.execute(query)
        
        parques = cursor.fetchall()
        
        # Calcular radio en metros (1 cuadra ≈ 100 metros en La Plata)
        radio_metros = cuadras_alrededor * 100
        
        for parque in parques:
            trazar_zona_alrededor_punto(
                lat=parque[0],
                lon=parque[1],
                nombre=parque[2],
                radio_metros=radio_metros,
                capa=capa,
                color='green',
                fill_opacity=0.2
            )
        
        cursor.close()
        conn.close()
        print(f"✓ {len(parques)} zonas de parques trazadas ({cuadras_alrededor} cuadras de radio)")
        return len(parques)
    except Exception as e:
        print(f"✗ Error al importar zonas de parques: {e}")
        return 0


def importar_zonas_genericas(capa, ciudad=None):
    """
    Importa zonas genéricas desde la base de datos.
    
    Args:
        capa: FeatureGroup de Folium donde se agregarán las zonas
        ciudad: (opcional) Filtrar por ciudad específica
    """
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        if ciudad:
            query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'zona' AND ciudad = %s"
            cursor.execute(query, (ciudad,))
        else:
            query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'zona'"
            cursor.execute(query)
        
        zonas = cursor.fetchall()
        
        for zona in zonas:
            folium.CircleMarker(
                location=[zona[0], zona[1]],
                radius=50,
                popup=zona[2],
                tooltip=zona[2],
                color='green',
                fillColor='green',
                fillOpacity=0.3,
                weight=2
            ).add_to(capa)
        
        cursor.close()
        conn.close()
        print(f"✓ {len(zonas)} zonas genéricas importadas")
        return len(zonas)
    except Exception as e:
        print(f"✗ Error al importar zonas genéricas: {e}")
        return 0


def importar_cables_fibra_optica(capa, ciudad=None):
    """
    Importa cables de fibra óptica desde la base de datos.
    
    Args:
        capa: FeatureGroup de Folium donde se agregarán los cables
        ciudad: (opcional) Filtrar por ciudad específica
    """
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        if ciudad:
            query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'fibra_optica' AND ciudad = %s ORDER BY id"
            cursor.execute(query, (ciudad,))
        else:
            query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'fibra_optica' ORDER BY id"
            cursor.execute(query)
        
        cables = cursor.fetchall()
        
        # Si hay cables, crear líneas entre puntos consecutivos
        if len(cables) > 1:
            puntos_cable = [[cable[0], cable[1]] for cable in cables]
            folium.PolyLine(
                puntos_cable,
                color='orange',
                weight=4,
                opacity=0.7,
                popup='Cable de Fibra Óptica',
                tooltip='Cable de Fibra Óptica'
            ).add_to(capa)
        
        # Agregar marcadores para cada punto del cable
        for cable in cables:
            folium.Marker(
                location=[cable[0], cable[1]],
                popup=cable[2] if cable[2] else 'Punto de Fibra Óptica',
                tooltip=cable[2] if cable[2] else 'Punto de Fibra Óptica',
                icon=folium.Icon(color='orange', icon='wifi', prefix='fa')
            ).add_to(capa)
        
        cursor.close()
        conn.close()
        print(f"✓ {len(cables)} puntos de fibra óptica importados")
        return len(cables)
    except Exception as e:
        print(f"✗ Error al importar cables de fibra óptica: {e}")
        return 0


def crear_mapa_la_plata():
    """
    Crea el mapa de La Plata con todas las capas importadas.
    """
    # Coordenadas de la Catedral de La Plata
    catedral_la_plata = [-34.9215, -57.9545]
    m = folium.Map(location=catedral_la_plata, zoom_start=14)
    
    # Agregar marcador en la Catedral de La Plata
    folium.Marker(
        location=catedral_la_plata,
        popup='Catedral de La Plata',
        tooltip='Catedral de La Plata',
        icon=folium.Icon(color='red', icon='church', prefix='fa')
    ).add_to(m)
    
    # Crear capas separadas para diferentes tipos de información
    capa_edificios = folium.FeatureGroup(name='Edificios', show=True)
    capa_zonas_parques = folium.FeatureGroup(name='Zonas de Parques (5 cuadras)', show=True)
    capa_zonas_genericas = folium.FeatureGroup(name='Zonas Genéricas', show=False)
    capa_fibra_optica = folium.FeatureGroup(name='Cables de Fibra Óptica', show=True)
    
    # Importar todas las capas
    print("Importando capas...")
    importar_edificios(capa_edificios, ciudad='La Plata')
    importar_zonas_parques(capa_zonas_parques, ciudad='La Plata', cuadras_alrededor=5)
    importar_zonas_genericas(capa_zonas_genericas, ciudad='La Plata')
    importar_cables_fibra_optica(capa_fibra_optica, ciudad='La Plata')
    
    # Agregar todas las capas al mapa
    capa_edificios.add_to(m)
    capa_zonas_parques.add_to(m)
    capa_zonas_genericas.add_to(m)
    capa_fibra_optica.add_to(m)
    
    # Agregar control de capas para activar/desactivar cada tipo
    folium.LayerControl().add_to(m)

    return m

@app.route('/')
def index():
    return render_template('base.html', titulo='Página Principal', contenido='Bienvenido a la página principal')

@app.route('/mapa_la_plata')
def mapa_la_plata():
    return render_template('mapa_interactivo.html', titulo='Mapa de La Plata')

@app.route('/mapa_buenos_aires')
def mapa_buenos_aires():
    return render_template('base.html', titulo='Mapa de Buenos Aires', mostrar_mapa=True)

@app.route('/otra_pagina')
def otra_pagina():
    return render_template('base.html', titulo='Otra Página', contenido='Contenido de otra página')

@app.route('/mapa_iframe')
def mapa_iframe():
    mapa = crear_mapa_la_plata()
    return mapa._repr_html_()

# Endpoints API para importar capas dinámicamente
@app.route('/api/edificios')
def api_edificios():
    """API endpoint para obtener edificios"""
    ciudad = request.args.get('ciudad', 'La Plata')
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'edificio' AND ciudad = %s"
        cursor.execute(query, (ciudad,))
        edificios = cursor.fetchall()
        
        resultado = []
        for edificio in edificios:
            resultado.append({
                'lat': float(edificio[0]),
                'lon': float(edificio[1]),
                'nombre': edificio[2],
                'tipo': edificio[3]
            })
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'count': len(resultado), 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/parques')
def api_parques():
    """API endpoint para obtener parques"""
    ciudad = request.args.get('ciudad', 'La Plata')
    cuadras = int(request.args.get('cuadras', 5))
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query = """
            SELECT latitud, longitud, nombre, tipo 
            FROM puntos 
            WHERE (tipo = 'parque' OR LOWER(nombre) LIKE '%parque%') 
            AND ciudad = %s
        """
        cursor.execute(query, (ciudad,))
        parques = cursor.fetchall()
        
        resultado = []
        for parque in parques:
            resultado.append({
                'lat': float(parque[0]),
                'lon': float(parque[1]),
                'nombre': parque[2],
                'tipo': parque[3],
                'radio_metros': cuadras * 100
            })
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'count': len(resultado), 'data': resultado, 'cuadras': cuadras})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/zonas')
def api_zonas():
    """API endpoint para obtener zonas genéricas"""
    ciudad = request.args.get('ciudad', 'La Plata')
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'zona' AND ciudad = %s"
        cursor.execute(query, (ciudad,))
        zonas = cursor.fetchall()
        
        resultado = []
        for zona in zonas:
            resultado.append({
                'lat': float(zona[0]),
                'lon': float(zona[1]),
                'nombre': zona[2],
                'tipo': zona[3]
            })
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'count': len(resultado), 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/fibra_optica')
def api_fibra_optica():
    """API endpoint para obtener cables de fibra óptica"""
    ciudad = request.args.get('ciudad', 'La Plata')
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query = "SELECT latitud, longitud, nombre, tipo FROM puntos WHERE tipo = 'fibra_optica' AND ciudad = %s ORDER BY id"
        cursor.execute(query, (ciudad,))
        cables = cursor.fetchall()
        
        resultado = []
        for cable in cables:
            resultado.append({
                'lat': float(cable[0]),
                'lon': float(cable[1]),
                'nombre': cable[2] if cable[2] else 'Punto de Fibra Óptica',
                'tipo': cable[3]
            })
        
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'count': len(resultado), 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Endpoints para importar desde archivos CSV
@app.route('/api/importar/edificios', methods=['POST'])
def api_importar_edificios():
    """Importa edificios desde un archivo CSV"""
    try:
        if 'file' not in request.files:
            # Si no hay archivo, intentar usar el archivo por defecto
            archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'edificios.csv')
            if os.path.exists(archivo_path):
                datos = leer_csv(archivo_path)
            else:
                return jsonify({'success': False, 'error': 'No se proporcionó archivo y no existe archivo por defecto'}), 400
        else:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                datos = leer_csv(filepath)
            else:
                return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
        
        resultado = []
        for row in datos:
            try:
                resultado.append({
                    'lat': float(row.get('latitud', row.get('lat', 0))),
                    'lon': float(row.get('longitud', row.get('lon', row.get('lng', 0)))),
                    'nombre': row.get('nombre', 'Sin nombre'),
                    'tipo': row.get('tipo', 'edificio')
                })
            except (ValueError, KeyError) as e:
                continue
        
        return jsonify({'success': True, 'count': len(resultado), 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/importar/parques', methods=['POST'])
def api_importar_parques():
    """Importa parques desde un archivo CSV"""
    try:
        cuadras = int(request.form.get('cuadras', 5))
        
        if 'file' not in request.files:
            # Si no hay archivo, intentar usar el archivo por defecto
            archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'parques.csv')
            if os.path.exists(archivo_path):
                datos = leer_csv(archivo_path)
            else:
                return jsonify({'success': False, 'error': 'No se proporcionó archivo y no existe archivo por defecto'}), 400
        else:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                datos = leer_csv(filepath)
            else:
                return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
        
        resultado = []
        for row in datos:
            try:
                resultado.append({
                    'lat': float(row.get('latitud', row.get('lat', 0))),
                    'lon': float(row.get('longitud', row.get('lon', row.get('lng', 0)))),
                    'nombre': row.get('nombre', 'Sin nombre'),
                    'tipo': row.get('tipo', 'parque'),
                    'radio_metros': cuadras * 100
                })
            except (ValueError, KeyError) as e:
                continue
        
        return jsonify({'success': True, 'count': len(resultado), 'data': resultado, 'cuadras': cuadras})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/importar/zonas', methods=['POST'])
def api_importar_zonas():
    """Importa zonas desde un archivo CSV"""
    try:
        if 'file' not in request.files:
            # Si no hay archivo, intentar usar el archivo por defecto
            archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'zonas.csv')
            if os.path.exists(archivo_path):
                datos = leer_csv(archivo_path)
            else:
                return jsonify({'success': False, 'error': 'No se proporcionó archivo y no existe archivo por defecto'}), 400
        else:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                datos = leer_csv(filepath)
            else:
                return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
        
        resultado = []
        for row in datos:
            try:
                resultado.append({
                    'lat': float(row.get('latitud', row.get('lat', 0))),
                    'lon': float(row.get('longitud', row.get('lon', row.get('lng', 0)))),
                    'nombre': row.get('nombre', 'Sin nombre'),
                    'tipo': row.get('tipo', 'zona')
                })
            except (ValueError, KeyError) as e:
                continue
        
        return jsonify({'success': True, 'count': len(resultado), 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/importar/fibra_optica', methods=['POST'])
def api_importar_fibra_optica():
    """Importa cables de fibra óptica desde un archivo CSV"""
    try:
        if 'file' not in request.files:
            # Si no hay archivo, intentar usar el archivo por defecto
            archivo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'fibra_optica.csv')
            if os.path.exists(archivo_path):
                datos = leer_csv(archivo_path)
            else:
                return jsonify({'success': False, 'error': 'No se proporcionó archivo y no existe archivo por defecto'}), 400
        else:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No se seleccionó archivo'}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(filepath)
                datos = leer_csv(filepath)
            else:
                return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
        
        resultado = []
        for row in datos:
            try:
                resultado.append({
                    'lat': float(row.get('latitud', row.get('lat', 0))),
                    'lon': float(row.get('longitud', row.get('lon', row.get('lng', 0)))),
                    'nombre': row.get('nombre', 'Punto de Fibra Óptica'),
                    'tipo': row.get('tipo', 'fibra_optica')
                })
            except (ValueError, KeyError) as e:
                continue
        
        return jsonify({'success': True, 'count': len(resultado), 'data': resultado})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)