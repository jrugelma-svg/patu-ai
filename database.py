import os
import bcrypt
import mercadopago
import streamlit as st
from supabase import create_client, Client

# Inicializar cliente de Supabase desde Streamlit Secrets / Env Vars
url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en las variables de entorno.")

supabase: Client = create_client(url, key)

# Inicializar SDK de Mercado Pago desde Streamlit Secrets / Env Vars
mp_token = st.secrets.get("MERCADOPAGO_ACCESS_TOKEN", os.getenv("MERCADOPAGO_ACCESS_TOKEN"))
if mp_token:
    sdk = mercadopago.SDK(mp_token)
else:
    sdk = None


def registrar_usuario(nombre, email, password):
    """
    Registra un nuevo usuario con la contraseña encriptada usando bcrypt.
    """
    try:
        # Verificar si el usuario ya existe
        res = supabase.table("usuarios").select("id").eq("email", email).execute()
        if res.data:
            return False, "El correo electrónico ya está registrado."

        # Encriptar la contraseña
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        # Insertar usuario
        nuevo_usuario = {
            "nombre": nombre,
            "email": email,
            "password_hash": hashed_pw,
            "consultas_usadas": 0,
            "es_premium": False
        }
        supabase.table("usuarios").insert(nuevo_usuario).execute()
        return True, "Usuario registrado exitosamente."
    except Exception as e:
        return False, f"Error al registrar usuario: {str(e)}"


def verificar_login(email, password):
    """
    Valida las credenciales de acceso del usuario.
    Devuelve: (exito: bool, usuario: dict/None, mensaje: str)
    """
    try:
        res = supabase.table("usuarios").select("*").eq("email", email).execute()
        if not res.data:
            return False, None, "Usuario no encontrado."

        usuario = res.data[0]
        stored_hash = usuario.get("password_hash")

        if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True, usuario, "Inicio de sesión exitoso."
        else:
            return False, None, "Contraseña incorrecta."
    except Exception as e:
        return False, None, f"Error en la verificación: {str(e)}"


def obtener_usuario_por_id(user_id):
    """
    Obtiene los datos actualizados del usuario por su ID.
    """
    try:
        res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        st.error(f"Error al obtener datos del usuario: {str(e)}")
        return None


def incrementar_consultas(user_id):
    """
    Suma una consulta realizada al contador del usuario.
    """
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
    """
    Actualiza el estado del usuario a Premium tras la confirmación del pago.
    """
    try:
        supabase.table("usuarios").update({"es_premium": es_premium}).eq("id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al actualizar plan: {str(e)}")
        return False


def crear_preferencia_pago(user_id, email):
    """
    Genera un link de pago en Mercado Pago para activar la versión Premium.
    """
    if not sdk:
        return None, "El servicio de Mercado Pago no está configurado."

    try:
        preference_data = {
            "items": [
                {
                    "title": "PATU Workstation - Suscripción Premium / Recarga",
                    "quantity": 1,
                    "unit_price": 29.90,  # Monto en la moneda configurada en tu cuenta
                    "currency_id": "PEN"   # Moneda (PEN, ARS, MXN, USD)
                }
            ],
            "payer": {
                "email": email
            },
            "external_reference": str(user_id),
            "back_urls": {
                "success": "https://patu-ai-ripezmnuqetlldnw52nhua.streamlit.app",
                "failure": "https://patu-ai-ripezmnuqetlldnw52nhua.streamlit.app",
                "pending": "https://patu-ai-ripezmnuqetlldnw52nhua.streamlit.app"
            },
            "auto_return": "approved"
        }

        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        # Devuelve el link de checkout de Mercado Pago
        return preference.get("init_point"), "Preferencia creada correctamente."
    except Exception as e:
        return None, f"Error al generar la preferencia de pago: {str(e)}"
