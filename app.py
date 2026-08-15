import streamlit as st
import engine
import database as db
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

# Inicializar Estados de Sesión
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
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
    .stApp { background-color: #FEFCE8 !important; font-family: 'Inter', system-ui, sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    h1, h2, h3, .stSubheader { color: #EA580C !important; font-weight: 800 !important; }
    p, label, span, div { color: #78350F !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #FEF3C7; padding: 8px 12px; border-radius: 16px; border: 2px solid #FDE68A; }
    .stTabs [data-baseweb="tab"] { height: 44px; border-radius: 12px; color: #92400E !important; font-weight: 700 !important; font-size: 0.9rem !important; border: none !important; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #16A34A 0%, #15803D 100%) !important; color: #FFFFFF !important; box-shadow: 0 4px 14px rgba(22, 163, 74, 0.35) !important; }
    .stTabs [aria-selected="true"] * { color: #FFFFFF !important; }
    .stButton > button, .stDownloadButton > button { background: linear-gradient(135deg, #FF7E7A 0%, #E05652 100%) !important; color: #FFFFFF !important; border: none !important; border-radius: 12px !important; padding: 0.75rem 1.4rem !important; font-weight: 800 !important; box-shadow: 0 4px 14px rgba(255, 126, 122, 0.4) !important; width: 100%; }
    .stButton > button *, .stDownloadButton > button * { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] { background: #FEF3C7 !important; border-right: 2px solid #FDE68A !important; }
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input { border-radius: 12px !important; border: 2px solid #FDE68A !important; background-color: #FFFFFF !important; color: #78350F !important; }
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
                    <h1 style="color: #EA580C !important; margin: 0; font-size: 2.1rem; font-weight: 900;">
                        Workstation Clínico
                        <span style="font-size: 0.85rem; background: #16A34A; color: #FFFFFF !important; padding: 4px 14px; border-radius: 20px; font-weight: 800;">v3.0 PRO</span>
                    </h1>
                    <p style="color: #92400E !important; margin: 4px 0 0 0; font-size: 1rem; font-weight: 700;">
                        PATU — Psychologists United Across America
                    </p>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# MÓDULO DE AUTENTICACIÓN (LOGIN / REGISTRO)
# =========================================================
if st.session_state["usuario"] is None:
    st.subheader("🔐 Acceso a la Plataforma Clínica")
    tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta Gratis"])
    
    with tab_login:
        col_l1, col_l2 = st.columns([1, 1])
        with col_l1:
            email_login = st.text_input("Correo Electrónico:", key="log_email")
            pass_login = st.text_input("Contraseña:", type="password", key="log_pass")
            if st.button("🚀 Entrar al Workstation"):
                if email_login and pass_login:
                    exito, res = db.verificar_login(email_login, pass_login)
                    if exito:
                        st.session_state["usuario"] = res
                        st.success(f"¡Bienvenido/a, {res['nombre']}!")
                        st.rerun()
                    else:
                        st.error(res)
                else:
                    st.warning("Por favor completa correo y contraseña.")

    with tab_registro:
        col_r1, col_r2 = st.columns([1, 1])
        with col_r1:
            nombre_reg = st.text_input("Nombre Completo o Título Prof.:", key="reg_nom")
            email_reg = st.text_input("Correo Electrónico:", key="reg_email")
            pass_reg = st.text_input("Crear Contraseña:", type="password", key="reg_pass")
            if st.button("✨ Crear mi Cuenta"):
                if nombre_reg and email_reg and pass_reg:
                    exito, msg = db.registrar_usuario(nombre_reg, email_reg, pass_reg)
                    if exito:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:
                    st.warning("Completa todos los campos para registrarte.")
    
    st.stop()

# =========================================================
# USUARIO LOGUEADO - BARRA LATERAL (SIDEBAR)
# =========================================================
usuario_actual = st.session_state["usuario"]

with st.sidebar:
    st.markdown(f"### 👤 Usuario: **{usuario_actual['nombre']}**")
    plan_tag = "⭐ PREMIUM" if usuario_actual['plan'] == 'premium' else "🌱 PLAN FREE"
    st.markdown(f"**Plan Actual:** `{plan_tag}`")
    
    if st.button("🚪 Cerrar Sesión"):
        st.session_state["usuario"] = None
        st.rerun()
        
    st.divider()
    st.markdown("### ⚙️ Configuración API")
    
    api_key_secret = st.secrets.get("GROQ_API_KEY", "")
    if api_key_secret:
        api_key = api_key_secret
        st.success("Sistema Conectado", icon="⚡")
    else:
        api_key = st.text_input("🔑 Groq API Key:", type="password", help="Ingresa tu clave de API de Groq")
        if api_key:
            st.success("API Key Conectada", icon="✅")
        else:
            st.warning("Ingrese su API Key para comenzar", icon="⚠️")

# =========================================================
# PESTAÑAS PRINCIPALES DE LA APLICACIÓN
# =========================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab_historial = st.tabs([
    "📋 Analizador Clínico", 
    "🧪 Buscador de Pruebas", 
    "📄 Generador de Informes", 
    "🎙️ Analizador de Sesiones", 
    "📚 Psicoeducación",
    "🧮 Corrector Psicométrico",
    "🗂️ Mi Historial"
])

# ---------------------------------------------------------
# TAB 1: ANALIZADOR CLÍNICO INICIAL
# ---------------------------------------------------------
with tab1:
    st.subheader("📋 Análisis Diagnóstico Inicial y Multiaxial")
    
    col_edad1, col_edad2 = st.columns(2)
    with col_edad1:
        edad_paciente = st.number_input("🎂 Edad del Paciente (años):", min_value=1, max_value=110, value=25, step=1)
    with col_edad2:
        etapa_default = "Adulto"
        if edad_paciente < 12: etapa_default = "Infantil (Niño/a)"
        elif edad_paciente < 18: etapa_default = "Adolescente"
        elif edad_paciente >= 65: etapa_default = "Adulto Mayor"
            
        opciones_etapa = ["Infantil (Niño/a)", "Adolescente", "Adulto", "Adulto Mayor"]
        etapa_paciente = st.selectbox("👶/👵 Etapa de Desarrollo:", opciones_etapa, index=opciones_etapa.index(etapa_default))

    st.markdown("#### 🎙️ Dictar o Escribir la Narrativa Clínica")
    audio_dictado = st.audio_input("Presiona para dictar las notas de voz del caso:")
    
    if audio_dictado is not None:
        if not api_key:
            st.error("Por favor ingresa tu API Key en la barra lateral.")
        else:
            with st.spinner("Transcribiendo dictado por voz..."):
                texto_dictado = engine.transcribir_audio_groq(audio_dictado, api_key)
                if "Error" not in texto_dictado:
                    st.session_state["narrativa_texto"] = (st.session_state["narrativa_texto"] + "\n" + texto_dictado).strip()
                    st.success("¡Voz transcrita e integrada correctamente!")

    narrativa = st.text_area("Narrativa o notas de la consulta inicial:", value=st.session_state["narrativa_texto"], height=160)
    st.session_state["narrativa_texto"] = narrativa

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Analizar Caso y Brechas"):
            if not api_key: st.error("Ingresa tu API Key.")
            elif not narrativa.strip(): st.warning("Ingresa una narrativa.")
            else:
                with st.spinner("Procesando hipótesis clínicas..."):
                    res = engine.analizar_caso_inicial(narrativa, api_key)
                    st.markdown(res)
                    db.guardar_historial(usuario_actual["id"], "Análisis Inicial", f"Caso Edad {edad_paciente}", res)
                    st.toast("💾 Análisis guardado en tu historial")
                    
    with col2:
        if st.button("🧪 Sugerir Batería Psicométrica"):
            if not api_key: st.error("Ingresa tu API Key.")
            elif not narrativa.strip(): st.warning("Ingresa una narrativa.")
            else:
                with st.spinner("Sugeriendo batería..."):
                    res = engine.obtener_pruebas_psicometricas(narrativa, edad_paciente, etapa_paciente, api_key)
                    st.markdown(res)
                    db.guardar_historial(usuario_actual["id"], "Sugerencia Pruebas", f"Batería para {edad_paciente} años", res)

# ---------------------------------------------------------
# TAB 2: BUSCADOR DE PRUEBAS
# ---------------------------------------------------------
with tab2:
    st.subheader("🧪 Buscador de Pruebas y Recursos Psicométricos")
    query_prueba = st.text_input("Nombre de la prueba o área a evaluar:", placeholder="Ej: WISC-V, BDI-II, RAVEN...")
    if st.button("🔎 Buscar Recursos"):
        if not api_key: st.error("Ingresa tu API Key.")
        elif not query_prueba.strip(): st.warning("Escribe una búsqueda.")
        else:
            with st.spinner("Consultando..."):
                res = engine.buscar_recursos_pruebas(query_prueba, api_key)
                st.markdown(res)

# ---------------------------------------------------------
# TAB 3: GENERADOR DE INFORMES
# ---------------------------------------------------------
with tab3:
    st.subheader("📄 Generador de Informes y Exportación a Word")
    archivo_plantilla = st.file_uploader("📂 Subir Plantilla de Informe en Word (.docx):", type=["docx"])
    plantilla_extraida = engine.extraer_texto_docx(archivo_plantilla) if archivo_plantilla else ""

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
        if not api_key: st.error("Ingresa tu API Key.")
        else:
            datos_dict = {"nombre": nombre, "edad": edad, "genero": genero, "ocupacion": ocupacion, "motivo": motivo, "problema_actual": problema_actual, "pruebas_aplicadas": pruebas_aplicadas, "observaciones": observaciones, "diagnostico": diagnostico}
            with st.spinner("Redactando informe..."):
                res = engine.generar_informe_premium(datos_dict, enfoque, plantilla_extraida, api_key)
                st.markdown(res)
                db.guardar_historial(usuario_actual["id"], "Informe Psicológico", f"Informe: {nombre or 'Paciente'}", res)
                
                doc_bytes = engine.crear_documento_word(f"Informe - {nombre or 'Paciente'}", res)
                st.download_button(label="📥 Descargar Informe en Word (.docx)", data=doc_bytes, file_name=f"Informe_{nombre or 'Paciente'}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# ---------------------------------------------------------
# TAB 4: ANALIZADOR DE SESIONES
# ---------------------------------------------------------
with tab4:
    st.subheader("🎙️ Analizador de Sesiones Grabadas")
    archivo_audio = st.file_uploader("Sube el audio de la sesión (MP3, WAV, M4A):", type=["mp3", "wav", "m4a"])
    if archivo_audio and st.button("🎙️ Transcribir y Analizar Sesión"):
        if not api_key: st.error("Ingresa tu API Key.")
        else:
            with st.spinner("Transcribiendo..."):
                transcripcion = engine.transcribir_audio_groq(archivo_audio, api_key)
            if "Error" not in transcripcion:
                with st.spinner("Analizando..."):
                    analisis = engine.analizar_transcripcion_sesion(transcripcion, api_key)
                    st.markdown(analisis)
                    db.guardar_historial(usuario_actual["id"], "Análisis Sesión Audio", f"Sesión: {archivo_audio.name}", analisis)

# ---------------------------------------------------------
# TAB 5: PSICOEDUCACIÓN
# ---------------------------------------------------------
with tab5:
    st.subheader("📚 Generador de Material Psicoeducativo")
    diag_base = st.text_area("Diagnóstico o tema a explicar:", placeholder="Ej: Trastorno de Ansiedad Generalizada...")
    destinatario = st.selectbox("Destinatario de la guía:", ["Paciente (Adulto)", "Padres / Familiares", "Paciente (Adolescente)", "Docentes / Colegio"])
    if st.button("📖 Generar Guía Psicoeducativa"):
        if not api_key: st.error("Ingresa tu API Key.")
        elif not diag_base.strip(): st.warning("Ingresa un tema.")
        else:
            with st.spinner("Elaborando guía..."):
                res = engine.generar_plantilla_psicoeducacion(diag_base, destinatario, api_key)
                st.markdown(res)
                db.guardar_historial(usuario_actual["id"], "Psicoeducación", f"Guía: {diag_base[:30]}", res)

# ---------------------------------------------------------
# TAB 6: CORRECTOR PSICOMÉTRICO
# ---------------------------------------------------------
with tab6:
    st.subheader("🧮 Corrector e Interpretador de Puntajes Psicométricos")
    prueba_nom = st.text_input("Nombre de la Prueba:", placeholder="Ej: WISC-V...")
    puntajes_input = st.text_area("Ingresa los puntajes:", height=100)
    if st.button("📊 Interpretar Puntajes"):
        if not api_key: st.error("Ingresa tu API Key.")
        elif not prueba_nom.strip() or not puntajes_input.strip(): st.warning("Completa los datos.")
        else:
            with st.spinner("Interpretar puntajes..."):
                res = engine.interpretar_puntajes_psicometricos(prueba_nom, puntajes_input, edad_paciente, api_key)
                st.markdown(res)
                db.guardar_historial(usuario_actual["id"], "Corrección Psicométrica", f"Prueba: {prueba_nom}", res)

# ---------------------------------------------------------
# TAB 7: HISTORIAL DEL USUARIO
# ---------------------------------------------------------
with tab_historial:
    st.subheader(f"🗂️ Historial Clínico de {usuario_actual['nombre']}")
    st.caption("Aquí se guardan automáticamente las consultas, informes y análisis que generes en la plataforma.")
    
    registros = db.obtener_historial_usuario(usuario_actual["id"])
    
    if not registros:
        st.info("Aún no tienes análisis o informes guardados en tu historial.")
    else:
        for reg_id, tipo, titulo, contenido, fecha in registros:
            with st.expander(f"📌 [{tipo}] {titulo} — 🗓️ {fecha}"):
                st.markdown(contenido)
                doc_bytes = engine.crear_documento_word(titulo, contenido)
                st.download_button(
                    label="📥 Descargar en Word (.docx)",
                    data=doc_bytes,
                    file_name=f"{titulo.replace(' ', '_')}.docx",
                    key=f"hist_dl_{reg_id}"
                )
