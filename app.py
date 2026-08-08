import os
import base64
import streamlit as st
import engine

# ---------------------------------------------------------
# 1. Configuración de la página
# ---------------------------------------------------------
st.set_page_config(
    page_title="PATU AI • Clinical SaaS Platform",
    page_icon="logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 2. Función para codificar imagen a Base64
# ---------------------------------------------------------
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

img_base64 = get_image_base64("logo.jpg")

# ---------------------------------------------------------
# 3. Estilos CSS Personalizados (Dark Emerald SaaS Theme)
# ---------------------------------------------------------
custom_css = """
<style>
    /* Ocultar elementos predeterminados de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}

    /* Fondo principal de la app */
    .stApp {
        background-color: #12181F;
        color: #E2E8F0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Contenedor del Encabezado (Glassmorphism Header) */
    .saas-header {
        background: rgba(30, 38, 48, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .logo-container {
        background-color: #FFFFFF;
        padding: 8px 16px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .logo-img {
        height: 55px;
        object-fit: contain;
    }

    .status-badge {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
    }

    /* Tarjetas del Sistema */
    .saas-card {
        background: #1E2630;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }

    /* Estilo del Textarea */
    .stTextArea textarea {
        background-color: #161D26 !important;
        color: #F1F5F9 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        font-size: 0.95rem !important;
    }

    .stTextArea textarea:focus {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2) !important;
    }

    /* Botones Personalizados */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        border: none !important;
    }

    /* Botón Primario */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }

    /* Botones Secundarios */
    .stButton > button[kind="secondary"] {
        background: #283342 !important;
        color: #E2E8F0 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #323F52 !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: #FFFFFF !important;
    }

    /* Títulos y Subtítulos */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. Encabezado SaaS (Header)
# ---------------------------------------------------------
logo_html = f'<img src="data:image/jpeg;base64,{img_base64}" class="logo-img">' if img_base64 else '<span style="color:#000; font-weight:bold;">PATU AI</span>'

header_html = f"""
<div class="saas-header">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div class="logo-container">
            {logo_html}
        </div>
        <div>
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; color: #10B981; font-weight: 700;">Clinical Intelligence Platform</span>
            <h2 style="margin: 0; font-size: 1.6rem; line-height: 1.2;">PATU AI <span style="font-size: 0.8rem; color: #64748B; font-weight: 400;">v1.0</span></h2>
        </div>
    </div>
    <div class="status-badge">
        <div class="status-dot"></div>
        DSM-5-TR Motor Activo
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. Verificación de la API Key
# ---------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = ""

if not api_key:
    st.error("⚠️ **Clave de API no detectada.** Por favor configura `GEMINI_API_KEY` en el panel de control de Streamlit Cloud.")
    st.stop()

# ---------------------------------------------------------
# 6. Módulo Principal: Narrativa Clínica
# ---------------------------------------------------------
st.markdown('<div class="saas-card">', unsafe_allow_html=True)
st.subheader("📝 Motivo de Consulta / Narrativa Clínica Libre")
st.caption("Introduce la sintomatología o la descripción del caso referida por el paciente:")

texto_caso = st.text_area(
    label="Caso Clínico",
    placeholder="Ejemplo: Paciente de 28 años refiere episodios recurrentes de ansiedad intensa, taquicardia y temor a perder el control en espacios públicos...",
    height=160,
    label_visibility="collapsed"
)

col_btn1, col_btn2 = st.columns([0.3, 0.7])
with col_btn1:
    btn_analizar = st.button("🚀 Analizar Caso Clínico", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Ejecución del Análisis Inicial
if btn_analizar:
    if not texto_caso.strip():
        st.warning("⚠️ Ingresa la narrativa del caso clínico antes de proceder.")
    else:
        with st.spinner("Procesando análisis sintomatológico y diagnóstico DSM-5-TR..."):
            resultado = engine.analizar_caso_inicial(texto_caso, api_key)
            st.markdown('<div class="saas-card">', unsafe_allow_html=True)
            st.markdown(resultado)
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. Módulo Secundario: Módulos a Demanda
# ---------------------------------------------------------
st.subheader("🛠️ Profundización Evaluativa")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown("#### 🧪 Batería Psicométrica")
    st.caption("Genera una propuesta de reactivos y pruebas estandarizadas acordes al cuadro clínico.")
    if st.button("Sugerir Pruebas Psicométricas", type="secondary", use_container_width=True):
        if not texto_caso.strip():
            st.warning("⚠️ Primero debes ingresar el motivo de consulta.")
        else:
            with st.spinner("Compilando batería de evaluación psicométrica..."):
                resultado_pruebas = engine.obtener_pruebas_psicometricas(texto_caso, api_key)
                st.markdown("---")
                st.markdown(resultado_pruebas)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    st.markdown("#### 📋 Evaluación Multiaxial")
    st.caption("Estructura la formulación clínica conforme al modelo multiaxial estandarizado.")
    if st.button("Formular Diagnóstico Multiaxial", type="secondary", use_container_width=True):
        if not texto_caso.strip():
            st.warning("⚠️ Primero debes ingresar el motivo de consulta.")
        else:
            with st.spinner("Sintetizando estructura multiaxial..."):
                resultado_multiaxial = engine.generar_diagnostico_multiaxial(texto_caso, "", api_key)
                st.markdown("---")
                st.markdown(resultado_multiaxial)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 8. Pie de página (Footer)
# ---------------------------------------------------------
st.markdown("---")

footer_code = """
<div style="text-align: center; color: #64748B; padding: 20px; font-size: 0.85rem;">
    <p style="margin-bottom: 4px;">© 2026 <b>PATU AI</b>. Todos los derechos reservados.</p>
    <p style="margin-bottom: 12px;"><b>Creador y Titular de Propiedad Intelectual:</b> J. Rugel</p>
    <p style="font-size: 0.75rem; color: #475569; max-width: 800px; margin: 0 auto; line-height: 1.4;">
        <b>Aviso Legal / Disclaimer:</b> PATU AI es un sistema de asistencia clínica impulsado por Inteligencia Artificial. 
        No emite diagnósticos médicos definitivos ni reemplaza la evaluación directa de un profesional de la salud mental colegiado.
    </p>
</div>
"""
st.markdown(footer_code, unsafe_allow_html=True)
