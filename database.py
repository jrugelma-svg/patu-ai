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

# Inicializar cliente de Supabase desde Streamlit Secrets / Env Vars
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
    Registra un usuario mediante Supabase Auth para enviar correo de verificación.
    """
    try:
        email_clean = email.strip().lower()
        
        # 1. Registrar en el sistema de autenticación de Supabase (envía email de confirmación)
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
            
            # 2. Guardar perfil inicial en la tabla pública de usuarios
            nuevo_usuario = {
                "id": res.user.id,
                "nombre": nombre,
                "email": email_clean,
                "password_hash": "SUPABASE_AUTH_MANAGED",
                "consultas_usadas": 0,
                "es_premium": es_dev
            }
            supabase.table("usuarios").insert(nuevo_usuario).execute()
            
            msg = "Registro exitoso. Revisa tu correo electrónico para confirmar tu cuenta antes de iniciar sesión."
            if es_dev:
                msg += " (Cuenta con beneficios de Desarrollador)."
            return True, msg

        return False, "No se pudo completar el registro."

    except Exception as e:
        return False, f"Error al registrar usuario: {str(e)}"


def verificar_login(email, password):
    """
    Inicia sesión validando credenciales y estado de correo a través de Supabase Auth.
    """
    try:
        email_clean = email.strip().lower()
        
        # Iniciar sesión vía Supabase Auth
        auth_res = supabase.auth.sign_in_with_password({
            "email": email_clean,
            "password": password
        })
        
        if auth_res.user:
            # Obtener los datos del perfil desde la tabla pública
            res = supabase.table("usuarios").select("*").eq("id", auth_res.user.id).execute()
            
            if not res.data:
                return False, None, "Perfil de usuario no encontrado."

            usuario = res.data[0]

            # Actualizar automáticamente a Premium si es correo dev
            if es_correo_desarrollador(email_clean) and not usuario.get("es_premium", False):
                actualizar_plan_usuario(usuario["id"], True)
                usuario["es_premium"] = True

            return True, usuario, "Inicio de sesión exitoso."

    except Exception as e:
        mensaje_error = str(e)
        if "Email not confirmed" in mensaje_error:
            return False, None, "Por favor, confirma tu correo electrónico antes de ingresar."
        elif "Invalid login credentials" in mensaje_error:
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


def actualizar_plan_usuario(user_id, es_premium=True):
    """Actualiza el estado del usuario a Premium tras el pago o por rol dev."""
    try:
        supabase.table("usuarios").update({"es_premium": es_premium}).eq("id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar plan: {str(e)}")
        return False


def crear_preferencia_pago(user_id, email):
    """Genera un link de pago en Mercado Pago para activar la versión Premium por S/. 2.00."""
    if not sdk:
        return None, "El servicio de Mercado Pago no está configurado."

    try:
        preference_data = {
            "items": [
                {
                    "title": "PATU Workstation - Suscripción Premium / Recarga",
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
