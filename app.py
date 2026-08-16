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

# Estilos CSS exactos de la interfaz original
st.markdown("""
    <style>
    .stApp { background-color: #FFFDF0 !important; color: #5C3A21 !important; }
    section[data-testid="stSidebar"] { background-color: #FFF9D6 !important; border-right: 1px solid #E6DFB8 !important; }
    h1, h2, h3, h4, label, p, span, div { color: #5C3A21 !important; }
    div.stButton > button { background-color: #2D6A4F !important; color: #FFFFFF !important; border-radius: 8px !important; border: none !important; font-weight: bold !important; }
    .stTextInput input, .stTextArea textarea, .stSelectbox select { background-color: #FFFFFF !important; color: #5C3A21 !important; border: 1px solid #E2D9B7 !important; border-radius: 8px !important; }
    .badge-pro { background-color: #00A86B; color: white !important; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; display: inline-block; }
    .caja-pruebas { background-color: #EAE5D9; padding: 12px; border-radius: 10px; text-align: center; font-weight: 500; color: #5C3A21; margin-top: 10px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if "user" not in st.session_state:
    st.session_state.user = None

# Capturar pago exitoso
query_params = st.query_params
if query_params.get("pago") == "exitoso":
    user_id_pago = query_params.get("user_id")
    if user_id_pago:
        actualizar_plan_usuario(user_id_pago, True)
        if st.session_state.user and str(st.session_state.user["id"]) == str(user_id_pago):
            st.session_state.user["es_premium"] = True
        st.success("🎉 ¡Pago confirmado! Tu cuenta ha sido activada a Plan Premium.")
        st.query_params.clear()

def mostrar_logo(width=160):
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=width)
    else:
        st.write("🦆 **PATU**")

# AUTENTICACIÓN
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

        if st.button("Iniciar Sesión"):
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

        if st.button("Registrarse"):
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
    # PANEL PRINCIPAL
    user = obtener_usuario_por_id(st.session_state.user["id"])
    if user:
        st.session_state.user = user

    user = st.session_state.user
    limite_gratis = 4
    consultas_usadas = user.get("consultas_usadas", 0)
    es_premium = user.get("es_premium", False)
    puede_consultar = es_premium or (consultas_usadas < limite_gratis)

    # CABECERA
    col_a, col_b = st.columns([1, 4])
    with col_a:
        mostrar_logo(width=130)
    with col_b:
        st.markdown('<h1>Workstation Clínico <span class="badge-pro">v3.0 PRO</span></h1>', unsafe_allow_html=True)
        st.write("**PATU** — Psychologists United Across America")

    # BARRA LATERAL
    with st.sidebar:
        st.markdown(f"👤 **Usuario:** `{user.get('nombre', 'Usuario')}`")
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

    # CONTROL DE LÍMITES
    if not puede_consultar:
        st.warning(f"⚠️ Has alcanzado el límite de {limite_gratis} pruebas gratuitas.")
        st.info("Adquiere la versión Premium para continuar utilizando las herramientas clínicas de forma ilimitada.")
        link_pago, msg_pago = crear_preferencia_pago(user["id"], user["email"])
        if link_pago:
            st.link_button("🚀 Adquirir Plan Premium con Mercado Pago", link_pago)
        else:
            st.error(f"Error al generar enlace de pago: {msg_pago}")

    else:
        # PESTAÑAS
        tabs = st.tabs([
            "📋 Analizador Clínico", 
            "🧪 Buscador de Pruebas", 
            "📄 Generador de Informes", 
            "🎙️ Analizador de Sesiones", 
            "📚 Psicoeducación", 
            "📝 Corrector Psicométrico", 
            "📂 Mi Historial"
        ])

        # 1. ANALIZADOR CLÍNICO
        with tabs[0]:
            st.subheader("📋 Análisis Diagnóstico Inicial y Multiaxial")
            col1, col2 = st.columns(2)
            with col1:
                edad = st.number_input("🎂 Edad del Paciente (años):", min_value=1, max_value=120, value=25)
            with col2:
                etapa = st.selectbox("👶 / 🧑 Etapa de Desarrollo:", ["Infantil", "Adolescente", "Adulto", "Adulto Mayor"])

            archivo = st.file_uploader("🎙️ Dictar o Cargar Documento / Narrativa Clínica", type=["pdf", "docx", "txt", "png", "jpg"], key="uploader_1")
            instrucciones = st.text_area("✍️ Dictar o Escribir la Narrativa Clínica", placeholder="Escribe o adjunta las notas clínicas aquí...", key="txt_1")

            if st.button("Procesar Análisis Clínico", key="btn_1"):
                if archivo or instrucciones:
                    with st.spinner("Procesando análisis clínico..."):
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
                            st.error("Error al procesar la consulta.")
                else:
                    st.warning("Por favor ingresa la narrativa o sube un documento.")

        # 2. BUSCADOR DE PRUEBAS
        with tabs[1]:
            st.subheader("🧪 Buscador de Pruebas Psicológicas y Psicométricas")
            st.write("Encuentra la prueba recomendada según el motivo de consulta o constructo a evaluar.")
            
            consulta_prueba = st.text_input("🔍 ¿Qué síntoma, constructo o área deseas evaluar?", placeholder="Ej: Ansiedad en adolescentes, deterioro cognitivo...")
            
            if st.button("Buscar Pruebas Recomendadas", key="btn_2"):
                if consulta_prueba:
                    with st.spinner("Buscando pruebas adecuadas..."):
                        prompt_prueba = f"Recomienda pruebas psicológicas y psicométricas estandarizadas para evaluar: {consulta_prueba}. Incluye nombre, edad de aplicación y qué mide."
                        resultado = procesar_analisis(None, prompt_prueba)
                        if resultado:
                            st.subheader("🔍 Pruebas Recomendadas:")
                            st.markdown(resultado)
                            if not es_premium:
                                nuevas = incrementar_consultas(user["id"])
                                if nuevas is not None:
                                    st.session_state.user["consultas_usadas"] = nuevas
                                st.rerun()
                else:
                    st.warning("Escribe lo que deseas evaluar.")

        # 3. GENERADOR DE INFORMES
        with tabs[2]:
            st.subheader("📄 Generador de Informes Psicológicos")
            datos_informe = st.text_area("Datos clave para el informe:", placeholder="Motivo de consulta, resultados...", key="txt_3")
            if st.button("Generar Informe", key="btn_3"):
                if datos_informe:
                    with st.spinner("Generando informe..."):
                        resultado = procesar_analisis(None, f"Redacta un informe psicológico formal basado en: {datos_informe}")
                        if resultado:
                            st.markdown(resultado)
                            if not es_premium:
                                nuevas = incrementar_consultas(user["id"])
                                if nuevas is not None:
                                    st.session_state.user["consultas_usadas"] = nuevas
                                st.rerun()

        # 4. ANALIZADOR DE SESIONES
        with tabs[3]:
            st.subheader("🎙️ Analizador de Sesiones Terapéuticas")
            notas_sesion = st.text_area("Transcripción o notas de la sesión:", key="txt_4")
            if st.button("Analizar Sesión", key="btn_4"):
                if notas_sesion:
                    with st.spinner("Analizando sesión..."):
                        resultado = procesar_analisis(None, f"Analiza estas notas de sesión clínica: {notas_sesion}")
                        if resultado:
                            st.markdown(resultado)
                            if not es_premium:
                                nuevas = incrementar_consultas(user["id"])
                                if nuevas is not None:
                                    st.session_state.user["consultas_usadas"] = nuevas
                                st.rerun()

        # 5. PSICOEDUCACIÓN
        with tabs[4]:
            st.subheader("📚 Material Psicoeducativo")
            tema_psico = st.text_input("Tema a explicar al paciente:", placeholder="Ej: Ataques de pánico, regulación emocional...", key="txt_5")
            if st.button("Generar Material", key="btn_5"):
                if tema_psico:
                    with st.spinner("Generando explicación..."):
                        resultado = procesar_analisis(None, f"Crea una guía psicoeducativa clara para entregar a un paciente sobre: {tema_psico}")
                        if resultado:
                            st.markdown(resultado)
                            if not es_premium:
                                nuevas = incrementar_consultas(user["id"])
                                if nuevas is not None:
                                    st.session_state.user["consultas_usadas"] = nuevas
                                st.rerun()

        # 6. CORRECTOR PSICOMÉTRICO
        with tabs[5]:
            st.subheader("📝 Corrector y Orientación Psicométrica")
            st.info("Herramienta para asistencia en la interpretación de puntajes y baremos.")

        # 7. MI HISTORIAL
        with tabs[6]:
            st.subheader("📂 Mi Historial de Consultas")
            st.write(f"Consultas realizadas en este periodo: **{consultas_usadas}**")
