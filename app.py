import os
import io
import base64
import streamlit as st
from docx import Document
import engine

# 1. Configuración inicial de la página
st.set_page_config(
    page_title="PATU AI • Workstation Clínica",
    page_icon="logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar estados de navegación y sesión
if "modo_premium" not in st.session_state:
    st.session_state.modo_premium = False

if "ultimo_informe" not in st.session_state:
    st.session_state.ultimo_informe = None

if "ultimo_nombre_paciente" not in st.session_state:
    st.session_state.ultimo_nombre_paciente = "Paciente"

if "texto_transcrito_temp" not in st.session_state:
    st.session_state.texto_transcrito_temp = None


# 2. Función para codificar la imagen del logo a Base64
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

img_base64 = get_image_base64("logo.jpg")


# 3. Función auxiliar para convertir el Markdown a un archivo .docx (Word)
def generar_word_desde_markdown(texto_markdown):
    doc = Document()
    doc.add_heading('INFORME PSICOLÓGICO', level=1)
    
    lineas = texto_markdown.split('\n')
    for linea in lineas:
        linea_clean = linea.strip()
        if not linea_clean:
            continue
            
        if linea_clean.startswith('# '):
            doc.add_heading(linea_clean.replace('# ', ''), level=1)
        elif linea_clean.startswith('## '):
            doc.add_heading(linea_clean.replace('## ', ''), level=2)
        elif linea_clean.startswith('### '):
            doc.add_heading(linea_clean.replace('### ', ''), level=3)
        elif linea_clean.startswith('* ') or linea_clean.startswith('- '):
            texto = linea_clean[2:].replace('**', '')
            doc.add_paragraph(texto, style='List Bullet')
        else:
            texto = linea_clean.replace('**', '')
            doc.add_paragraph(texto)
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# 4. Estilos CSS Personalizados
custom_css = """
<style>
    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}

    /* Fondo general */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F8F8F8 !important;
        color: #2D3748 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #2D3748 !important;
    }

    /* Tarjetas principales */
    .split-card {
        background: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    }

    /* Tarjeta Premium Especial */
    .premium-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF5F7 100%);
        border: 2px solid #FDA4AF;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.06);
    }

    /* Contenedor del Logo */
    .logo-container {
        background: transparent !important;
        text-align: center;
        margin-bottom: 12px;
        padding: 0;
    }

    .logo-img {
        max-height: 95px;
        width: auto;
        object-fit: contain;
        mix-blend-mode: multiply;
    }

    .status-badge {
        background-color: #FEF3C7;
        color: #D97706 !important;
        border: 1px solid #FDE68A;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #F59E0B;
        border-radius: 50%;
    }

    .premium-badge {
        background: linear-gradient(90deg, #E11D48, #FB7185);
        color: #FFFFFF !important;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* Textarea e Inputs */
    .stTextArea textarea, .stTextInput input {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;
        border: 1px solid #DCDCDC !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #E11D48 !important;
        box-shadow: 0 0 0 3px rgba(225, 29, 72, 0.15) !important;
    }

    /* Botones */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease-in-out !important;
    }

    .stButton > button[kind="primary"] {
        background: #E11D48 !important;
        color: #FFFFFF !important;
        border: 2px solid #BE123C !important;
        box-shadow: 0 4px 12px rgba(225, 29, 72, 0.2) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #BE123C !important;
        border-color: #9F1239 !important;
        box-shadow: 0 6px 18px rgba(225, 29, 72, 0.3) !important;
        transform: translateY(-1px);
    }

    .stButton > button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #9F1239 !important;
        border: 2px solid #FDA4AF !important;
        box-shadow: 0 2px 8px rgba(225, 29, 72, 0.05) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #FFF1F2 !important;
        color: #881337 !important;
        border-color: #F43F5E !important;
        box-shadow: 0 4px 12px rgba(225, 29, 72, 0.15) !important;
        transform: translateY(-1px);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 5. Verificación de la API Key
api_key = os.getenv("GROQ_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = ""

if not api_key:
    st.error("⚠️ Clave de API no detectada. Configura la API Key en las variables de entorno o Secrets.")
    st.stop()


# ---------------------------------------------------------
# VISTA 1: EDITOR DE INFORMES PREMIUM & HERRAMIENTAS AVANZADAS
# ---------------------------------------------------------
if st.session_state.modo_premium:
    
    col_nav, _ = st.columns([0.3, 0.7])
    with col_nav:
        if st.button("⬅️ Volver a Workstation Rápido", type="secondary"):
            st.session_state.modo_premium = False
            st.rerun()

    st.markdown('''
    <div style="text-align: center; margin-top: 10px; margin-bottom: 25px;">
        <span class="premium-badge">⭐ MÓDULO PREMIUM</span>
        <h2 style="margin: 5px 0;">Herramientas Diagnósticas e Informes Integrados</h2>
        <p style="color: #64748B !important;">Genera reportes técnicos, procesa audios/transcripciones extensas y consulta baterías psicométricas.</p>
    </div>
    ''', unsafe_allow_html=True)

    # Navegación interna por Pestañas
    tab_informe, tab_transcripcion, tab_pruebas = st.tabs([
        "📄 Generador de Informes (.docx)", 
        "🎙️ Analizador de Audios y Transcripciones", 
        "🧪 Buscador de Pruebas"
    ])

    # -----------------------------------------------------
    # PESTAÑA 1: GENERADOR DE INFORMES (CON EXPORTADOR WORD)
    # -----------------------------------------------------
    with tab_informe:
        col_form, col_resultado = st.columns([0.45, 0.55], gap="large")

        with col_form:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown("### 📝 Datos del Caso / Evaluación")
            
            enfoque = st.selectbox(
                "🎯 Selecciona el Enfoque del Informe:",
                ["Clínico", "Educativo", "Organizacional"]
            )

            st.markdown("---")
            st.markdown("##### 👤 Datos de Filiación")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                nombre = st.text_input("Nombre / Iniciales:", placeholder="Ej. J.P.")
                edad = st.text_input("Edad:", placeholder="Ej. 28 años")
            with col_f2:
                genero = st.text_input("Sexo / Género:", placeholder="Ej. Femenino")
                ocupacion = st.text_input("Ocupación / Escolaridad:", placeholder="Ej. Estudiante universitario")

            st.markdown("---")
            st.markdown("##### 📋 Contenido Clínico (Acepta notas o palabras sueltas)")
            
            motivo = st.text_area("1. Motivo de Consulta:", placeholder="Ej: Ansiedad, problemas para dormir...", height=70)
            problema_actual = st.text_area("2. Problema Actual / Antecedentes:", placeholder="Ej: Rompimiento reciente...", height=80)
            pruebas_aplicadas = st.text_area("3. Pruebas / Instrumentos Aplicados:", placeholder="Ej: BDI-II, HAM-A...", height=70)
            observaciones = st.text_area("4. Observaciones Conductuales:", placeholder="Ej: Contacto visual escaso...", height=70)
            diagnostico = st.text_area("5. Impresión Diagnóstica / Conclusiones:", placeholder="Ej: Sospecha de episodio depresivo...", height=70)

            btn_generar_informe = st.button("🚀 Redactar e Integrar Informe con IA", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_resultado:
            st.subheader("📄 Vista Previa del Documento")

            if btn_generar_informe:
                datos_dict = {
                    "nombre": nombre, "edad": edad, "genero": genero, "ocupacion": ocupacion,
                    "motivo": motivo, "problema_actual": problema_actual,
                    "pruebas_aplicadas": pruebas_aplicadas, "observaciones": observaciones,
                    "diagnostico": diagnostico
                }
                with st.spinner(f"Sintetizando e integrando el informe con enfoque {enfoque}..."):
                    informe_final = engine.generar_informe_premium(datos_dict, enfoque, api_key)
                    st.session_state.ultimo_informe = informe_final
                    st.session_state.ultimo_nombre_paciente = nombre if nombre.strip() else "Paciente"

            if st.session_state.ultimo_informe:
                st.markdown('<div class="split-card">', unsafe_allow_html=True)
                st.markdown(st.session_state.ultimo_informe)
                st.markdown('</div>', unsafe_allow_html=True)

                docx_buffer = generar_word_desde_markdown(st.session_state.ultimo_informe)
                nombre_archivo = f"Informe_Psicologico_{st.session_state.ultimo_nombre_paciente}.docx"

                st.download_button(
                    label="📥 Descargar Informe en Word (.docx)",
                    data=docx_buffer,
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.markdown('''
                <div class="split-card" style="text-align: center; padding: 50px 20px;">
                    <p style="font-size: 3rem; margin-bottom: 10px;">📄</p>
                    <h3>Espacio de Trabajo Premium</h3>
                    <p style="color: #78716C !important; font-size: 0.95rem; max-width: 420px; margin: 0 auto;">
                        Completa los campos de la izquierda y presiona <b>Redactar e Integrar Informe con IA</b>.
                    </p>
                </div>
                ''', unsafe_allow_html=True)

    # -----------------------------------------------------
    # PESTAÑA 2: ANALIZADOR DE AUDIOS Y TRANCRIPCIONES
    # -----------------------------------------------------
    with tab_transcripcion:
        col_t_left, col_t_right = st.columns([0.45, 0.55], gap="large")

        with col_t_left:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown("### 🎙️ Procesador de Sesión Extensa")
            st.caption("Sube la grabación de audio de la consulta o pega directamente las notas/transcripción.")

            opcion_entrada = st.radio(
                "Selecciona el origen de la sesión:",
                ["📁 Subir Grabación de Audio", "✍️ Pegar Texto / Notas Directas"],
                horizontal=True
            )

            transcripcion_para_analizar = ""

            if "Subir Grabación" in opcion_entrada:
                audio_file = st.file_uploader(
                    "Carga el archivo de audio (.mp3, .m4a, .wav, .ogg):",
                    type=["mp3", "m4a", "wav", "ogg", "mp4"]
                )
                if audio_file:
                    st.audio(audio_file)
                    btn_procesar_audio = st.button("⚡ Transcribir Audio y Analizar con IA", type="primary", use_container_width=True)
                    
                    if btn_procesar_audio:
                        with st.spinner("1/2 Transcribiendo audio con Whisper AI..."):
                            texto_transcrito = engine.transcribir_audio_groq(audio_file, api_key)
                            
                        if texto_transcrito.startswith("⚠️"):
                            st.error(texto_transcrito)
                        else:
                            st.success("✅ Transcripción completada con éxito.")
                            st.session_state.texto_transcrito_temp = texto_transcrito
                            transcripcion_para_analizar = texto_transcrito

            else:
                transcripcion_input = st.text_area(
                    "Transcripción o Registro Verbal de la Sesión:",
                    placeholder="[Paciente 10:15]: Siento que ya no puedo con la presión del trabajo...\n[Terapeuta 10:16]: ¿Qué situaciones específicas han detonado esta sensación?...",
                    height=280
                )
                btn_analizar_texto = st.button("🔍 Analizar Texto de Sesión", type="primary", use_container_width=True)
                if btn_analizar_texto:
                    transcripcion_para_analizar = transcripcion_input

            st.markdown('</div>', unsafe_allow_html=True)

        with col_t_right:
            st.subheader("📊 Análisis Diagnóstico Cualitativo")

            if transcripcion_para_analizar.strip():
                with st.spinner("2/2 Analizando discurso, detectando afecto y evaluando alertas de riesgo..."):
                    resultado_transcripcion = engine.analizar_transcripcion_sesion(transcripcion_para_analizar, api_key)
                    
                    if st.session_state.texto_transcrito_temp:
                        with st.expander("📄 Ver Transcripción Literal Generada"):
                            st.write(st.session_state.texto_transcrito_temp)
                    
                    st.markdown('<div class="split-card">', unsafe_allow_html=True)
                    st.markdown(resultado_transcripcion)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div class="split-card" style="text-align: center; padding: 50px 20px;">
                    <p style="font-size: 3rem; margin-bottom: 10px;">🎙️</p>
                    <h3>Analizador de Audio y Diálogo Terapéutico</h3>
                    <p style="color: #78716C !important; font-size: 0.95rem; max-width: 420px; margin: 0 auto;">
                        Sube la <b>grabación de audio</b> o pega las <b>notas de la sesión</b> a la izquierda para extraer automáticamente <b>alertas de riesgo, afecto, palabras recurrentes y puntos clave</b>.
                    </p>
                </div>
                ''', unsafe_allow_html=True)

    # -----------------------------------------------------
    # PESTAÑA 3: BUSCADOR DE PRUEBAS
    # -----------------------------------------------------
    with tab_pruebas:
        st.markdown('<div class="split-card">', unsafe_allow_html=True)
        st.markdown("### 🔗 Buscador de Fuentes y Enlaces de Pruebas")
        col_b1, col_b2 = st.columns([0.7, 0.3])
        with col_b1:
            prueba_query = st.text_input("Buscar prueba psicométrica:", placeholder="Ej. STAI, WAIS-IV, Beck Depression...", label_visibility="collapsed")
        with col_b2:
            btn_buscar_prueba = st.button("🔎 Buscar Recursos", type="secondary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if btn_buscar_prueba:
            if not prueba_query.strip():
                st.warning("⚠️ Escribe el nombre o acrónimo de la prueba a buscar.")
            else:
                with st.spinner(f"Buscando ficha técnica y referencias para {prueba_query}..."):
                    resultado_busqueda = engine.buscar_recursos_pruebas(prueba_query, api_key)
                    st.markdown('<div class="split-card">', unsafe_allow_html=True)
                    st.markdown(resultado_busqueda)
                    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# VISTA 2: WORKSTATION PRINCIPAL (VISTA CLÁSICA)
# ---------------------------------------------------------
else:
    col_izquierda, col_derecha = st.columns([0.38, 0.62], gap="large")

    with col_izquierda:
        logo_html = f'<img src="data:image/jpeg;base64,{img_base64}" class="logo-img">' if img_base64 else '<b>PATU AI</b>'
        
        st.markdown(f'''
        <div class="logo-container">
            {logo_html}
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('''
        <div style="text-align: center; margin-bottom: 20px;">
            <div class="status-badge">
                <div class="status-dot"></div>
                DSM-5-TR Motor Activo
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Bloque 1: Formulario Rápido
        st.markdown('<div class="split-card">', unsafe_allow_html=True)
        st.subheader("📝 Motivo de Consulta")
        st.caption("Escribe la narrativa clínica del paciente:")

        texto_caso = st.text_area(
            label="Caso Clínico",
            placeholder="Ejemplo: Paciente refiere que desde hace 6 meses experimenta episodios de ansiedad, angustia y palpitaciones...",
            height=180,
            label_visibility="collapsed"
        )

        btn_analizar = st.button("🚀 Analizar Caso Clínico", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Bloque 2: Acceso a Módulos Premium
        st.markdown('''
        <div class="premium-card">
            <span class="premium-badge">⭐ Módulos Premium</span>
            <h4 style="margin: 4px 0 2px 0;">🛠️ Evaluaciones e Informes</h4>
            <p style="font-size: 0.85rem; color: #64748B !important; margin-bottom: 12px;">Genera reportes técnicos y consulta baterías psicométricas:</p>
        </div>
        ''', unsafe_allow_html=True)
        
        btn_ir_premium = st.button("⭐ Abrir Generador de Informes Premium", type="primary", use_container_width=True)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        btn_pruebas = st.button("🧪 Sugerir Pruebas Psicométricas", type="secondary", use_container_width=True)
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        btn_multiaxial = st.button("📋 Formular Diagnóstico Multiaxial", type="secondary", use_container_width=True)

        if btn_ir_premium:
            st.session_state.modo_premium = True
            st.rerun()

    with col_derecha:
        st.subheader("📊 Panel de Resultados Clínicos")
        
        if btn_analizar:
            if not texto_caso.strip():
                st.warning("⚠️ Ingresa primero la narrativa del caso en el panel izquierdo.")
            else:
                with st.spinner("Ejecutando análisis sintomatológico DSM-5-TR..."):
                    resultado = engine.analizar_caso_inicial(texto_caso, api_key)
                    st.markdown('<div class="split-card">', unsafe_allow_html=True)
                    st.markdown("### 📌 Mapeo y Diagnóstico Inicial")
                    st.markdown("---")
                    st.markdown(resultado)
                    st.markdown('</div>', unsafe_allow_html=True)

        elif btn_pruebas:
            if not texto_caso.strip():
                st.warning("⚠️ Ingresa primero la narrativa del caso en el panel izquierdo.")
            else:
                with st.spinner("Compilando batería psicométrica recomendada..."):
                    resultado_pruebas = engine.obtener_pruebas_psicometricas(texto_caso, api_key)
                    st.markdown('<div class="split-card">', unsafe_allow_html=True)
                    st.markdown(resultado_pruebas)
                    st.markdown('</div>', unsafe_allow_html=True)

        elif btn_multiaxial:
            if not texto_caso.strip():
                st.warning("⚠️ Ingresa primero la narrativa del caso en el panel izquierdo.")
            else:
                with st.spinner("Generando formulación multiaxial..."):
                    resultado_multiaxial = engine.generar_diagnostico_multiaxial(texto_caso, "", api_key)
                    st.markdown('<div class="split-card">', unsafe_allow_html=True)
                    st.markdown(resultado_multiaxial)
                    st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.markdown('''
            <div class="split-card" style="text-align: center; padding: 40px 20px;">
                <p style="font-size: 2.5rem; margin-bottom: 10px;">🩺</p>
                <h3 style="margin-bottom: 8px;">Listo para evaluar</h3>
                <p style="color: #78716C !important; font-size: 0.95rem; max-width: 400px; margin: 0 auto;">
                    Ingresa el motivo de consulta en el panel de la izquierda y presiona <b>Analizar Caso Clínico</b> o accede al <b>Generador Premium</b>.
                </p>
            </div>
            ''', unsafe_allow_html=True)

# ---------------------------------------------------------
# Pie de página (Footer)
# ---------------------------------------------------------
st.markdown("---")
footer_code = """
<div style="text-align: center; color: #78716C; padding: 15px; font-size: 0.85rem;">
    <p style="margin-bottom: 5px;">© 2026 <b>PATU AI</b>. Todos los derechos reservados.</p>
    <p style="margin-bottom: 10px;"><b>Creador y Titular de Propiedad Intelectual:</b> J. Rugel</p>
    <p style="font-size: 0.75rem; color: #A8A29E; max-width: 800px; margin: 0 auto;">
        <b>Aviso Legal / Disclaimer:</b> PATU AI es un sistema de asistencia clínica basado en Inteligencia Artificial. 
        No emite diagnósticos médicos definitivos ni reemplaza la evaluación directa de un profesional de la salud mental colegiado.
    </p>
</div>
"""
st.markdown(footer_code, unsafe_allow_html=True)
