import psycopg2
from config import Config


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            client_encoding='UTF8'
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None