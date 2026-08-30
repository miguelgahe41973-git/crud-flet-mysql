"""
database.py
Capa de acceso a datos (MySQL) para el CRUD de productos.
Requiere: pip install mysql-connector-python
"""

import os
import mysql.connector
from mysql.connector import Error

# ============================================
# CONFIGURACIÓN DE CONEXIÓN
# Lee las credenciales desde variables de entorno
# (necesario para desplegar en Render/Railway/etc.)
# Si no existen, usa valores locales por defecto
# para seguir funcionando en tu PC con XAMPP/WAMP.
# ============================================
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "crud_flet"),
    "port": int(os.environ.get("DB_PORT", 3306)),
}


def get_connection():
    """Crea y devuelve una nueva conexión a la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


def obtener_productos():
    """Devuelve una lista de todos los productos (como diccionarios)."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos ORDER BY id DESC")
        resultado = cursor.fetchall()
        return resultado
    except Error as e:
        print(f"Error al obtener productos: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def agregar_producto(nombre, descripcion, precio, cantidad):
    """Inserta un nuevo producto. Devuelve True/False según el resultado."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO productos (nombre, descripcion, precio, cantidad)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, descripcion, precio, cantidad))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al agregar producto: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def actualizar_producto(id_producto, nombre, descripcion, precio, cantidad):
    """Actualiza un producto existente por su id."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        query = """
            UPDATE productos
            SET nombre = %s, descripcion = %s, precio = %s, cantidad = %s
            WHERE id = %s
        """
        cursor.execute(query, (nombre, descripcion, precio, cantidad, id_producto))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al actualizar producto: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def eliminar_producto(id_producto):
    """Elimina un producto por su id."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id_producto,))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al eliminar producto: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
