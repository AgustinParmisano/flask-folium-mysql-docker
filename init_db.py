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
                    ciudad VARCHAR(255) NOT NULL
                )
            """)

            cursor.execute("""
                INSERT INTO puntos (latitud, longitud, nombre, ciudad) 
                VALUES 
                (-34.6037, -58.3816, 'Obelisco', 'Buenos Aires'),
                (-34.6076, -58.4376, 'Parque Centenario', 'Buenos Aires'),
                (-34.5863, -58.3917, 'Recoleta', 'Buenos Aires')
            """)

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