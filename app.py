import streamlit as st
import engine

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="Workstation Clínico v3.0 PRO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# ESTILOS CSS - REDISEÑO ESTÉTICO UX/UI v3.0
# =========================================================
st.markdown("""
    <style>
    /* 1. Fondo General y Fuentes */
    .main {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 2. Ocultar menús nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 3. Encabezados Principales */
    h1, h2, h3 {
        color: #1E293B !important;
        font-weight: 700 !important;
    }
    
    /* 4. Estilo de Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E2E8F0;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 8px;
        color: #475569;
        font-weight: 600;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
    }

    /* 5. Botones Principales */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3) !important;
    }

    /* 6. Inputs, Textareas y Selects */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* 7. Barra Lateral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# BANNER ENCABEZADO V3.0 (TÍTULO EN BLANCO VISIBLE)
# =========================================================
st.markdown("""
    <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 1.8rem; border-radius: 16px; margin-bottom: 2rem; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);">
        <h2 style="color: #FFFFFF !important; margin: 0; font-size: 1.8rem; display: flex; align-items: center; gap: 10px;">
            🧠 <span style="color: #FFFFFF !important;">Workstation Clínico</span> 
            <span style="font-size: 0.85rem; background: #2563EB; color: #FFFFFF !important; padding: 4px 12px; border-radius: 20px;">v3.0 PRO</span>
        </h2>
        <p style="color: #CBD5E1 !important; margin-top: 0.5rem; margin-bottom: 0; font-size: 0.95rem;">
            Plataforma Integrada de Evaluación Diagnóstica, Psicométrica y Asistencia Terapéutica
        </p>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# BARRA LATERAL (SIDEBAR) - LOGO Y GESTIÓN DE API KEY
# =========================================================
with st.sidebar:
    try:
        st.image("logo.jpg", use_container_width=True)
    except Exception:
        pass

    st.title("⚙️ Configuración")
    
    # Intenta obtener la API Key automáticamente de los Secrets
    api_key_secret = st.secrets.get("GROQ_API_KEY", "")
    
    if api_key_secret:
        api_key = api_key_secret
        st.success("API Key Conectada Automáticamente", icon="⚡")
    else:
        api_key = st.text_input("🔑 Groq API Key:", type="password", help="Ingresa tu clave de API de Groq para activar las funciones")
        if api_key:
            st.success("API Key Conectada", icon="✅")
        else:
            st.warning("Ingrese su API Key para comenzar", icon="⚠️")
            
    st.divider()
    st.caption("Workstation Clínico v3.0 | Módulo Psicológico")

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
# TAB 3: GENERADOR DE INFORMES (.DOCX / MARKDOWN)
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
