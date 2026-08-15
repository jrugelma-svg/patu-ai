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

# Inicializar estado de sesión para el texto dictado
if "narrativa_texto" not in st.session_state:
    st.session_state["narrativa_texto"] = ""

# Cargar la imagen del logo en base64
def get_image_base64(path):
    for posib in [path, "logo.JPG", "logo.jpeg", "logo.png", "LOGO.JPG"]:
        if os.path.exists(posib):
            with open(posib, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()
    return None

logo_b64 = get_image_base64("logo.jpg")

# =========================================================
# ESTILOS CSS - PALETA CÁLIDA TIPO LOGO PATU
# =========================================================
st.markdown("""
    <style>
    /* 1. FONDO GENERAL CÁLIDO */
    .stApp {
        background-color: #FEFCE8 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 2. TÍTULOS Y TEXTOS GENERALES */
    h1, h2, h3, .stSubheader {
        color: #EA580C !important;
        font-weight: 800 !important;
    }
    
    p, label, span, div {
        color: #78350F !important;
    }

    /* 3. PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #FEF3C7;
        padding: 8px 12px;
        border-radius: 16px;
        border: 2px solid #FDE68A;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 12px;
        color: #92400E !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #16A34A 0%, #15803D 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(22, 163, 74, 0.35) !important;
    }
    .stTabs [aria-selected="true"] * {
        color: #FFFFFF !important;
    }

    /* 4. BOTONES CORAL / SALMÓN */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #FF7E7A 0%, #E05652 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.4rem !important;
        font-weight: 800 !important;
        font-size: 0.98rem !important;
        box-shadow: 0 4px 14px rgba(255, 126, 122, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    .stButton > button *, .stDownloadButton > button * {
        color: #FFFFFF !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 126, 122, 0.55) !important;
    }

    /* 5. BARRA LATERAL (SIDEBAR) */
    section[data-testid="stSidebar"] {
        background: #FEF3C7 !important;
        border-right: 2px solid #FDE68A !important;
    }
    section[data-testid="stSidebar"] * {
        color: #78350F !important;
    }

    /* 6. CAJAS DE TEXTO (INPUTS) */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
        border-radius: 12px !important;
        border: 2px solid #FDE68A !important;
        background-color: #FFFFFF !important;
        color: #78350F !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus {
        border-color: #FF7E7A !important;
        box-shadow: 0 0 0 3px rgba(255, 126, 122, 0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# BANNER PRINCIPAL
# =========================================================
if logo_b64:
    logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height: 85px; width: auto; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); background: white; padding: 4px; border: 2px solid #FDE68A;">'
else:
    logo_html = '<div style="font-size: 3.5rem;">🦆</div>'

st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); padding: 1.5rem 2rem; border-radius: 20px; margin-bottom: 1.8rem; box-shadow: 0 10px 25px -5px rgba(217, 119, 6, 0.15); border: 2px solid #FDE68A; border-left: 10px solid #FF7E7A;">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 15px;">
            <div style="display: flex; align-items: center; gap: 20px;">
                {logo_html}
                <div>
                    <h1 style="color: #EA580C !important; margin: 0; font-size: 2.1rem; font-weight: 900; display: flex; align-items: center; gap: 12px;">
                        Workstation Clínico
                        <span style="font-size: 0.85rem; background: #16A34A; color: #FFFFFF !important; padding: 4px 14px; border-radius: 20px; font-weight: 800;">v3.0 PRO</span>
                    </h1>
                    <p style="color: #92400E !important; margin: 4px 0 0 0; font-size: 1rem; font-weight: 700;">
                        PATU — Psychologists United Across America
                    </p>
                </div>
            </div>
            <div style="background: #FFFFFF; padding: 10px 18px; border-radius: 14px; border: 2px solid #FDE68A; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                <span style="color: #EA580C !important; font-size: 0.9rem; font-weight: 800;">🧠 Módulo Clínico Activo</span>
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Analizador Clínico", 
    "🧪 Buscador de Pruebas", 
    "📄 Generador de Informes", 
    "🎙️ Analizador de Sesiones", 
    "📚 Psicoeducación",
    "🧮 Corrector Psicométrico"
])

# ---------------------------------------------------------
# TAB 1: ANALIZADOR CLÍNICO INICIAL (CON DICTADO POR VOZ)
# ---------------------------------------------------------
with tab1:
    st.subheader("📋 Análisis Diagnóstico Inicial y Multiaxial")
    
    col_edad1, col_edad2 = st.columns(2)
    with col_edad1:
        edad_paciente = st.number_input("🎂 Edad del Paciente (años):", min_value=1, max_value=110, value=25, step=1)
    with col_edad2:
        if edad_paciente < 12:
            etapa_default = "Infantil (Niño/a)"
        elif edad_paciente < 18:
            etapa_default = "Adolescente"
        elif edad_paciente < 65:
            etapa_default = "Adulto"
        else:
            etapa_default = "Adulto Mayor"
            
        opciones_etapa = ["Infantil (Niño/a)", "Adolescente", "Adulto", "Adulto Mayor"]
        etapa_paciente = st.selectbox(
            "👶/👵 Etapa de Desarrollo:", 
            opciones_etapa,
            index=opciones_etapa.index(etapa_default)
        )

    st.markdown("#### 🎙️ Dictar o Escribir la Narrativa Clínica")
    st.caption("Haz clic en el micrófono para hablarle a la app o escribe directamente en el recuadro de texto.")
    
    # Grabador de Voz Directo
    audio_dictado = st.audio_input("Presiona para dictar las notas de voz del caso:")
    
    if audio_dictado is not None:
        if not api_key:
            st.error("Por favor ingresa tu API Key en la barra lateral para usar el dictado por voz.")
        else:
            with st.spinner("Transcribiendo tu dictado por voz..."):
                texto_dictado = engine.transcribir_audio_groq(audio_dictado, api_key)
                if "Error" not in texto_dictado:
                    # Acumular o reemplazar el texto
                    if st.session_state["narrativa_texto"]:
                        st.session_state["narrativa_texto"] += "\n" + texto_dictado
                    else:
                        st.session_state["narrativa_texto"] = texto_dictado
                    st.success("¡Voz transcrita e integrada correctamente!")

    # Carga el texto acumulado del dictado o lo que el usuario digite manualmente
    narrativa = st.text_area(
        "Narrativa o notas de la consulta inicial:", 
        value=st.session_state["narrativa_texto"],
        height=160, 
        placeholder="Escribe o habla por el micrófono para capturar la narrativa clínica del paciente..."
    )
    # Actualizar la sesión si el usuario edita el texto manualmente
    st.session_state["narrativa_texto"] = narrativa

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Analizar Caso y Brechas"):
            if not api_key:
                st.error("Por favor, ingresa tu API Key en la barra lateral.")
            elif not narrativa.strip():
                st.warning("Ingresa o dicta una narrativa antes de analizar.")
            else:
                with st.spinner("Procesando hipótesis clínicas..."):
                    res = engine.analizar_caso_inicial(narrativa, api_key)
                    st.markdown(res)
                    
    with col2:
        if st.button("🧪 Sugerir Batería Psicométrica"):
            if not api_key:
                st.error("Por favor, ingresa tu API Key en la barra lateral.")
            elif not narrativa.strip():
                st.warning("Ingresa o dicta una narrativa antes de analizar.")
            else:
                with st.spinner(f"Identificando pruebas válidas para {edad_paciente} años ({etapa_paciente})..."):
                    res = engine.obtener_pruebas_psicometricas(narrativa, edad_paciente, etapa_paciente, api_key)
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
# TAB 2: BUSCADOR WEB DE PRUEBAS
# ---------------------------------------------------------
with tab2:
    st.subheader("🧪 Buscador de Pruebas y Recursos Psicométricos")
    st.caption("Rastrea información técnica sobre pruebas psicológicas.")
    
    query_prueba = st.text_input("Nombre de la prueba o área a evaluar:", placeholder="Ej: WISC-V, BDI-II, RAVEN, Ansiedad, STAI...")
    if st.button("🔎 Buscar Recursos"):
        if not api_key:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        elif not query_prueba.strip():
            st.warning("Escribe el nombre de una prueba o término de búsqueda.")
        else:
            with st.spinner("Consultando información de la prueba..."):
                res = engine.buscar_recursos_pruebas(query_prueba, api_key)
                st.markdown(res)

# ---------------------------------------------------------
# TAB 3: GENERADOR DE INFORMES CON DESCARGA WORD (.DOCX)
# ---------------------------------------------------------
with tab3:
    st.subheader("📄 Generador de Informes y Exportación a Word")
    st.caption("Sube tu archivo de Word con la plantilla de tu consultorio o usa la estructura estándar.")
    
    archivo_plantilla = st.file_uploader("📂 Subir Plantilla de Informe en Word (.docx):", type=["docx"])
    
    plantilla_extraida = ""
    if archivo_plantilla is not None:
        plantilla_extraida = engine.extraer_texto_docx(archivo_plantilla)
        if "Error" not in plantilla_extraida:
            st.success(f"✅ Plantilla '{archivo_plantilla.name}' cargada correctamente con éxito.")
            with st.expander("Ver estructura detectada de tu plantilla"):
                st.text(plantilla_extraida)
        else:
            st.error(plantilla_extraida)

    st.divider()

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
    
    if st.button("📑 Redactar Informe Clínico"):
        if not api_key:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        else:
            datos_dict = {
                "nombre": nombre, "edad": edad, "genero": genero, "ocupacion": ocupacion,
                "motivo": motivo, "problema_actual": problema_actual,
                "pruebas_aplicadas": pruebas_aplicadas, "observaciones": observaciones,
                "diagnostico": diagnostico
            }
            with st.spinner("Procesando datos y redactando el informe..."):
                res = engine.generar_informe_premium(datos_dict, enfoque, plantilla_extraida, api_key)
                st.markdown(res)
                
                # Botón de Descarga en Word
                doc_bytes = engine.crear_documento_word(f"Informe Psicológico - {nombre or 'Paciente'}", res)
                st.download_button(
                    label="📥 Descargar Informe en Word (.docx)",
                    data=doc_bytes,
                    file_name=f"Informe_Psicologico_{nombre or 'Paciente'}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

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
# TAB 5: GUÍAS PSICOEDUCATIVAS CON DESCARGA
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
                
                # Botón de Descarga Word
                doc_bytes = engine.crear_documento_word(f"Guía Psicoeducativa: {diag_base}", res)
                st.download_button(
                    label="📥 Descargar Guía en Word (.docx)",
                    data=doc_bytes,
                    file_name=f"Guia_Psicoeducativa_{destinatario}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

# ---------------------------------------------------------
# TAB 6: CORRECTOR DE PUNTAJES PSICOMÉTRICOS
# ---------------------------------------------------------
with tab6:
    st.subheader("🧮 Corrector e Interpretador de Puntajes Psicométricos")
    st.caption("Ingresa los puntajes obtenidos (Directos, Percentiles, Escalones o T) para generar una interpretación técnica automática.")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        prueba_nom = st.text_input("Nombre de la Prueba:", placeholder="Ej: WISC-V, BDI-II, STAI, Figura Completa de Rey...")
    with col_p2:
        edad_p = st.number_input("Edad del evaluado:", min_value=1, max_value=100, value=edad_paciente)
        
    puntajes_input = st.text_area(
        "Ingresa los puntajes o subescalas obtenidos:", 
        height=120, 
        placeholder="Ej:\n- Comprensión Verbal: Directo 35, Percentil 75\n- Visoperceptiva: Escalar 8\n- Memoria de Trabajo: Percentil 12 (Bajo)\n- Índice Total: CI 105"
    )
    
    if st.button("📊 Interpretar y Clasificar Puntajes"):
        if not api_key:
            st.error("Por favor, ingresa tu API Key en la barra lateral.")
        elif not prueba_nom.strip() or not puntajes_input.strip():
            st.warning("Completa el nombre de la prueba y los puntajes.")
        else:
            with st.spinner("Procesando baremos e interpretando puntajes..."):
                res = engine.interpretar_puntajes_psicometricos(prueba_nom, puntajes_input, edad_p, api_key)
                st.markdown(res)
                
                # Botón de Descarga Word
                doc_bytes = engine.crear_documento_word(f"Interpretación Psicométrica - {prueba_nom}", res)
                st.download_button(
                    label="📥 Descargar Interpretación en Word (.docx)",
                    data=doc_bytes,
                    file_name=f"Resultado_{prueba_nom}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
