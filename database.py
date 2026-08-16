import os
import uuid
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

# Inicializar SDK de Mercado Pago desde Streamlit Secrets / Env Vars
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
    Registra un nuevo usuario con ID UUID y contraseña encriptada.
    Otorga Premium automático si pertenece a la lista de desarrolladores.
    """
    try:
        email_clean = email.strip().lower()
        
        # Verificar si el usuario ya existe
        res = supabase.table("usuarios").select("id").eq("email", email_clean).execute()
        if res.data:
            return False, "El correo electrónico ya está registrado."

        # Encriptar la contraseña
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        # Determinar si es cuenta dev/premium
        es_dev = es_correo_desarrollador(email_clean)

        # Insertar usuario
        nuevo_usuario = {
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "email": email_clean,
            "password_hash": hashed_pw,
            "consultas_usadas": 0,
            "es_premium": es_dev
        }
        supabase.table("usuarios").insert(nuevo_usuario).execute()
        
        msg = "Usuario registrado exitosamente como Desarrollador (Premium)." if es_dev else "Usuario registrado exitosamente."
        return True, msg
    except Exception as e:
        return False, f"Error al registrar usuario: {str(e)}"


def verificar_login(email, password):
    """
    Valida credenciales y actualiza automáticamente a Premium si es un desarrollador.
    Devuelve: (exito: bool, usuario: dict/None, mensaje: str)
    """
    try:
        email_clean = email.strip().lower()
        res = supabase.table("usuarios").select("*").eq("email", email_clean).execute()
        if not res.data:
            return False, None, "Usuario no encontrado."

        usuario = res.data[0]
        stored_hash = usuario.get("password_hash")

        if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            # Si el correo es de un desarrollador y no figura como Premium, se actualiza automáticamente
            if es_correo_desarrollador(email_clean) and not usuario.get("es_premium", False):
                actualizar_plan_usuario(usuario["id"], True)
                usuario["es_premium"] = True
                
            return True, usuario, "Inicio de sesión exitoso."
        else:
            return False, None, "Contraseña incorrecta."
    except Exception as e:
        return False, None, f"Error en la verificación: {str(e)}"


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
    """Genera un link de pago en Mercado Pago para activar la versión Premium."""
    if not sdk:
        return None, "El servicio de Mercado Pago no está configurado."

    try:
        preference_data = {
            "items": [
                {
                    "title": "PATU Workstation - Suscripción Premium / Recarga",
                    "quantity": 1,
                    "unit_price": 29.90,
                    "currency_id": "PEN"
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
        
        return preference.get("init_point"), "Preferencia creada correctamente."
    except Exception as e:
        return None, f"Error al generar la preferencia de pago: {str(e)}"
