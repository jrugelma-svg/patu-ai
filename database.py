import os
from supabase import create_client, Client

# Conexión a Supabase usando variables de entorno o Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================================================================
# LISTA DE CORREOS VIP / DESARROLLADORES (ACCESO ILIMITADO AUTOMÁTICO)
# Coloca aquí los correos reales de tu equipo (incluso antes de que se registren).
# ==============================================================================
ADMIN_EMAILS = [
    "jrugelma@ucvvirtual.edu.pe",  # Tu correo principal
    "desarrollador2@ejemplo.com",   # Correo 2
    "desarrollador3@ejemplo.com",   # Correo 3
    "desarrollador4@ejemplo.com",   # Correo 4
    "desarrollador5@ejemplo.com",   # Correo 5
    "desarrollador6@ejemplo.com",   # Correo 6
]

def registrar_usuario(nombre, email, password):
    """
    Registra un nuevo usuario mediante Supabase Auth.
    Supabase enviará automáticamente un correo de confirmación.
    """
    supabase = get_supabase()
    email_clean = email.lower().strip()
    
    lista_vip = [e.lower().strip() for e in ADMIN_EMAILS]
    plan_inicial = "admin" if email_clean in lista_vip else "free"
    
    try:
        # 1. Registrar usuario en Supabase Auth
        res_auth = supabase.auth.sign_up({
            "email": email_clean,
            "password": password,
            "options": {
                "data": {
                    "nombre": nombre,
                    "plan": plan_inicial
                }
            }
        })
        
        # 2. Guardar datos complementarios en la tabla de usuarios
        if res_auth.user:
            data_tabla = {
                "id": res_auth.user.id,
                "id_auth": res_auth.user.id,
                "nombre": nombre,
                "email": email_clean,
                "password_hash": "SUPABASE_AUTH_MANAGED",
                "plan": plan_inicial
            }
            try:
                supabase.table("usuarios").insert(data_tabla).execute()
            except Exception as e_db:
                print("Nota en tabla usuarios:", e_db)

        return True, "📧 Te hemos enviado un correo de confirmación. Por favor revisa tu bandeja de entrada (o carpeta de SPAM) y confirma tu cuenta antes de iniciar sesión."
        
    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower() or "unique" in msg.lower():
            return False, "Este correo electrónico ya está registrado."
        return False, f"Error al registrar: {msg}"

def verificar_login(email, password):
    """
    Verifica las credenciales mediante Supabase Auth.
    Si el correo no ha sido verificado, rehusará el inicio de sesión.
    """
    supabase = get_supabase()
    email_clean = email.lower().strip()
    
    try:
        # Intentar iniciar sesión en Supabase Auth
        res_auth = supabase.auth.sign_in_with_password({
            "email": email_clean,
            "password": password
        })
        
        user_auth = res_auth.user
        
        if user_auth:
            # Comprobar si el correo está confirmado
            if not user_auth.email_confirmed_at and user_auth.confirmed_at is None:
                return False, "⚠️ Tu correo aún no ha sido verificado. Por favor revisa tu bandeja de entrada para confirmar tu cuenta."
            
            # Obtener datos adicionales del perfil
            nombre = user_auth.user_metadata.get("nombre", "Usuario")
            
            lista_vip = [e.lower().strip() for e in ADMIN_EMAILS]
            plan_final = "admin" if email_clean in lista_vip else user_auth.user_metadata.get("plan", "free")
            
            return True, {
                "id": user_auth.id,
                "nombre": nombre,
                "email": user_auth.email,
                "plan": plan_final
            }
            
    except Exception as e:
        msg = str(e)
        if "Email not confirmed" in msg:
            return False, "⚠️ Debes verificar tu correo antes de ingresar. Revisa tu bandeja de entrada."
        if "Invalid login credentials" in msg:
            return False, "Correo o contraseña incorrectos."
        return False, f"Error de autenticación: {msg}"

    return False, "Correo o contraseña incorrectos."

def guardar_historial(usuario_id, tipo_registro, titulo, contenido):
    """Guarda un registro en la base de datos de Supabase."""
    supabase = get_supabase()
    try:
        data = {
            "usuario_id": str(usuario_id),
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
        res = supabase.table("historial_clinico").select("*").eq("usuario_id", str(usuario_id)).order("fecha", desc=True).execute()
        registros = []
        for r in res.data:
            registros.append((r["id"], r["tipo_registro"], r["titulo"], r["contenido"], r["fecha"]))
        return registros
    except Exception as e:
        print("Error obteniendo historial:", e)
        return []
