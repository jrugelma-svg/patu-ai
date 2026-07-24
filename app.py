import os
import streamlit as st
import engine

# 1. Configuración inicial de la página
st.set_page_config(
    page_title="PATU AI - Asistente Clínico",
    page_icon="🦆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Ocultar la barra superior, menú de Streamlit, footer y botón de GitHub/Lápiz
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppHeader {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 3. Encabezado principal de la aplicación
st.title("🦆 PATU AI")
st.subtitle("Asistente para Diagnóstico DSM-5-TR, Psicometría y Evaluación Multiaxial")

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
