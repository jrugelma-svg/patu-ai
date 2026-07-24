import streamlit as st
import os
from engine import (
    analizar_caso_inicial, 
    obtener_pruebas_psicometricas, 
    generar_diagnostico_multiaxial
)

# Configuración principal de la página
st.set_page_config(
    page_title="PATU AI - Asistente Clínico",
    page_icon="🧠",
    layout="wide"
)

# Estilos CSS personalizados basados en el logo oficial
st.markdown("""
    <style>
    :root {
        --primary-coral: #FF6584;
        --secondary-green: #48A14D;
        --accent-orange: #FF9E2A;
        --dark-text: #633A2B;
    }

    .stButton > button {
        background: linear-gradient(135deg, #FF6584 0%, #FF9E2A 100%);
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    .stTextArea label {
        color: #633A2B !important;
        font-weight: 600;
    }

    .custom-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 6px solid #48A14D;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- OBTENER API KEY AUTOMÁTICAMENTE ---
# 1. Busca en los secretos de la nube (Streamlit Secrets)
# 2. Busca en las variables de entorno locales
# 3. Si no hay, permite ingresar una manualmente en la barra lateral
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

# ---------------- BARRA LATERAL ----------------
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    elif os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🦆 PATU AI")

    st.markdown("---")
    st.header("⚙️ Configuración")
    
    # Si la clave no está preconfigurada en la nube, muestra el campo de entrada
    if not api_key:
        api_key = st.text_input(
            "Clave de API de Gemini",
            type="password",
            help="Introduce tu API Key para conectar con la IA."
        )
    else:
        st.success("🟢 Sistema Conectado a Gemini AI")

    st.info("💡 **PATU AI** unifica la comprensión del DSM-5-TR mediante lenguaje natural y análisis multinivel.")

# ---------------- ENCABEZADO PRINCIPAL ----------------
col_logo, col_titulo = st.columns([1, 4])

with col_logo:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=150)
    elif os.path.exists("logo.png"):
        st.image("logo.png", width=150)

with col_titulo:
    st.markdown("<h1 style='color: #FF6584; margin-bottom: 0;'>PATU AI</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #FF9E2A; margin-top: 0;'>Psychologists United Across America</h4>", unsafe_allow_html=True)
    st.caption("Asistente pedagógico para el análisis sintomático y evaluación psicopatológica.")

st.markdown("---")

# ---------------- ÁREA DE INGRESO ----------------
st.subheader("📝 Motivo de Consulta / Narrativa Clínica Libre")
caso_texto = st.text_area(
    "Ingresa la sintomatología expresada por el paciente (puedes redactar en lenguaje informal o coloquial):",
    height=140,
    placeholder="Ejemplo: El paciente comenta que no logra concentrarse en el trabajo, se distrae a cada rato, siente un nudo en el pecho por las tardes y le cuesta conciliar el sueño desde hace un par de semanas..."
)

# Estados de sesión para controlar el flujo a demanda
if "analisis_hecho" not in st.session_state:
    st.session_state.analisis_hecho = False
if "ver_pruebas" not in st.session_state:
    st.session_state.ver_pruebas = False
if "ver_multiaxial" not in st.session_state:
    st.session_state.ver_multiaxial = False

# Botón Principal
if st.button("🚀 Analizar Caso Clínico"):
    if not api_key:
        st.error("🔑 La clave de API no está configurada. Ingrésala en la barra lateral.")
    elif not caso_texto.strip():
        st.warning("Escribe un motivo de consulta o narrativa clínica para poder realizar el análisis.")
    else:
        st.session_state.analisis_hecho = True
        st.session_state.ver_pruebas = False
        st.session_state.ver_multiaxial = False

# ---------------- MOSTRAR RESULTADOS ----------------
if st.session_state.analisis_hecho:
    st.markdown("---")
    
    with st.spinner("Analizando semejanzas diagnósticas y brechas clínicas..."):
        res_inicial = analizar_caso_inicial(caso_texto, api_key)
        st.markdown(res_inicial)

    st.markdown("---")
    st.subheader("🛠️ Profundizar Evaluación (Opciones a Demanda)")
    
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("🧪 Sugerir Pruebas Psicométricas"):
            st.session_state.ver_pruebas = True

    with col_btn2:
        if st.button("📋 Formular Diagnóstico Multiaxial"):
            st.session_state.ver_multiaxial = True

    # Despliegue Opcional 1: Pruebas Psicométricas
    if st.session_state.ver_pruebas:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        with st.spinner("Generando batería psicométrica sugerida..."):
            pruebas_res = obtener_pruebas_psicometricas(caso_texto, api_key)
            st.markdown(pruebas_res)
        st.markdown("</div>", unsafe_allow_html=True)

    # Despliegue Opcional 2: Diagnóstico Multiaxial
    if st.session_state.ver_multiaxial:
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.markdown("### 📋 Formulación Diagnóstica Multiaxial")
        
        datos_extra = st.text_area(
            "Ingresa información contextual adicional (estresores familiares/laborales, antecedentes médicos, etc.):",
            placeholder="Ejemplo: Situación de despido laboral reciente, sin antecedentes médicos relevantes, cuenta con apoyo familiar..."
        )
        
        if st.button("⚡ Generar Evaluación Multiaxial (Ejes I al V)"):
            with st.spinner("Estructurando los 5 Ejes del DSM..."):
                multi_res = generar_diagnostico_multiaxial(caso_texto, datos_extra, api_key)
                st.markdown(multi_res)
        st.markdown("</div>", unsafe_allow_html=True)
# ---------------------------------------------------------
# 8. Pie de página y Aviso de Copyright / Nota Legal
# ---------------------------------------------------------
st.markdown("---")

footer_code = """
<div style="text-align: center; color: #888888; padding: 10px; font-size: 0.85rem;">
    <p>© 2026 <b>PATU AI</b>. Todos los derechos reservados.</p>
    <p><b>Creador y Titular de Propiedad Intelectual:</b> J. Rugel</p>
    <hr style="border: 0.5px solid #333333; margin: 10px auto; width: 50%;">
    <p style="font-size: 0.75rem; color: #aaaaaa;">
        <b>Aviso Legal / Disclaimer:</b> PATU AI es un sistema de apoyo y consulta clínica basado en Inteligencia Artificial. 
        No emite diagnósticos médicos definitivos ni sustituye el criterio ni la evaluación clínica de un profesional de la salud mental colegiado.
    </p>
</div>
"""

st.markdown(footer_code, unsafe_allow_html=True)
