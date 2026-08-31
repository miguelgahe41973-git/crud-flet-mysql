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
# Acepta tanto los nombres propios (DB_HOST, DB_USER, etc.)
# como los nombres que Railway genera automáticamente para
# su plugin de MySQL (MYSQLHOST, MYSQLUSER, etc.), para no
# depender de renombrar variables en la interfaz de Railway.
# Si no existe ninguna, usa valores locales (XAMPP/WAMP).
# ============================================
DB_CONFIG = {
    "host": os.environ.get("DB_HOST") or os.environ.get("MYSQLHOST", "localhost"),
    "user": os.environ.get("DB_USER") or os.environ.get("MYSQLUSER", "root"),
    "password": os.environ.get("DB_PASSWORD") or os.environ.get("MYSQLPASSWORD", ""),
    "database": os.environ.get("DB_NAME") or os.environ.get("MYSQLDATABASE", "crud_flet"),
    "port": int(os.environ.get("DB_PORT") or os.environ.get("MYSQLPORT", 3306)),
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
    """Devuelve una lista de todos los productos ACTIVOS (no eliminados lógicamente)."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE activo = TRUE ORDER BY id DESC")
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
    """Borrado LÓGICO: marca el producto como inactivo, no lo borra de la base de datos."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET activo = FALSE WHERE id = %s", (id_producto,))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al eliminar producto: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def restaurar_producto(id_producto):
    """Restaura un producto previamente eliminado (lo vuelve a marcar como activo)."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET activo = TRUE WHERE id = %s", (id_producto,))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al restaurar producto: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def obtener_productos_eliminados():
    """Devuelve los productos marcados como inactivos (eliminados lógicamente)."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM productos WHERE activo = FALSE ORDER BY id DESC")
        resultado = cursor.fetchall()
        return resultado
    except Error as e:
        print(f"Error al obtener productos eliminados: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def eliminar_producto_definitivo(id_producto):
    """Borrado FÍSICO permanente. Úsalo solo si de verdad quieres borrar el registro para siempre."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos WHERE id = %s", (id_producto,))
        conn.commit()
        return True
    except Error as e:
        print(f"Error al eliminar producto definitivamente: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
