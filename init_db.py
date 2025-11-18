import mysql.connector
import os
import time

def init_db():
    db_config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'user': os.environ.get('MYSQL_USER', 'user'),
        'password': os.environ.get('MYSQL_PASSWORD', 'password'),
        'database': os.environ.get('MYSQL_DB', 'mapdb')
    }

    max_retries = 30
    for _ in range(max_retries):
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS puntos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    latitud DECIMAL(10, 8) NOT NULL,
                    longitud DECIMAL(11, 8) NOT NULL,
                    nombre VARCHAR(255) NOT NULL,
                    ciudad VARCHAR(255) NOT NULL,
                    tipo VARCHAR(50) DEFAULT 'punto'
                )
            """)

            # Verificar si la columna 'tipo' existe, si no, agregarla
            cursor.execute("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'puntos' 
                AND COLUMN_NAME = 'tipo'
            """)
            if cursor.fetchone()[0] == 0:
                cursor.execute("ALTER TABLE puntos ADD COLUMN tipo VARCHAR(50) DEFAULT 'punto'")

            # Verificar si ya existen datos para evitar duplicados
            cursor.execute("SELECT COUNT(*) FROM puntos")
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute("""
                    INSERT INTO puntos (latitud, longitud, nombre, ciudad, tipo) 
                    VALUES 
                    -- Buenos Aires
                    (-34.6037, -58.3816, 'Obelisco', 'Buenos Aires', 'edificio'),
                    (-34.6076, -58.4376, 'Parque Centenario', 'Buenos Aires', 'zona'),
                    (-34.5863, -58.3917, 'Recoleta', 'Buenos Aires', 'zona'),
                    -- La Plata - Edificios
                    (-34.9215, -57.9545, 'Catedral de La Plata', 'La Plata', 'edificio'),
                    (-34.9200, -57.9500, 'Edificio Municipal', 'La Plata', 'edificio'),
                    (-34.9180, -57.9520, 'Teatro Argentino', 'La Plata', 'edificio'),
                    -- La Plata - Parques (4 parques principales)
                    (-34.9100, -57.9500, 'Paseo del Bosque', 'La Plata', 'parque'),
                    (-34.9300, -57.9600, 'Parque Saavedra', 'La Plata', 'parque'),
                    (-34.9150, -57.9400, 'Parque Vucetich', 'La Plata', 'parque'),
                    (-34.9250, -57.9450, 'Parque San Martín', 'La Plata', 'parque'),
                    -- La Plata - Zonas
                    (-34.9190, -57.9550, 'Plaza Moreno', 'La Plata', 'zona'),
                    -- La Plata - Cables de Fibra Óptica
                    (-34.9220, -57.9530, 'Punto Fibra 1', 'La Plata', 'fibra_optica'),
                    (-34.9205, -57.9520, 'Punto Fibra 2', 'La Plata', 'fibra_optica'),
                    (-34.9195, -57.9510, 'Punto Fibra 3', 'La Plata', 'fibra_optica'),
                    (-34.9180, -57.9500, 'Punto Fibra 4', 'La Plata', 'fibra_optica')
                """)
                print("Datos de ejemplo insertados correctamente")
            else:
                print(f"La base de datos ya contiene {count} registros. Omitiendo inserción de datos de ejemplo.")

            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully!")
            break
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            print("Retrying in 1 second...")
            time.sleep(1)
    else:
        print("Failed to initialize database after multiple attempts")

if __name__ == "__main__":
    init_db()