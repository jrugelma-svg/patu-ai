import streamlit as st
import os
from database import (
    registrar_usuario,
    verificar_login,
    obtener_usuario_por_id,
    incrementar_consultas,
    actualizar_plan_usuario,
    crear_preferencia_pago
)
from engine import procesar_analisis

# Configuración de la página
st.set_page_config(
    page_title="PATU - Workstation de Análisis",
    page_icon="🤖",
    layout="wide"
)

# Inicializar estado de sesión del usuario
if "user" not in st.session_state:
    st.session_state.user = None

# Capturar redirección desde Mercado Pago tras pago exitoso
query_params = st.query_params
if query_params.get("pago") == "exitoso":
    user_id_pago = query_params.get("user_id")
    if user_id_pago:
        actualizar_plan_usuario(user_id_pago, "premium")
        if st.session_state.user and str(st.session_state.user["id"]) == str(user_id_pago):
            st.session_state.user["plan"] = "premium"
        st.success("🎉 ¡Pago confirmado! Tu cuenta ha sido activada a Plan Premium automáticamente.")
        st.query_params.clear()

# LÓGICA DE NAVEGACIÓN Y LOGIN
if not st.session_state.user:
    st.title("🤖 Bienvenido a PATU Workstation")
    opcion = st.sidebar.radio("Navegación", ["Iniciar Sesión", "Registrarse"])

    if opcion == "Iniciar Sesión":
        st.subheader("Accede a tu cuenta")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar Sesión", type="primary"):
            if email and password:
                exito, usuario, msg = verificar_login(email, password)
                if exito:
                    st.session_state.user = usuario
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Por favor ingresa tu correo y contraseña.")

    elif opcion == "Registrarse":
        st.subheader("Crea una nueva cuenta")
        nombre = st.text_input("Nombre Completo")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")

        if st.button("Registrarse", type="primary"):
            if nombre and email and password:
                exito, msg = registrar_usuario(nombre, email, password)
                if exito:
                    st.success(msg)
                    st.info("Ya puedes iniciar sesión con tu cuenta.")
                else:
                    st.error(msg)
            else:
                st.warning("Por favor completa todos los campos.")

else:
    # USUARIO AUTENTICADO
    user = obtener_usuario_por_id(st.session_state.user["id"])
    if user:
        st.session_state.user = user  # Sincronizar datos de la BD

    user = st.session_state.user
    limite_gratis = 3
    consultas_usadas = user.get("consultas_usadas", 0)
    plan = user.get("plan", "gratuito")

    # BARRA LATERAL
    st.sidebar.title(f"👤 {user['nombre']}")
    st.sidebar.write(f"**Plan actual:** {plan.capitalize()}")
    if plan == "gratuito":
        st.sidebar.write(f"**Consultas usadas:** {consultas_usadas} / {limite_gratis}")
    else:
        st.sidebar.write("**Consultas:** Ilimitadas ✨")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()

    st.title("📊 Panel de Análisis de Documentos")

    # VERIFICACIÓN DE LÍMITES DE USO
    puede_consultar = (plan == "premium") or (consultas_usadas < limite_gratis)

    if not puede_consultar:
        st.warning("⚠️ Has alcanzado el límite de 3 consultas gratuitas.")
        st.info("Actualiza a Plan Premium por solo S/ 10.00 para obtener análisis ilimitados.")

        link_pago = crear_preferencia_pago(user["id"], user["email"])
        if link_pago:
            st.link_button("🚀 Pagar con Yape / Tarjeta (S/ 10.00)", link_pago, type="primary")
        else:
            st.error("No se pudo conectar con Mercado Pago. Verifica tus credenciales.")

    else:
        # FORMULARIO DE ANÁLISIS
        archivo = st.file_uploader("Carga tu archivo o documento para analizar", type=["pdf", "docx", "txt", "png", "jpg"])
        instrucciones = st.text_area("Instrucciones específicas de análisis", placeholder="Ejemplo: Resume este documento y extrae los datos clave...")

        if st.button("Procesar Documento", type="primary"):
            if archivo and instrucciones:
                with st.spinner("Procesando tu documento con IA..."):
                    resultado = procesar_analisis(archivo, instrucciones)
                    if resultado:
                        st.subheader("📄 Resultado del Análisis:")
                        st.write(resultado)

                        # Incrementar contador solo si es plan gratuito
                        if plan == "gratuito":
                            nuevas = incrementar_consultas(user["id"])
                            st.session_state.user["consultas_usadas"] = nuevas
                            st.rerun()
                    else:
                        st.error("Hubo un error al procesar el archivo.")
            else:
                st.warning("Asegúrate de subir un archivo y escribir las instrucciones.")
