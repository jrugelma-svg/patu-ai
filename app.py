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
    page_title="PATU - Workstation Clínico",
    page_icon="🦆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS idénticos a la versión original (Fondo Crema/Cálido + Detalles Café/Verde)
st.markdown("""
    <style>
    /* Fondo principal cálido */
    .stApp {
        background-color: #FFFDF0 !important;
        color: #5C3A21 !important;
    }
    
    /* Sidebar cálida */
    section[data-testid="stSidebar"] {
        background-color: #FFF9D6 !important;
        border-right: 1px solid #E6DFB8 !important;
    }

    /* Textos y títulos en color café */
    h1, h2, h3, h4, label, p, span, div {
        color: #5C3A21 !important;
    }

    /* Botón rojo/coral (Cerrar Sesión / Acciones secundarias) */
    div.stButton > button {
        background-color: #E85D04 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: bold !important;
    }

    /* Botón primario verde/rojo acorde a la acción */
    div.stButton > button[kind="primary"] {
        background-color: #2D6A4F !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }

    /* Cajas de texto y selectores */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #FFFFFF !important;
        color: #5C3A21 !important;
        border: 1px solid #E2D9B7 !important;
        border-radius: 8px !important;
    }

    /* Badge v3.0 PRO */
    .badge-pro {
        background-color: #00A86B;
        color: white !important;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }

    /* Caja informativa de limite de pruebas en sidebar */
    .caja-pruebas {
        background-color: #EAE5D9;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        font-weight: 500;
        color: #5C3A21;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if "user" not in st.session_state:
    st.session_state.user = None

# Capturar pago exitoso desde Mercado Pago
query_params = st.query_params
if query_params.get("pago") == "exitoso":
    user_id_pago = query_params.get("user_id")
    if user_id_pago:
        actualizar_plan_usuario(user_id_pago, True)
        if st.session_state.user and str(st.session_state.user["id"]) == str(user_id_pago):
            st.session_state.user["es_premium"] = True
        st.success("🎉 ¡Pago confirmado! Tu cuenta ha sido activada a Plan Premium.")
        st.query_params.clear()

# Función para mostrar el logo
def mostrar_logo(width=160):
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=width)
    else:
        st.write("🦆 **PATU**")

# LÓGICA DE NAVEGACIÓN / LOGIN
if not st.session_state.user:
    col_logo, col_header = st.columns([1, 4])
    with col_logo:
        mostrar_logo(width=140)
    with col_header:
        st.markdown('<h1>Workstation Clínico <span class="badge-pro">v3.0 PRO</span></h1>', unsafe_allow_html=True)
        st.write("**PATU** — Psychologists United Across America")

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
        st.session_state.user = user

    user = st.session_state.user
    limite_gratis = 4
    consultas_usadas = user.get("consultas_usadas", 0)
    es_premium = user.get("es_premium", False) or user.get("plan") == "premium"

    # CABECERA PRINCIPAL
    col_a, col_b = st.columns([1, 4])
    with col_a:
        mostrar_logo(width=130)
    with col_b:
        st.markdown('<h1>Workstation Clínico <span class="badge-pro">v3.0 PRO</span></h1>', unsafe_allow_html=True)
        st.write("**PATU** — Psychologists United Across America")

    # BARRA LATERAL (Sidebar)
    with st.sidebar:
        st.markdown(f"👤 **Usuario:** `{user.get('nombre', 'jhoru')}`")
        
        if es_premium:
            st.markdown("**Plan Actual:** 🌟 `PLAN PREMIUM`")
        else:
            st.markdown("**Plan Actual:** 🌱 `PLAN FREE`")
            st.markdown("---")
            st.write(f"📊 **Uso del Plan Gratuito:** {consultas_usadas}/{limite_gratis}")
            
            restantes = max(0, limite_gratis - consultas_usadas)
            st.markdown(f'<div class="caja-pruebas">Te quedan {restantes} registros de prueba.</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.user = None
            st.rerun()

    # PESTAÑAS Y HERRAMIENTAS
    tabs = st.tabs([
        "📋 Analizador Clínico", 
        "🧪 Buscador de Pruebas", 
        "📄 Generador de Informes", 
        "🎙️ Analizador de Sesiones", 
        "📚 Psicoeducación", 
        "📝 Corrector Psicométrico", 
        "📂 Mi Historial"
    ])

    with tabs[0]:
        st.subheader("📋 Análisis Diagnóstico Inicial y Multiaxial")

        puede_consultar = es_premium or (consultas_usadas < limite_gratis)

        if not puede_consultar:
            st.warning("⚠️ Has alcanzado el límite de 4 pruebas gratuitas.")
            st.info("Adquiere la versión Premium para continuar realizando análisis e informes ilimitados.")

            link_pago, msg_pago = crear_preferencia_pago(user["id"], user["email"])
            if link_pago:
                st.link_button("🚀 Adquirir Plan Premium con Mercado Pago", link_pago, type="primary")
            else:
                st.error(f"Error al generar enlace de pago: {msg_pago}")

        else:
            col1, col2 = st.columns(2)
            with col1:
                edad = st.number_input("🎂 Edad del Paciente (años):", min_value=1, max_value=120, value=25)
            with col2:
                etapa = st.selectbox("👶 / 🧑 Etapa de Desarrollo:", ["Infantil", "Adolescente", "Adulto", "Adulto Mayor"])

            archivo = st.file_uploader("🎙️ Dictar o Cargar Documento / Narrativa Clínica", type=["pdf", "docx", "txt", "png", "jpg"])
            instrucciones = st.text_area("✍️ Dictar o Escribir la Narrativa Clínica", placeholder="Escribe o adjunta las notas clínicas aquí...")

            if st.button("Procesar Análisis Clínico", type="primary"):
                if (archivo or instrucciones):
                    with st.spinner("Procesando análisis clínico con IA..."):
                        prompt_completo = f"Edad: {edad}, Etapa: {etapa}. {instrucciones}"
                        resultado = procesar_analisis(archivo, prompt_completo)
                        
                        if resultado:
                            st.subheader("📄 Resultado del Análisis Diagnóstico:")
                            st.markdown(resultado)

                            if not es_premium:
                                nuevas = incrementar_consultas(user["id"])
                                if nuevas is not None:
                                    st.session_state.user["consultas_usadas"] = nuevas
                                st.rerun()
                        else:
                            st.error("Hubo un error al procesar el documento.")
                else:
                    st.warning("Por favor ingresa la narrativa o sube un documento.")
