import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = "patu_workstation.db"

def init_db():
    """Inicializa la base de datos y crea las tablas si no existen."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de Usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            plan TEXT DEFAULT 'free',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de Historial / Registros de Pacientes y Análisis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_clinico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo_registro TEXT NOT NULL,
            titulo TEXT NOT NULL,
            contenido TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def registrar_usuario(nombre, email, password):
    """Registra un nuevo usuario con contraseña encriptada."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password_hash, plan) VALUES (?, ?, ?, 'free')",
            (nombre, email.lower().strip(), password_hash)
        )
        conn.commit()
        conn.close()
        return True, "¡Cuenta creada exitosamente! Ya puedes iniciar sesión."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El correo electrónico ya está registrado."
    except Exception as e:
        conn.close()
        return False, f"Error al registrar: {str(e)}"

def verificar_login(email, password):
    """Verifica las credenciales del usuario."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nombre, email, password_hash, plan FROM usuarios WHERE email = ?", (email.lower().strip(),))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        user_id, nombre, email_db, pass_hash, plan = usuario
        if bcrypt.checkpw(password.encode('utf-8'), pass_hash.encode('utf-8')):
            return True, {
                "id": user_id,
                "nombre": nombre,
                "email": email_db,
                "plan": plan
            }
    return False, "Correo o contraseña incorrectos."

def guardar_historial(usuario_id, tipo_registro, titulo, contenido):
    """Guarda una actividad o informe en el historial del usuario."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historial_clinico (usuario_id, tipo_registro, titulo, contenido) VALUES (?, ?, ?, ?)",
        (usuario_id, tipo_registro, titulo, contenido)
    )
    conn.commit()
    conn.close()

def obtener_historial_usuario(usuario_id):
    """Recupera todo el historial guardado del usuario logueado."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, tipo_registro, titulo, contenido, fecha FROM historial_clinico WHERE usuario_id = ? ORDER BY fecha DESC",
        (usuario_id,)
    )
    registros = cursor.fetchall()
    conn.close()
    return registros

# Inicializar DB al importar
init_db()
