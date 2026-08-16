import os
from supabase import create_client, Client

# Conexión a Supabase usando variables de entorno o Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# LÍMITE DE REGISTROS PARA USUARIOS GRATUITOS
LIMITE_REGISTROS_FREE = 4

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# ==============================================================================
# LISTA DE CORREOS VIP / DESARROLLADORES (ACCESO ILIMITADO AUTOMÁTICO)
# ==============================================================================
ADMIN_EMAILS = [
    "jrugelma@ucvvirtual.edu.pe",
    "desarrollador2@ejemplo.com",
    "desarrollador3@ejemplo.com",
    "desarrollador4@ejemplo.com",
    "desarrollador5@ejemplo.com",
    "desarrollador6@ejemplo.com",
]

def registrar_usuario(nombre, email, password):
    """
    Registra un nuevo usuario mediante Supabase Auth y sincroniza la tabla usuarios.
    """
    supabase = get_supabase()
    email_clean = email.lower().strip()
    
    lista_vip = [e.lower().strip() for e in ADMIN_EMAILS]
    plan_inicial = "admin" if email_clean in lista_vip else "free"
    
    try:
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
        
        if res_auth.user:
            user_id = str(res_auth.user.id)
            data_tabla = {
                "id": user_id,
                "id_auth": user_id,
                "nombre": nombre,
                "email": email_clean,
                "password_hash": "SUPABASE_AUTH_MANAGED",
                "plan": plan_inicial
            }
            try:
                supabase.table("usuarios").insert(data_tabla).execute()
            except Exception as e_db:
                print("Nota en sincronización de tabla usuarios:", e_db)

        return True, "📧 Te hemos enviado un correo de confirmación. Por favor revisa tu bandeja de entrada (o carpeta de SPAM) y confirma tu cuenta antes de iniciar sesión."
        
    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower() or "unique" in msg.lower():
            return False, "Este correo electrónico ya está registrado."
        return False, f"Error al registrar: {msg}"

def verificar_login(email, password):
    """
    Verifica las credenciales mediante Supabase Auth.
    """
    supabase = get_supabase()
    email_clean = email.lower().strip()
    
    try:
        res_auth = supabase.auth.sign_in_with_password({
            "email": email_clean,
            "password": password
        })
        
        user_auth = res_auth.user
        
        if user_auth:
            if not user_auth.email_confirmed_at and user_auth.confirmed_at is None:
                return False, "⚠️ Tu correo aún no ha sido verificado. Por favor revisa tu bandeja de entrada para confirmar tu cuenta."
            
            nombre = user_auth.user_metadata.get("nombre", "Usuario")
            lista_vip = [e.lower().strip() for e in ADMIN_EMAILS]
            plan_final = "admin" if email_clean in lista_vip else user_auth.user_metadata.get("plan", "free")
            
            return True, {
                "id": str(user_auth.id),
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

def verificar_limite_usuario(usuario_id, plan_usuario):
    """Verifica si el usuario alcanzó el límite de su plan."""
    if plan_usuario in ["admin", "premium"]:
        return True, "Acceso ilimitado"
    
    registros = obtener_historial_usuario(usuario_id)
    total_registros = len(registros)
    
    if total_registros >= LIMITE_REGISTROS_FREE:
        return False, f"🔒 Has alcanzado el límite del Plan Gratuito ({LIMITE_REGISTROS_FREE}/{LIMITE_REGISTROS_FREE} registros). ¡Actualiza a Premium para registros ilimitados!"
    
    return True, f"Te quedan {LIMITE_REGISTROS_FREE - total_registros} registros gratuitos."

def guardar_historial(usuario_id, tipo_registro, titulo, contenido, plan_usuario="free"):
    """Guarda un registro validando primero los límites del plan."""
    puedes_guardar, mensaje = verificar_limite_usuario(usuario_id, plan_usuario)
    if not puedes_guardar:
        return False, mensaje

    supabase = get_supabase()
    try:
        data = {
            "usuario_id": str(usuario_id),
            "tipo_registro": tipo_registro,
            "titulo": titulo,
            "contenido": contenido
        }
        supabase.table("historial_clinico").insert(data).execute()
        return True, "Registro guardado exitosamente."
    except Exception as e:
        return False, f"Error guardando historial: {e}"

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
