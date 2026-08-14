import streamlit as st
import engine
from PIL import Image
import os
import base64

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="PATU | Workstation Clínico v3.0 PRO",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar la imagen del logo en base64 para incrustarla directo en el banner
def get_image_base64(path):
    for posib in [path, "logo.JPG", "logo.jpeg", "logo.png", "LOGO.JPG"]:
        if os.path.exists(posib):
            with open(posib, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

logo_b64 = get_image_base64("logo.jpg")

# =========================================================
# ESTILOS CSS - PALETA DE COLORES PERSONALIZADA PATU
# =========================================================
st.markdown("""
    <style>
    /* 1. Fondo General Cálico y Amigable */
    .main {
        background-color: #FAFAF9 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 2. Estilo de Pestañas (Tabs) con tonos Verde y Salmón PATU */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #F1F5F9;
        padding: 8px 12px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 12px;
        color: #475569 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        border: none !important;
        transition: all 0.2s ease-in-out;
    }
    /* Pestaña Seleccionada: Verde Patito Vibrante */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #16A34A 0%, #15803D 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(22, 163, 74, 0.3) !important;
    }

    /* 3. Botones Principales estilo Coral/Salmón PATU */
    .stButton > button {
        background: linear-gradient(135deg, #FF7E7A 0%, #E05652 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.4rem !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        box-shadow: 0 4px 14px rgba(255, 126, 122, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 126, 122, 0.5) !important;
    }

    /* 4. Barra Lateral (Sidebar) Estilo Noche Cálida */
    section[data-testid="stSidebar"] {
        background: #0F172A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    /* 5. Cajas de Texto e Inputs con Bordes Verdes Suaves al enfocar */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 12px !important;
        border: 1.5px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #22C55E !important;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# BANNER PRINCIPAL CON LOGO INTEGRADÍSIMO Y COLORES PATU
# =========================================================
if logo_b64:
    logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height: 80px; width: auto; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); background: white; padding: 4px;">'
else:
    logo_html = '<div style="font-size: 3rem;">🦆</div>'

st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); padding: 1.4rem 2rem; border-radius: 18px; margin-bottom: 1.8rem; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25); border-left: 8px solid #FF7E7A;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
            <div style="display: flex; align-items: center; gap: 20px;">
                {logo_html}
                <div>
                    <h1 style="color: #FFFFFF !important; margin: 0; font-size: 1.9rem; font-weight: 800; display: flex; align-items: center; gap: 12px;">
                        Workstation Clínico
                        <span style="font-size: 0.8rem; background: linear-gradient(135deg, #22C55E 0%, #16A34A 100%); color: #FFFFFF !important; padding: 4px 14px; border-radius: 20px; font-weight: 700;">v3.0 PRO</span>
                    </h1>
                    <p style="color: #FDBA74 !important; margin: 4px 0 0 0; font-size: 0.95rem; font-weight: 600;">
                        PATU — Psychologists United Across America
                    </p>
                </div>
            </div>
            <div style="background: rgba(255, 126, 122, 0.12); padding: 8px 16px; border-radius: 12px; border: 1px solid rgba(255, 126, 122, 0.3);">
                <span style="color: #FF7E7A; font-size: 0.85rem; font-weight: 700;">🧠 Módulo Clínico Activo</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# BARRA LATERAL (SIDEBAR)
# =========================================================
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    
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
    st.caption("PATU Workstation Clínico v3.0 PRO\nPsychologists United")

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
