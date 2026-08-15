import os
from supabase import create_client, Client
import bcrypt

# Conexión a Supabase usando variables de entorno o Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# LISTA DE CORREOS VIP / DESARROLLADORES (ACCESO ILIMITADO)
# Agrega o modifica aquí los 6 correos exactos de tu equipo:
# =========================================================
ADMIN_EMAILS = [
    "admin@patu.ai",
    "desarrollador1@patu.ai",
    "desarrollador2@patu.ai",
    "desarrollador3@patu.ai",
    "desarrollador4@patu.ai",
    "desarrollador5@patu.ai",
]

def registrar_usuario(nombre, email, password):
    """Registra un nuevo usuario en Supabase."""
    supabase = get_supabase()
    email_clean = email.lower().strip()
    
    # Asignar rol 'admin' automáticamente si el correo está en la lista VIP
    plan_inicial = "admin" if email_clean in [e.lower() for e in ADMIN_EMAILS] else "free"
    
    # Encriptar contraseña
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    try:
        data = {
            "nombre": nombre,
            "email": email_clean,
            "password_hash": password_hash,
            "plan": plan_inicial
        }
        res = supabase.table("usuarios").insert(data).execute()
        return True, "¡Cuenta creada exitosamente! Ya puedes iniciar sesión."
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return False, "El correo electrónico ya está registrado."
        return False, f"Error al registrar: {str(e)}"

def verificar_login(email, password):
    """Verifica las credenciales en Supabase."""
    supabase = get_supabase()
    email_clean = email.lower().strip()
    
    try:
        res = supabase.table("usuarios").select("*").eq("email", email_clean).execute()
        if res.data and len(res.data) > 0:
            usuario = res.data[0]
            if bcrypt.checkpw(password.encode('utf-8'), usuario["password_hash"].encode('utf-8')):
                # Garantizar plan 'admin' si el correo es VIP
                plan_final = "admin" if email_clean in [e.lower() for e in ADMIN_EMAILS] else usuario["plan"]
                return True, {
                    "id": usuario["id"],
                    "nombre": usuario["nombre"],
                    "email": usuario["email"],
                    "plan": plan_final
                }
    except Exception as e:
        print("Error en login:", e)
        
    return False, "Correo o contraseña incorrectos."

def guardar_historial(usuario_id, tipo_registro, titulo, contenido):
    """Guarda un registro en la base de datos remota de Supabase."""
    supabase = get_supabase()
    try:
        data = {
            "usuario_id": usuario_id,
            "tipo_registro": tipo_registro,
            "titulo": titulo,
            "contenido": contenido
        }
        supabase.table("historial_clinico").insert(data).execute()
    except Exception as e:
        print("Error guardando historial:", e)

def obtener_historial_usuario(usuario_id):
    """Obtiene el historial persistente desde Supabase."""
    supabase = get_supabase()
    try:
        res = supabase.table("historial_clinico").select("*").eq("usuario_id", usuario_id).order("fecha", desc=True).execute()
        registros = []
        for r in res.data:
            registros.append((r["id"], r["tipo_registro"], r["titulo"], r["contenido"], r["fecha"]))
        return registros
    except Exception as e:
        print("Error obteniendo historial:", e)
        return []
