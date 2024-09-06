import time
import mysql.connector
import os

def wait_for_db():
    db_config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'user': os.environ.get('MYSQL_USER', 'user'),
        'password': os.environ.get('MYSQL_PASSWORD', 'password'),
        'database': os.environ.get('MYSQL_DB', 'mapdb')
    }

    while True:
        try:
            conn = mysql.connector.connect(**db_config)
            conn.close()
            print("Database is ready!")
            break
        except mysql.connector.Error as err:
            print("Waiting for database...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_db()