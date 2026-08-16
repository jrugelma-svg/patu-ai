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
    """Registra un nuevo usuario mediante Supabase Auth y sincroniza la tabla usuarios."""
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
                supabase.table("usuarios").upsert(data_tabla, on_conflict="id").execute()
            except Exception as e_db:
                print("Nota en sincronización de tabla usuarios:", e_db)

        return True, "📧 Te hemos enviado un correo de confirmación. Por favor revisa tu bandeja de entrada y confirma tu cuenta."
        
    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower() or "unique" in msg.lower():
            return False, "Este correo electrónico ya está registrado."
        return False, f"Error al registrar: {msg}"

def verificar_login(email, password):
    """Verifica las credenciales y asegura la sincronización del usuario."""
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
                return False, "⚠️ Tu correo aún no ha sido verificado. Revisa tu bandeja de entrada."
            
            nombre = user_auth.user_metadata.get("nombre", "Usuario")
            lista_vip = [e.lower().strip() for e in ADMIN_EMAILS]
            plan_final = "admin" if email_clean in lista_vip else user_auth.user_metadata.get("plan", "free")
            user_id = str(user_auth.id)

            # Sincronización en tabla publica
            data_tabla = {
                "id": user_id,
                "id_auth": user_id,
                "nombre": nombre,
                "email": email_clean,
                "password_hash": "SUPABASE_AUTH_MANAGED",
                "plan": plan_final
            }
            try:
                supabase.table("usuarios").upsert(data_tabla, on_conflict="id").execute()
            except Exception as e_sync:
                print("Error sincronizando usuario:", e_sync)
            
            return True, {
                "id": user_id,
                "nombre": nombre,
                "email": user_auth.email,
                "plan": plan_final
            }
            
    except Exception as e:
        msg = str(e)
        if "Email not confirmed" in msg:
            return False, "⚠️ Debes verificar tu correo antes de ingresar."
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
        return False, f"🔒 Has alcanzado el límite del Plan Gratuito ({LIMITE_REGISTROS_FREE}/{LIMITE_REGISTROS_FREE} registros)."
    
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

# ==============================================================================
# FUNCIONES DE GESTIÓN DE PAGOS Y ACTIVACIÓN PREMIUM
# ==============================================================================
def registrar_solicitud_pago(usuario_id, email, num_operacion, comprobante):
    """Guarda la solicitud de verificación de pago en Supabase."""
    supabase = get_supabase()
    try:
        data = {
            "usuario_id": str(usuario_id),
            "email": email,
            "num_operacion": num_operacion,
            "comprobante": comprobante,
            "estado": "pendiente"
        }
        supabase.table("solicitudes_pago").insert(data).execute()
        return True, "Solicitud guardada correctamente."
    except Exception as e:
        return False, f"Error registrando solicitud: {e}"

def activar_plan_premium(usuario_id, plan="premium"):
    """Actualiza el plan de un usuario en la DB pública y en Auth Metadata."""
    supabase = get_supabase()
    try:
        # Actualizar en la tabla publica de usuarios
        supabase.table("usuarios").update({"plan": plan}).eq("id", str(usuario_id)).execute()
        return True, f"Usuario actualizado a {plan} exitosamente."
    except Exception as e:
        return False, f"Error actualizando plan: {e}"
