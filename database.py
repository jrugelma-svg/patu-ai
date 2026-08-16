import os
import bcrypt
import mercadopago
import streamlit as st
from supabase import create_client, Client

# Lista de correos de desarrolladores (Acceso Premium ilimitado automático)
DESARROLLADORES = [
    "jhordanmartinez164@gmail.com",
    "kujojosep62@gmail.com",
    "desarrollador3@gmail.com",
    "desarrollador4@gmail.com",
    "desarrollador5@gmail.com",
    "desarrollador6@gmail.com"
]

# Inicializar cliente de Supabase
url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en las variables de entorno.")

supabase: Client = create_client(url, key)

# Inicializar SDK de Mercado Pago
mp_token = st.secrets.get("MERCADOPAGO_ACCESS_TOKEN", os.getenv("MERCADOPAGO_ACCESS_TOKEN"))
if mp_token:
    sdk = mercadopago.SDK(mp_token)
else:
    sdk = None


def es_correo_desarrollador(email):
    """Verifica si el correo pertenece a la lista de desarrolladores."""
    return email.strip().lower() in [dev.lower() for dev in DESARROLLADORES]


def registrar_usuario(nombre, email, password):
    """
    Registra un usuario de forma directa en Supabase Auth y en la tabla pública.
    """
    try:
        email_clean = email.strip().lower()
        
        # 1. Registrar en Supabase Auth
        res = supabase.auth.sign_up({
            "email": email_clean,
            "password": password,
            "options": {
                "data": {
                    "nombre": nombre
                }
            }
        })
        
        if res.user:
            es_dev = es_correo_desarrollador(email_clean)
            
            # 2. Intentar guardar en la tabla pública de usuarios
            nuevo_usuario = {
                "id": res.user.id,
                "nombre": nombre,
                "email": email_clean,
                "password_hash": "SUPABASE_AUTH_MANAGED",
                "consultas_usadas": 0,
                "es_premium": es_dev
            }
            supabase.table("usuarios").insert(nuevo_usuario).execute()
            
            return True, "Registro exitoso. ¡Bienvenido a PATU!"

        return False, "No se pudo completar el registro."

    except Exception as e:
        error_str = str(e)
        if "already exists" in error_str or "duplicate key" in error_str:
            return False, "Este correo electrónico ya se encuentra registrado. Intenta iniciar sesión."
        return False, f"Error al registrar usuario: {error_str}"


def verificar_login(email, password):
    """
    Inicia sesión validando credenciales a través de Supabase Auth.
    """
    try:
        email_clean = email.strip().lower()
        
        auth_res = supabase.auth.sign_in_with_password({
            "email": email_clean,
            "password": password
        })
        
        if auth_res.user:
            res = supabase.table("usuarios").select("*").eq("id", auth_res.user.id).execute()
            
            if not res.data:
                return False, None, "Perfil de usuario no encontrado."

            usuario = res.data[0]

            if es_correo_desarrollador(email_clean) and not usuario.get("es_premium", False):
                supabase.table("usuarios").update({"es_premium": True}).eq("id", usuario["id"]).execute()
                usuario["es_premium"] = True

            return True, usuario, "Inicio de sesión exitoso."

    except Exception as e:
        mensaje_error = str(e)
        if "Invalid login credentials" in mensaje_error:
            return False, None, "Correo o contraseña incorrectos."
        return False, None, f"Error en el inicio de sesión: {mensaje_error}"


def obtener_usuario_por_id(user_id):
    """Obtiene los datos actualizados del usuario por su ID."""
    try:
        res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Error al obtener datos del usuario: {str(e)}")
        return None


def incrementar_consultas(user_id):
    """Suma una consulta realizada al contador del usuario."""
    try:
        usuario = obtener_usuario_por_id(user_id)
        if usuario:
            consultas_actuales = usuario.get("consultas_usadas", 0) + 1
            supabase.table("usuarios").update({"consultas_usadas": consultas_actuales}).eq("id", user_id).execute()
            return consultas_actuales
        return None
    except Exception as e:
        st.error(f"Error al actualizar consultas: {str(e)}")
        return None


def recargar_creditos_usuario(user_id, creditos_a_sumar=10):
    """
    Recarga créditos al usuario restando consultas usadas para otorgar nuevo saldo.
    """
    try:
        usuario = obtener_usuario_por_id(user_id)
        if usuario:
            consultas_actuales = usuario.get("consultas_usadas", 0)
            nuevas_consultas = max(0, consultas_actuales - creditos_a_sumar)
            supabase.table("usuarios").update({"consultas_usadas": nuevas_consultas}).eq("id", user_id).execute()
            return True
        return False
    except Exception as e:
        st.error(f"Error al recargar créditos: {str(e)}")
        return False


def crear_preferencia_pago(user_id, email):
    """Genera un link de pago en Mercado Pago para recargar +10 créditos por S/. 2.00."""
    if not sdk:
        return None, "El servicio de Mercado Pago no está configurado."

    try:
        preference_data = {
            "items": [
                {
                    "title": "PATU Workstation - Recarga de 10 Créditos",
                    "quantity": 1,
                    "unit_price": 2.00,
                    "currency_id": "PEN"
                }
            ],
            "payer": {
                "email": email
            },
            "external_reference": str(user_id),
            "back_urls": {
                "success": "https://patu-ai-ripezmnuqetlldnw52nhua.streamlit.app?pago=exitoso&user_id=" + str(user_id),
                "failure": "https://patu-ai-ripezmnuqetlldnw52nhua.streamlit.app",
                "pending": "https://patu-ai-ripezmnuqetlldnw52nhua.streamlit.app"
            },
            "auto_return": "approved"
        }

        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        return preference.get("init_point"), "Preferencia creada correctamente."
    except Exception as e:
        return None, f"Error al generar la preferencia de pago: {str(e)}"
