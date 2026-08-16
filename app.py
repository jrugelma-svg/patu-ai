import streamlit as st
import os
from database import (
    registrar_usuario,
    verificar_login,
    obtener_usuario_por_id,
    incrementar_consultas,
    recargar_creditos_usuario,
    crear_preferencia_pago
)
from engine import (
    procesar_analisis, 
    transcribir_audio_groq
)

# Configuración de la página
st.set_page_config(
    page_title="PATU - Workstation Clínico",
    page_icon="🦆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
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

# Inicializar estados de sesión
if "user" not in st.session_state:
    st.session_state.user = None

if "resultado_analisis" not in st.session_state:
    st.session_state.resultado_analisis = None

if "texto_narrativa" not in st.session_state:
    st.session_state.texto_narrativa = ""

# Capturar pago exitoso y recargar +10 créditos
query_params = st.query_params
if query_params.get("pago") == "exitoso":
    user_id_pago = query_params.get("user_id")
    if user_id_pago:
        exito_recarga = recargar_creditos_usuario(user_id_pago, creditos_a_sumar=10)
        if exito_recarga:
            st.success("🎉 ¡Pago confirmado! Se han añadido +10 créditos a tu cuenta.")
            if st.session_state.user and str(st.session_state.user["id"]) == str(user_id_pago):
                st.session_state.user = obtener_usuario_por_id(user_id_pago)
        st.query_params.clear()

def mostrar_logo(width=160):
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=width)
    else:
        st.write("🦆 **PATU**")

# VISTA DE LOGIN Y REGISTRO
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
                    st.session_state.resultado_analisis = None
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
                else:
                    st.error(msg)
            else:
                st.warning("Por favor completa todos los campos.")

# PANEL PRINCIPAL LOGUEADO
else:
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
            st.write(f"📊 **Uso del Plan:** {consultas_usadas}/{limite_gratis}")
            restantes = max(0, limite_gratis - consultas_usadas)
            st.markdown(f'<div class="caja-pruebas">Te quedan {restantes} créditos disponibles.</div>', unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.user = None
            st.session_state.resultado_analisis = None
            st.session_state.texto_narrativa = ""
            st.rerun()

    # CONTROL DE LÍMITES Y RECARGA
    if not puede_consultar:
        st.warning(f"⚠️ Has agotado tus créditos disponibles.")
        st.info("Recarga 10 créditos adicionales por solo S/. 2.00 para continuar realizando consultas.")
        link_pago, msg_pago = crear_preferencia_pago(user["id"], user["email"])
        if link_pago:
            st.link_button("🚀 Recargar +10 Créditos con Mercado Pago (S/. 2.00)", link_pago)
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

            st.write("---")
            st.write("📷 **1. Cargar Imágenes o Documentos del Motivo de Consulta:**")
            archivo = st.file_uploader(
                "Sube fotos de fichas, capturas, imágenes o PDFs:",
                type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
                key="uploader_1"
            )

            st.write("🎙️ **2. Dictar Motivo de Consulta por Voz:**")
            audio_input = st.audio_input("Grabar notas de voz:", key="audio_voice_1")

            # --- LÓGICA DE TRANSCRIPCIÓN AUTOMÁTICA DE AUDIO ---
            if audio_input is not None:
                audio_bytes = audio_input.getvalue()
                if st.session_state.get("last_audio_bytes") != audio_bytes:
                    with st.spinner("🎙️ Transcribiendo nota de voz a texto..."):
                        transcripcion = transcribir_audio_groq(audio_input)
                        if transcripcion and not str(transcripcion).startswith("Error"):
                            st.session_state.texto_narrativa = str(transcripcion).strip()
                            st.session_state["last_audio_bytes"] = audio_bytes
                            st.success("✅ ¡Voz transcrita exitosamente en el cuadro de texto!")
                        else:
                            st.error(f"Error al transcribir: {transcripcion}")

            # Cuadro de texto sincronizado con session_state
            instrucciones = st.text_area(
                "✍️ **3. Narrativa o Transcripción del Motivo de Consulta:**",
                value=st.session_state.texto_narrativa,
                placeholder="Escribe o revisa la narrativa transcrita aquí...",
                key="txt_1"
            )
            
            # Guardar modificaciones manuales del usuario
            st.session_state.texto_narrativa = instrucciones

            # BOTÓN DE PROCESAMIENTO
            if st.button("Procesar Análisis Clínico", key="btn_1"):
                texto_a_procesar = instrucciones.strip()
                
                # Transcripción de respaldo si presionó el botón directamente con el audio sin esperar
                if not texto_a_procesar and audio_input is not None:
                    with st.spinner("Transcribiendo audio antes de analizar..."):
                        transcripcion = transcribir_audio_groq(audio_input)
                        if transcripcion and not str(transcripcion).startswith("Error"):
                            texto_a_procesar = str(transcripcion).strip()
                            st.session_state.texto_narrativa = texto_a_procesar

                if archivo or texto_a_procesar:
                    with st.spinner("Procesando análisis clínico con IA..."):
                        prompt_completo = f"Edad: {edad}, Etapa: {etapa}. Motivo de Consulta/Narrativa: {texto_a_procesar}"
                        
                        resultado = procesar_analisis(archivo, prompt_completo)
                        
                        if resultado and not resultado.startswith("❌"):
                            st.session_state.resultado_analisis = resultado
                            if not es_premium:
                                nuevas = incrementar_consultas(user["id"])
                                if nuevas is not None:
                                    st.session_state.user["consultas_usadas"] = nuevas
                                st.rerun()
                        else:
                            st.error(resultado)
                else:
                    st.warning("Por favor ingresa una narrativa, graba audio o sube un documento/imagen.")

            # Mostrar resultado persistente
            if st.session_state.resultado_analisis:
                st.markdown("---")
                st.subheader("📄 Resultado del Análisis Diagnóstico:")
                st.markdown(st.session_state.resultado_analisis)

        # 2. BUSCADOR DE PRUEBAS
        with tabs[1]:
            st.subheader("🧪 Buscador de Pruebas Psicológicas y Psicométricas")
            st.write("Encuentra la prueba recomendada según el motivo de consulta o constructo a evaluar.")
            
            consulta_prueba = st.text_input("🔍 ¿Qué síntoma, constructo o área deseas evaluar?", placeholder="Ej: Ansiedad en adolescentes, deterioro cognitivo...")
            
            if st.button("Buscar Pruebas Recomendadas", key="btn_2"):
                if consulta_prueba:
                    with st.spinner("Buscando pruebas adecuadas..."):
                        prompt_prueba = f"Recomienda pruebas psicológicas estandarizadas para evaluar: {consulta_prueba}. Incluye nombre, edad de aplicación y qué mide."
                        resultado = procesar_analisis(None, prompt_prueba)
                        if resultado:
                            st.session_state.resultado_analisis = resultado
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
                            st.session_state.resultado_analisis = resultado
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
                            st.session_state.resultado_analisis = resultado
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
                            st.session_state.resultado_analisis = resultado
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
