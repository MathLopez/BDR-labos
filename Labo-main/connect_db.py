import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "votre_base",
    "user": "votre_utilisateur",
    "password": "votre_mot_de_passe",
    "host": "localhost",
    "port": "5432",
}

def get_db_connection():
    return psycopg2.connect(cursor_factory=RealDictCursor, **DB_CONFIG)
