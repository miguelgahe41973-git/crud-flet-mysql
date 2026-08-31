"""
database.py
Capa de acceso a datos (MySQL) para el CRUD de productos.
Requiere: pip install mysql-connector-python
"""

import os
import hashlib
import secrets
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


# ============================================
# AUTENTICACIÓN DE USUARIOS
# ============================================

def hash_password(password, salt=None):
    """Genera un hash seguro de la contraseña usando PBKDF2 (librería estándar, sin dependencias extra)."""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000)
    return f"{salt}${hash_bytes.hex()}"


def verificar_password(password, password_hash_guardado):
    """Compara una contraseña en texto plano contra el hash guardado en la base de datos."""
    try:
        salt, hash_guardado = password_hash_guardado.split("$")
        hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000)
        return hash_bytes.hex() == hash_guardado
    except (ValueError, AttributeError):
        return False


def verificar_login(username, password):
    """
    Verifica usuario y contraseña contra la base de datos.
    Devuelve el diccionario del usuario si es correcto, o None si no.
    """
    if not username or not password:
        return None
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE username = %s AND activo = TRUE", (username,)
        )
        usuario = cursor.fetchone()
        if usuario and verificar_password(password, usuario["password_hash"]):
            usuario.pop("password_hash")  # nunca regresar el hash a la interfaz
            return usuario
        return None
    except Error as e:
        print(f"Error al verificar login: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def crear_usuario(username, password, nombre, perfil="Usuario"):
    """Crea un nuevo usuario con contraseña cifrada y un perfil asignado."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, nombre, perfil) VALUES (%s, %s, %s, %s)",
            (username, hash_password(password), nombre, perfil),
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error al crear usuario: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def obtener_usuarios():
    """Devuelve todos los usuarios (sin el hash de contraseña)."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, nombre, perfil, activo, fecha_creacion FROM usuarios ORDER BY id"
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def actualizar_usuario(id_usuario, nombre, perfil, activo, password=None):
    """
    Actualiza nombre, perfil y estado de un usuario.
    Si se manda 'password', también actualiza la contraseña; si no, la deja igual.
    """
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        if password:
            cursor.execute(
                "UPDATE usuarios SET nombre = %s, perfil = %s, activo = %s, password_hash = %s WHERE id = %s",
                (nombre, perfil, activo, hash_password(password), id_usuario),
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET nombre = %s, perfil = %s, activo = %s WHERE id = %s",
                (nombre, perfil, activo, id_usuario),
            )
        conn.commit()
        return True
    except Error as e:
        print(f"Error al actualizar usuario: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def existe_username(username, excluir_id=None):
    """Verifica si un nombre de usuario ya está en uso (para validar antes de crear/editar)."""
    conn = get_connection()
    if conn is None:
        return True  # por seguridad, si no se puede verificar, se bloquea
    try:
        cursor = conn.cursor()
        if excluir_id:
            cursor.execute(
                "SELECT id FROM usuarios WHERE username = %s AND id != %s", (username, excluir_id)
            )
        else:
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        return cursor.fetchone() is not None
    except Error as e:
        print(f"Error al verificar username: {e}")
        return True
    finally:
        cursor.close()
        conn.close()
