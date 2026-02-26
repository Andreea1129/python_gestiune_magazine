import mysql.connector
from mysql.connector import Error

# IMPORTANT: port 3306 = MySQL (port 5000 = Flask)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "bd*Genu2004",
    "database": "gestiune_magazine",
    "port": 3306,
}


def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_all_dict(sql: str, params=None):
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchall()
    finally:
        if cur is not None:
            cur.close()
        if conn is not None and conn.is_connected():
            conn.close()


def fetch_one_dict(sql: str, params=None):
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        return cur.fetchone()
    finally:
        if cur is not None:
            cur.close()
        if conn is not None and conn.is_connected():
            conn.close()


def execute(sql: str, params=None):
    """Executa INSERT/UPDATE/DELETE. Returneaza numarul de randuri afectate."""
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, params or ())
        conn.commit()
        return cur.rowcount
    except Error:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if cur is not None:
            cur.close()
        if conn is not None and conn.is_connected():
            conn.close()
