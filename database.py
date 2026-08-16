import os
from supabase import create_client, Client
import bcrypt
import mercadopago

# Inicializar cliente de Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en las variables de entorno.")

supabase: Client = create_client(url, key)


def registrar_usuario(nombre, email, password):
    """Registra un nuevo usuario en la base de datos con contraseña encriptada."""
    try:
        # Verificar si el correo ya existe
        res = supabase.table("usuarios").select("id").eq("email", email).execute()
        if len(res.data) > 0:
            return False, "El correo electrónico ya está registrado."

        # Encriptar la contraseña
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        # Insertar nuevo usuario
        data = {
            "nombre": nombre,
            "email": email,
            "password": hashed_pw,
            "plan": "gratuito",
            "consultas_usadas": 0
        }
        supabase.table("usuarios").insert(data).execute()
        return True, "Usuario registrado exitosamente."
    except Exception as e:
        return False, f"Error al registrar: {e}"


def verificar_login(email, password):
    """Verifica el correo y contraseña del usuario."""
    try:
        res = supabase.table("usuarios").select("*").eq("email", email).execute()
        if len(res.data) == 0:
            return False, None, "Usuario no encontrado."

        usuario = res.data[0]
        # Verificar contraseña encriptada
        if bcrypt.checkpw(password.encode('utf-8'), usuario['password'].encode('utf-8')):
            return True, usuario, "Inicio de sesión exitoso."
        else:
            return False, None, "Contraseña incorrecta."
    except Exception as e:
        return False, None, f"Error al iniciar sesión: {e}"


def obtener_usuario_por_id(user_id):
    """Obtiene los datos actualizados de un usuario por su ID."""
    try:
        res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
        if len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        print(f"Error obteniendo usuario: {e}")
        return None


def incrementar_consultas(user_id):
    """Suma 1 al contador de consultas del usuario."""
    try:
        usuario = obtener_usuario_por_id(user_id)
        if usuario:
            nuevas_consultas = usuario.get("consultas_usadas", 0) + 1
            supabase.table("usuarios").update({"consultas_usadas": nuevas_consultas}).eq("id", user_id).execute()
            return nuevas_consultas
        return 0
    except Exception as e:
        print(f"Error al incrementar consultas: {e}")
        return 0


def actualizar_plan_usuario(user_id, nuevo_plan="premium"):
    """Actualiza el plan del usuario (gratuito -> premium)."""
    try:
        supabase.table("usuarios").update({"plan": nuevo_plan}).eq("id", user_id).execute()
        return True, f"Usuario actualizado a {nuevo_plan} exitosamente."
    except Exception as e:
        return False, f"Error actualizando plan: {e}"


def crear_preferencia_pago(user_id, email, precio=10.0, plan_nombre="Plan Premium PATU"):
    """Genera el link de pago automático en Mercado Pago."""
    token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not token:
        return None

    sdk = mercadopago.SDK(token)

    # URL pública de tu app desplegada en Streamlit
    app_url = "https://patu-ai-ripezmnuqetlldnw52nhua.streamlit.app/"

    preference_data = {
        "items": [
            {
                "title": plan_nombre,
                "quantity": 1,
                "unit_price": float(precio),
                "currency_id": "PEN"
            }
        ],
        "payer": {
            "email": email
        },
        "back_urls": {
            "success": f"{app_url}?pago=exitoso&user_id={user_id}",
            "failure": f"{app_url}?pago=fallido",
            "pending": f"{app_url}?pago=pendiente"
        },
        "auto_return": "approved",
        "external_reference": str(user_id)
    }

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response.get("response", {})
    return preference.get("init_point")
