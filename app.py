import os
import base64
import streamlit as st
import engine

# 1. Configuración inicial de la página
st.set_page_config(
    page_title="PATU AI • Asistente Clínico",
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

# 3. Estilos CSS Personalizados: Forzar Modo Claro Soft & Warm
custom_css = """
<style>
    /* Ocultar menú y header nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}

    /* Forzar fondo claro cálido en toda la aplicación */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #FAF9F6 !important;
        color: #2D3748 !important;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Asegurar que todos los textos sean oscuros sobre fondo claro */
    p, span, label, h1, h2, h3, h4, h5, h6 {
        color: #2D3748 !important;
    }

    /* Tarjeta del Encabezado */
    .warm-header {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
    }

    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .logo-img {
        height: 60px;
        object-fit: contain;
    }

    .status-badge {
        background-color: #E6F4EA;
        color: #137333 !important;
        border: 1px solid #CEEAD6;
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
        background-color: #34A853;
        border-radius: 50%;
    }

    /* Tarjetas principales en blanco limpio */
    .warm-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }

    /* Campo de texto (Textarea) en modo claro */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;
        border: 1px solid #CBD5E0 !important;
        border-radius: 12px !important;
        font-size: 0.95rem !important;
    }

    .stTextArea textarea:focus {
        border-color: #2B6CB0 !important;
        box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15) !important;
    }

    /* Estilo de los Botones */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        border: none !important;
    }

    /* Botón Primario: Verde Esmeralda Cálido */
    .stButton > button[kind="primary"] {
        background: #0D9488 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #0F766E !important;
        box-shadow: 0 6px 16px rgba(13, 148, 136, 0.3) !important;
    }

    /* Botones Secundarios */
    .stButton > button[kind="secondary"] {
        background: #F1F5F9 !important;
        color: #334155 !important;
        border: 1px solid #CBD5E1 !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #E2E8F0 !important;
        color: #0F172A !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 4. Encabezado principal
logo_html = f'<img src="data:image/jpeg;base64,{img_base64}" class="logo-img">' if img_base64 else '<b>PATU AI</b>'

header_html = f"""
<div class="warm-header">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div class="logo-container">
            {logo_html}
        </div>
        <div>
            <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.2px; color: #0D9488; font-weight: 700;">Asistente Clínico de Psicología</span>
            <h2 style="margin: 0; font-size: 1.6rem; line-height: 1.2; color: #1E293B !important;">PATU AI <span style="font-size: 0.8rem; color: #64748B; font-weight: 400;">v1.0</span></h2>
        </div>
    </div>
    <div class="status-badge">
        <div class="status-dot"></div>
        Motor DSM-5-TR Listo
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 5. Verificación de la API Key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = ""

if not api_key:
    st.error("⚠️ Clave de API no detectada. Asegúrate de configurarla en Streamlit Cloud.")
    st.stop()

# 6. Módulo Principal: Narrativa Clínica
st.markdown('<div class="warm-card">', unsafe_allow_html=True)
st.subheader("📝 Motivo de Consulta / Narrativa Clínica Libre")
st.caption("Ingresa la sintomatología expresada por el paciente (puedes redactar en lenguaje informal o coloquial):")

texto_caso = st.text_area(
    label="Caso Clínico",
    placeholder="Ejemplo: Paciente refiere que desde hace 6 meses experimenta episodios repentinos de taquicardia, sudoración fría y sensación inminente de muerte...",
    height=150,
    label_visibility="collapsed"
)

col_btn1, col_btn2 = st.columns([0.3, 0.7])
with col_btn1:
    btn_analizar = st.button("🚀 Analizar Caso Clínico", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Ejecución del Análisis Inicial
if btn_analizar:
    if not texto_caso.strip():
        st.warning("⚠️ Por favor, ingresa la narrativa del caso clínico antes de continuar.")
    else:
        with st.spinner("Procesando análisis clínico y mapeo DSM-5-TR con PATU AI..."):
            resultado = engine.analizar_caso_inicial(texto_caso, api_key)
            st.markdown('<div class="warm-card">', unsafe_allow_html=True)
            st.markdown(resultado)
            st.markdown('</div>', unsafe_allow_html=True)

# 7. Mapeo a demanda
st.subheader("🛠️ Profundizar Evaluación (Opciones a Demanda)")

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="warm-card">', unsafe_allow_html=True)
    st.markdown("#### 🧪 Sugerir Pruebas Psicométricas")
    st.caption("Genera una batería psicométrica recomendada según los síntomas.")
    if st.button("Generar Batería Psicométrica", type="secondary", use_container_width=True):
        if not texto_caso.strip():
            st.warning("⚠️ Primero debes ingresar el motivo de consulta arriba.")
        else:
            with st.spinner("Generando batería psicométrica recomendada..."):
                resultado_pruebas = engine.obtener_pruebas_psicometricas(texto_caso, api_key)
                st.markdown("---")
                st.markdown(resultado_pruebas)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="warm-card">', unsafe_allow_html=True)
    st.markdown("#### 📋 Formular Diagnóstico Multiaxial")
    st.caption("Estructura la evaluación según el modelo multiaxial tradicional.")
    if st.button("Formular Diagnóstico Multiaxial", type="secondary", use_container_width=True):
        if not texto_caso.strip():
            st.warning("⚠️ Primero debes ingresar el motivo de consulta arriba.")
        else:
            with st.spinner("Generando estructura de Diagnóstico Multiaxial..."):
                resultado_multiaxial = engine.generar_diagnostico_multiaxial(texto_caso, "", api_key)
                st.markdown("---")
                st.markdown(resultado_multiaxial)
    st.markdown('</div>', unsafe_allow_html=True)

# 8. Pie de Página
st.markdown("---")

footer_code = """
<div style="text-align: center; color: #64748B; padding: 15px; font-size: 0.85rem;">
    <p style="margin-bottom: 5px;">© 2026 <b>PATU AI</b>. Todos los derechos reservados.</p>
    <p style="margin-bottom: 10px;"><b>Creador y Titular de Propiedad Intelectual:</b> J. Rugel</p>
    <p style="font-size: 0.75rem; color: #94A3B8; max-width: 800px; margin: 0 auto;">
        <b>Aviso Legal / Disclaimer:</b> PATU AI es un sistema de apoyo y consulta clínica basado en Inteligencia Artificial. 
        No emite diagnósticos médicos definitivos ni sustituye el criterio ni la evaluación clínica de un profesional de la salud mental colegiado.
    </p>
</div>
"""
st.markdown(footer_code, unsafe_allow_html=True)
