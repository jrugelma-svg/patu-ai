import os
import base64
import streamlit as st
import engine

# 1. Configuración inicial de la página
st.set_page_config(
    page_title="PATU AI • Workstation Clínica",
    page_icon="logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Función para codificar la imagen del logo a Base64
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

img_base64 = get_image_base64("logo.jpg")

# 3. Estilos CSS Personalizados con bordes rosados y tarjeta Premium
custom_css = """
<style>
    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}

    /* Fondo exacto coincidente con la imagen del logo */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F8F8F8 !important;
        color: #2D3748 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Tipografías oscuras para lectura clara */
    p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #2D3748 !important;
    }

    /* Tarjetas principales limpias */
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
        position: relative;
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

    /* Insignia Premium */
    .premium-badge {
        background: linear-gradient(90deg, #E11D48, #FB7185);
        color: #FFFFFF !important;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 8px;
    }

    /* Campo de Texto (Textarea) */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;
        border: 1px solid #DCDCDC !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
    }

    .stTextArea textarea:focus {
        border-color: #E11D48 !important;
        box-shadow: 0 0 0 3px rgba(225, 29, 72, 0.15) !important;
    }

    /* ESTILO GENERAL DE BOTONES CON BORDES ROSADOS */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease-in-out !important;
    }

    /* Botón Primario (Analizar) */
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

    /* Botones Secundarios */
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

# 4. Verificación de la API Key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = ""

if not api_key:
    st.error("⚠️ Clave de API no detectada. Configura `GEMINI_API_KEY` en Streamlit Cloud.")
    st.stop()

# ---------------------------------------------------------
# 5. Estructura Split View (2 Columnas)
# ---------------------------------------------------------
col_izquierda, col_derecha = st.columns([0.38, 0.62], gap="large")

# =========================================================
# COLUMNA IZQUIERDA: Panel de Entrada y Acciones
# =========================================================
with col_izquierda:
    # Encabezado / Logo
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

    # Bloque 1: Formulario de Entrada
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

    # Bloque 2: Módulos a Demanda (Tercer Cuadro con versión PREMIUM)
    st.markdown('''
    <div class="premium-card">
        <span class="premium-badge">⭐ Módulos Premium</span>
        <h4 style="margin: 4px 0 2px 0;">🛠️ Evaluaciones Avanzadas</h4>
        <p style="font-size: 0.85rem; color: #64748B !important; margin-bottom: 12px;">Genera reportes técnicos especializados a demanda:</p>
    </div>
    ''', unsafe_allow_html=True)
    
    btn_pruebas = st.button("🧪 Sugerir Pruebas Psicométricas", type="secondary", use_container_width=True)
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    btn_multiaxial = st.button("📋 Formular Diagnóstico Multiaxial", type="secondary", use_container_width=True)


# =========================================================
# COLUMNA DERECHA: Visualización de Resultados
# =========================================================
with col_derecha:
    st.subheader("📊 Panel de Resultados Clínicos")
    
    # Manejo de acciones y renderizado
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
                st.markdown("### 🧪 Batería Psicométrica Recomendada")
                st.markdown("---")
                st.markdown(resultado_pruebas)
                st.markdown('</div>', unsafe_allow_html=True)

    elif btn_multiaxial:
        if not texto_caso.strip():
            st.warning("⚠️ Ingresa primero la narrativa del caso en el panel izquierdo.")
        else:
            with st.spinner("Generando formulación multiaxial..."):
                resultado_multiaxial = engine.generar_diagnostico_multiaxial(texto_caso, "", api_key)
                st.markdown('<div class="split-card">', unsafe_allow_html=True)
                st.markdown("### 📋 Evaluación Multiaxial")
                st.markdown("---")
                st.markdown(resultado_multiaxial)
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Estado inicial
        st.markdown('''
        <div class="split-card" style="text-align: center; padding: 40px 20px;">
            <p style="font-size: 2.5rem; margin-bottom: 10px;">🩺</p>
            <h3 style="margin-bottom: 8px;">Listo para evaluar</h3>
            <p style="color: #78716C !important; font-size: 0.95rem; max-width: 400px; margin: 0 auto;">
                Ingresa el motivo de consulta en el panel de la izquierda y presiona <b>Analizar Caso Clínico</b> para ver los resultados aquí.
            </p>
        </div>
        ''', unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. Pie de página (Footer)
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
