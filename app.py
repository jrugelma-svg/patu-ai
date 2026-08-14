import streamlit as st
import engine

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="PATU | Workstation Clínico v3.0 PRO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ESTILOS CSS - UX/UI LIMPIO Y PROFESIONAL PARA PRESENTACIÓN
# =========================================================
st.markdown("""
    <style>
    /* Fondo general claro y tipografía legible */
    .main {
        background-color: #F8FAFC;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Ocultar elementos nativos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo para las Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #E2E8F0;
        padding: 8px 12px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        color: #334155 !important;
        font-weight: 600 !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }

    /* Estilo para Botones Principales */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
    }

    /* Barra Lateral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    
    /* Cajas de texto e inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# BARRA LATERAL (SIDEBAR) - LOGO E IDENTIDAD
# =========================================================
with st.sidebar:
    # Mostramos el logo dentro de un contenedor blanco limpio para que resalte
    st.markdown("""
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 14px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    """, unsafe_allow_html=True)
    
    try:
        st.image("logo.jpg", use_container_width=True)
    except Exception:
        # Si por alguna razón logo.jpg no carga, muestra un logo estilizado en texto
        st.markdown("<h2 style='color:#2563EB; margin:0; font-weight:800;'>🦆 PATU AI</h2>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### ⚙️ Configuración")
    
    # Intenta obtener la API Key automáticamente de Secrets de Streamlit
    api_key_secret = st.secrets.get("GROQ_API_KEY", "")
    
    if api_key_secret:
        api_key = api_key_secret
        st.success("Sistema Conectado", icon="⚡")
    else:
        api_key = st.text_input("🔑 Groq API Key:", type="password", help="Ingresa tu clave de API de Groq para activar las funciones")
        if api_key:
            st.success("API Key Conectada", icon="✅")
        else:
            st.warning("Ingrese su API Key para comenzar", icon="⚠️")
            
    st.divider()
    st.caption("PATU Workstation Clínico v3.0 PRO\nMódulo de Asistencia Psicológica")

# =========================================================
# BANNER SUPERIOR - ENCABEZADO CLARO Y PROFESIONAL
# =========================================================
# Usamos un diseño de tarjeta clara con borde azul vibrante (100% visible y elegante)
st.markdown("""
    <div style="background-color: #FFFFFF; border-left: 6px solid #2563EB; padding: 20px 24px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;">
            <div>
                <h1 style="color: #0F172A !important; margin: 0; font-size: 1.8rem; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                    🧠 Workstation Clínico 
                    <span style="font-size: 0.8rem; background-color: #2563EB; color: #FFFFFF !important; padding: 4px 12px; border-radius: 20px; font-weight: 600;">v3.0 PRO</span>
                </h1>
                <p style="color: #475569 !important; margin: 6px 0 0 0; font-size: 0.95rem;">
                    Plataforma Integrada de Evaluación Diagnóstica, Psicométrica y Asistencia Terapéutica
                </p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# PESTAÑAS PRINCIPALES DE LA APLICACIÓN
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Analizador Clínico", 
    "🧪 Buscador de Pruebas", 
    "📄 Generador de Informes", 
    "🎙️ Analizador de Sesiones", 
    "📚 Psicoeducación"
])

# ---------------------------------------------------------
# TAB 1: ANALIZADOR CLÍNICO INICIAL
# ---------------------------------------------------------
with tab1:
    st.subheader("📋 Análisis Diagnóstico Inicial y Multiaxial")
    narrativa = st.text_area("Narrativa o notas de la consulta inicial:", height=150, placeholder="Escribe o pega la narrativa clínica del paciente...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Analizar Caso y Brechas"):
            if not api_key:
                st.error("Por favor, ingresa tu API Key en la barra lateral.")
            elif not narrativa.strip():
                st.warning("Ingresa una narrativa antes de analizar.")
            else:
                with st.spinner("Procesando hipótesis clínicas..."):
                    res = engine.analizar_caso_inicial(narrativa, api_key)
                    st.markdown(res)
                    
    with col2:
        if st.button("🧪 Sugerir Batería Psicométrica"):
            if not api_key:
                st.error("Por favor, ingresa tu API Key en la barra lateral.")
            elif not narrativa.strip():
                st.warning("Ingresa una narrativa antes de analizar.")
            else:
                with st.spinner("Identificando pruebas recomendadas..."):
                    res = engine.obtener_pruebas_psicometricas(narrativa, api_key)
                    st.markdown(res)
                    
    st.divider()
    st.subheader("🌐 Evaluación Multiaxial Completa")
    datos_extra = st.text_input("Datos contextuales adicionales (opcional):", placeholder="Ej: Antecedentes familiares, examen físico, estresores actuales...")
    if st.button("📊 Generar Evaluación Multiaxial"):
        if not api_key:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        elif not narrativa.strip():
            st.warning("Ingresa la narrativa principal del caso.")
        else:
            with st.spinner("Formulando evaluación multiaxial..."):
                res = engine.generar_diagnostico_multiaxial(narrativa, datos_extra, api_key)
                st.markdown(res)

# ---------------------------------------------------------
# TAB 2: BUSCADOR WEB REAL DE PRUEBAS
# ---------------------------------------------------------
with tab2:
    st.subheader("🧪 Buscador Web Real de Pruebas y Recursos Psicométricos")
    st.caption("Rastrea internet en tiempo real para obtener enlaces a fichas técnicas, manuales y documentos PDF.")
    
    query_prueba = st.text_input("Nombre de la prueba o área a evaluar:", placeholder="Ej: WISC-V, BDI-II, RAVEN, Ansiedad, STAI...")
    if st.button("🔎 Buscar Recursos en la Web"):
        if not api_key:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        elif not query_prueba.strip():
            st.warning("Escribe el nombre de una prueba o término de búsqueda.")
        else:
            with st.spinner("Rastreando internet en tiempo real..."):
                res = engine.buscar_recursos_pruebas(query_prueba, api_key)
                st.markdown(res)

# ---------------------------------------------------------
# TAB 3: GENERADOR DE INFORMES
# ---------------------------------------------------------
with tab3:
    st.subheader("📄 Generador de Informes Psicológicos")
    col_a, col_b = st.columns(2)
    with col_a:
        nombre = st.text_input("Nombre / Iniciales:")
        edad = st.text_input("Edad:")
        genero = st.text_input("Género / Sexo:")
        ocupacion = st.text_input("Ocupación:")
    with col_b:
        enfoque = st.selectbox("Enfoque del Informe:", ["Cognitivo-Conductual", "Psicodinámico", "Humanista/Sistémico", "Neuropsicológico", "Integral / Clínico General"])
        motivo = st.text_area("Motivo de Consulta:", height=70)
        
    problema_actual = st.text_area("Problema Actual / Antecedentes:", height=90)
    pruebas_aplicadas = st.text_area("Pruebas Aplicadas:", height=70)
    observaciones = st.text_area("Observaciones Conductuales:", height=70)
    diagnostico = st.text_area("Conclusiones Diagnósticas:", height=70)
    
    if st.button("📑 Redactar Informe Profesional"):
        if not api_key:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        else:
            datos_dict = {
                "nombre": nombre, "edad": edad, "genero": genero, "ocupacion": ocupacion,
                "motivo": motivo, "problema_actual": problema_actual,
                "pruebas_aplicadas": pruebas_aplicadas, "observaciones": observaciones,
                "diagnostico": diagnostico
            }
            with st.spinner("Redactando informe profesional..."):
                res = engine.generar_informe_premium(datos_dict, enfoque, api_key)
                st.markdown(res)

# ---------------------------------------------------------
# TAB 4: TRANSCRIPCIÓN Y ANÁLISIS DE AUDIO
# ---------------------------------------------------------
with tab4:
    st.subheader("🎙️ Analizador de Sesiones Grabadas (Audio a Texto)")
    archivo_audio = st.file_uploader("Sube el audio de la sesión (MP3, WAV, M4A):", type=["mp3", "wav", "m4a"])
    
    if archivo_audio:
        st.audio(archivo_audio)
        if st.button("🎙️ Transcribir y Analizar Sesión"):
            if not api_key:
                st.error("Por favor, ingresa tu API Key en la barra lateral.")
            else:
                with st.spinner("Transcribiendo audio con Whisper..."):
                    transcripcion = engine.transcribir_audio_groq(archivo_audio, api_key)
                    
                if "Error" not in transcripcion:
                    st.success("¡Transcripción completada!")
                    with st.expander("Ver transcripción completa"):
                        st.write(transcripcion)
                    
                    with st.spinner("Analizando contenido clínico de la sesión..."):
                        analisis = engine.analizar_transcripcion_sesion(transcripcion, api_key)
                        st.markdown(analisis)
                else:
                    st.error(transcripcion)

# ---------------------------------------------------------
# TAB 5: GUÍAS PSICOEDUCATIVAS
# ---------------------------------------------------------
with tab5:
    st.subheader("📚 Generador de Material Psicoeducativo")
    diag_base = st.text_area("Diagnóstico o tema a explicar:", placeholder="Ej: Trastorno de Ansiedad Generalizada, Pánico, TDAH en adultos...")
    destinatario = st.selectbox("Destinatario de la guía:", ["Paciente (Adulto)", "Padres / Familiares", "Paciente (Adolescente)", "Docentes / Colegio"])
    
    if st.button("📖 Generar Guía Psicoeducativa"):
        if not api_key:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        elif not diag_base.strip():
            st.warning("Ingresa un diagnóstico o tema.")
        else:
            with st.spinner("Elaborando material psicoeducativo..."):
                res = engine.generar_plantilla_psicoeducacion(diag_base, destinatario, api_key)
                st.markdown(res)
