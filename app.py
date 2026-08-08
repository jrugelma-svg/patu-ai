import os
import streamlit as st
import engine

# 1. Configuración inicial de la página
st.set_page_config(
    page_title="PATU AI - Asistente Clínico",
    page_icon="logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Ocultar la barra superior, menú de Streamlit, footer predeterminado y headers
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 3. Encabezado principal con logo en tamaño claro y alineación perfecta
header_html = """
<div style="display: flex; align-items: center; gap: 20px; margin-bottom: 10px;">
    <img src="app/static/logo.jpg" style="height: 110px; border-radius: 12px; object-fit: contain;" onerror="this.src='logo.jpg'">
    <div>
        <h1 style="margin: 0; padding: 0; font-size: 2.8rem; font-weight: 700; color: #FFFFFF;">PATU AI</h1>
        <p style="margin: 5px 0 0 0; color: #AAAAAA; font-size: 1rem;">Asistente para Diagnóstico DSM-5-TR, Psicometría y Evaluación Multiaxial</p>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

st.markdown("---")

# 4. Obtención segura de la API Key (compatible con Render y Streamlit Cloud)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = ""

if not api_key:
    st.error("⚠️ No se encontró la API Key. Por favor, asegúrate de configurarla en Render (Environment Variables) o en Streamlit Cloud (Secrets).")
    st.stop()

# 5. Entrada del Motivo de Consulta
st.subheader("📝 Motivo de Consulta / Narrativa Clínica Libre")
st.caption("Ingresa la sintomatología expresada por el paciente (puedes redactar en lenguaje informal o coloquial):")

texto_caso = st.text_area(
    label="Caso Clínico",
    placeholder="Ejemplo: Paciente refiere que desde hace 6 meses experimenta episodios repentinos de taquicardia, sudoración fría y sensación inminente de muerte...",
    height=150,
    label_visibility="collapsed"
)

# 6. Botón de Análisis Inicial
if st.button("🚀 Analizar Caso Clínico", type="primary"):
    if not texto_caso.strip():
        st.warning("⚠️ Por favor, ingresa la narrativa del caso clínico antes de continuar.")
    else:
        with st.spinner("Procesando análisis clínico y mapeo DSM-5-TR con PATU AI..."):
            resultado = engine.analizar_caso_inicial(texto_caso, api_key)
            st.markdown(resultado)

st.markdown("---")

# 7. Opciones de Profundización (A Demanda)
st.subheader("🛠️ Profundizar Evaluación (Opciones a Demanda)")

col1, col2 = st.columns(2)

with col1:
    if st.button("🧪 Sugerir Pruebas Psicométricas"):
        if not texto_caso.strip():
            st.warning("⚠️ Primero debes ingresar el motivo de consulta arriba.")
        else:
            with st.spinner("Generando batería psicométrica recomendada..."):
                resultado_pruebas = engine.obtener_pruebas_psicometricas(texto_caso, api_key)
                st.markdown(resultado_pruebas)

with col2:
    if st.button("📋 Formular Diagnóstico Multiaxial"):
        if not texto_caso.strip():
            st.warning("⚠️ Primero debes ingresar el motivo de consulta arriba.")
        else:
            with st.spinner("Generando estructura de Diagnóstico Multiaxial..."):
                resultado_multiaxial = engine.generar_diagnostico_multiaxial(texto_caso, "", api_key)
                st.markdown(resultado_multiaxial)

# ---------------------------------------------------------
# 8. Pie de página: Aviso de Derechos de Autor y Nota Legal
# ---------------------------------------------------------
st.markdown("---")

footer_code = """
<div style="text-align: center; color: #888888; padding: 15px; font-size: 0.85rem;">
    <p style="margin-bottom: 5px;">© 2026 <b>PATU AI</b>. Todos los derechos reservados.</p>
    <p style="margin-bottom: 10px;"><b>Creador y Titular de Propiedad Intelectual:</b> J. Rugel</p>
    <hr style="border: 0.5px solid #444444; margin: 10px auto; width: 40%;">
    <p style="font-size: 0.75rem; color: #aaaaaa; max-width: 800px; margin: 0 auto;">
        <b>Aviso Legal / Disclaimer:</b> PATU AI es un sistema de apoyo y consulta clínica basado en Inteligencia Artificial. 
        No emite diagnósticos médicos definitivos ni sustituye el criterio ni la evaluación clínica de un profesional de la salud mental colegiado.
    </p>
</div>
"""

st.markdown(footer_code, unsafe_allow_html=True)
