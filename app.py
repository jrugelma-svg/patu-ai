import streamlit as st
import os
import io
import docx
from database import (
    registrar_usuario,
    verificar_login,
    obtener_usuario_por_id,
    incrementar_consultas,
    recargar_creditos_usuario,
    crear_preferencia_pago,
    guardar_consulta,
    obtener_historial_usuario,
    borrar_historial_usuario
)
from engine import (
    analizar_caso_inicial,
    obtener_pruebas_psicometricas,
    generar_informe_premium,
    analizar_transcripcion_sesion,
    generar_plantilla_psicoeducacion,
    interpretar_puntajes_psicometricos,
    transcribir_audio_groq,
    crear_documento_word,
    extraer_texto_docx,
    procesar_analisis,
    evaluar_nivel_riesgo_automatico
)

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="PATU AI - Workstation Clínico PRO",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS CSS AVANZADOS (UI/UX v4.0 HARMONY GLASSMORPHISM)
# ==========================================
st.markdown("""
    <style>
    /* 1. Fondo general con degradado pastel continuo */
    .stApp { 
        background: linear-gradient(135deg, #F8F5FB 0%, #EFE8FA 50%, #E6DEF7 100%) !important; 
        color: #4A3E5D !important; 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* 2. Barra lateral estilo Glassmorphism */
    section[data-testid="stSidebar"] { 
        background: rgba(240, 235, 252, 0.8) !important; 
        backdrop-filter: blur(14px) !important;
        border-right: 1px solid rgba(224, 211, 245, 0.7) !important; 
    }
    
    /* 3. Personalización de Scrollbar armónico */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #F8F5FB;
    }
    ::-webkit-scrollbar-thumb {
        background: #C4B5FD;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #8259BF;
    }

    /* 4. Tipografía y Títulos Armónicos */
    h1, h2, h3, h4, label, p, span, div { 
        color: #4A3E5D !important; 
    }
    h1, h2, h3 {
        color: #794BB6 !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* 5. Banner de Encabezado Principal */
    .header-banner {
        background: linear-gradient(120deg, #8259BF 0%, #8B93FF 50%, #FF94C2 100%);
        padding: 24px 32px;
        border-radius: 20px;
        color: white !important;
        box-shadow: 0 10px 25px rgba(130, 89, 191, 0.2);
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-banner h1, .header-banner p {
        color: white !important;
        margin: 0;
    }
    
    /* 6. Indicador de pulso verde en vivo */
    .status-pulse {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: #2ECC71;
        box-shadow: 0 0 0 rgba(46, 204, 113, 0.4);
        animation: pulse 2s infinite;
        margin-right: 6px;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
        100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
    }
    
    /* 7. Ficha Resumen del Paciente Activo */
    .ficha-paciente {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(224, 211, 245, 0.9);
        border-radius: 16px;
        padding: 16px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(130, 89, 191, 0.06);
        display: flex;
        justify-content: space-around;
        align-items: center;
    }
    .ficha-item {
        text-align: center;
    }
    .ficha-item small {
        color: #8259BF;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.75rem;
    }
    .ficha-item div {
        font-size: 1.1rem;
        font-weight: 700;
        color: #4A3E5D;
    }

    /* 8. Botones en Gradiente Pastel con Efecto Elevación */
    div.stButton > button { 
        background: linear-gradient(135deg, #8B93FF 0%, #794BB6 100%) !important; 
        color: #FFFFFF !important; 
        border-radius: 12px !important; 
        border: none !important; 
        font-weight: 700 !important; 
        padding: 10px 24px !important;
        box-shadow: 0 4px 14px rgba(139, 147, 255, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #FF94C2 0%, #8B93FF 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 148, 194, 0.4) !important;
    }
    
    /* 9. Entradas de Texto y Selectores */
    .stTextInput input, .stTextArea textarea, .stSelectbox select { 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        color: #4A3E5D !important; 
        border: 1.5px solid #E0D3F5 !important; 
        border-radius: 12px !important; 
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #8B93FF !important;
        box-shadow: 0 0 0 3px rgba(139, 147, 255, 0.2) !important;
    }

    /* 10. Pestañas en Estilo Píldora Reorganizadas */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        color: #5C4A72 !important;
        padding: 10px 18px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    button[aria-selected="true"] {
        background-color: #8259BF !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(130, 89, 191, 0.25) !important;
    }

    /* 11. Tarjeta de Resultado con Borde Acentuado */
    .resultado-ia { 
        background-color: #FFFFFF !important; 
        padding: 28px !important; 
        border-radius: 18px !important; 
        border: 1px solid #E0D3F5 !important; 
        border-left: 6px solid #8259BF !important; 
        margin-top: 20px !important; 
        box-shadow: 0px 8px 24px rgba(130, 89, 191, 0.08) !important; 
    }
    .badge-pro { 
        background: rgba(255, 255, 255, 0.25); 
        color: #FFFFFF !important; 
        padding: 4px 14px; 
        border-radius: 20px; 
        font-size: 0.8rem; 
        font-weight: 700; 
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ESTADOS DE SESIÓN Y DATOS DEL PACIENTE
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None
if "texto_narrativa" not in st.session_state:
    st.session_state.texto_narrativa = ""
if "historial_consultas" not in st.session_state:
    st.session_state.historial_consultas = []
if "caso_activo" not in st.session_state:
    st.session_state.caso_activo = False

# Datos dinámicos para el Dashboard del Paciente
if "paciente_nombre" not in st.session_state:
    st.session_state.paciente_nombre = "Paciente Anónimo"
if "paciente_edad" not in st.session_state:
    st.session_state.paciente_edad = "--"
if "paciente_etapa" not in st.session_state:
    st.session_state.paciente_etapa = "--"
if "paciente_riesgo" not in st.session_state:
    st.session_state.paciente_riesgo = "Bajo"

# Resultados Persistentes
for res_key in [
    "res_analizador_clinico", "res_buscador_pruebas", "res_generador_informes",
    "res_analizador_sesiones", "res_psicoeducacion", "res_corrector_psicometrico",
    "res_plan_tratamiento", "doc_informe_descargable", "doc_psico_descargable", "doc_plan_descargable"
]:
    if res_key not in st.session_state:
        st.session_state[res_key] = None

# Recarga Mercado Pago
query_params = st.query_params
if query_params.get("pago") == "exitoso":
    user_id_pago = query_params.get("user_id")
    if user_id_pago:
        exito_recarga = recargar_creditos_usuario(user_id_pago, creditos_a_sumar=10)
        if exito_recarga:
            st.success("🎉 ¡Pago confirmado! Se han añadido +10 créditos a tu cuenta.")
            if st.session_state.user and str(st.session_state.user["id"]) == str(user_id_pago):
                st.session_state.user = obtener_usuario_por_id(user_id_pago)
        st.query_params.clear()

def mostrar_logo(width=140):
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=width)
    else:
        st.markdown("<h2 style='margin:0;'>🐾 <b>PATU AI</b></h2>", unsafe_allow_html=True)

def guardar_en_historial(modulo, entrada, resultado):
    st.session_state.historial_consultas.append({
        "modulo": modulo,
        "entrada": entrada,
        "resultado": resultado
    })
    if st.session_state.user:
        guardar_consulta(st.session_state.user["id"], modulo, entrada, resultado)

def limpiar_caso_actual():
    st.session_state.caso_activo = False
    st.session_state.paciente_nombre = "Paciente Anónimo"
    st.session_state.paciente_edad = "--"
    st.session_state.paciente_etapa = "--"
    st.session_state.paciente_riesgo = "Bajo"
    for res_key in [
        "res_analizador_clinico", "res_buscador_pruebas", "res_generador_informes",
        "res_analizador_sesiones", "res_psicoeducacion", "res_corrector_psicometrico",
        "res_plan_tratamiento", "doc_informe_descargable", "doc_psico_descargable", "doc_plan_descargable"
    ]:
        st.session_state[res_key] = None
    st.session_state.texto_narrativa = ""

# ==========================================
# LOGIN Y REGISTRO
# ==========================================
if not st.session_state.user:
    col_logo, col_header = st.columns([1, 4])
    with col_logo:
        mostrar_logo(width=130)
    with col_header:
        st.markdown('''
            <div class="header-banner">
                <div>
                    <h1>PATU AI <span class="badge-pro">v4.0 PRO</span></h1>
                    <p>Psychologists United Across America — Workstation Clínico Intuitivo</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)

    opcion = st.sidebar.radio("Navegación", ["Iniciar Sesión", "Registrarse"])

    if opcion == "Iniciar Sesión":
        st.subheader("🔑 Acceso al Workstation")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar Sesión"):
            if email and password:
                exito, usuario, msg = verificar_login(email, password)
                if exito:
                    st.session_state.user = usuario
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Por favor ingresa tu correo y contraseña.")

    elif opcion == "Registrarse":
        st.subheader("📝 Crear nueva cuenta")
        nombre = st.text_input("Nombre Completo")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")

        if st.button("Registrarse"):
            if nombre and email and password:
                exito, msg = registrar_usuario(nombre, email, password)
                if exito:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Por favor completa todos los campos.")

# ==========================================
# PANEL PRINCIPAL LOGUEADO
# ==========================================
else:
    api_key_env = os.getenv("GROQ_API_KEY")
    user = obtener_usuario_por_id(st.session_state.user["id"])
    if user:
        st.session_state.user = user

    user = st.session_state.user
    limite_gratis = 4
    consultas_usadas = user.get("consultas_usadas", 0)
    es_premium = user.get("es_premium", False)
    puede_consultar = es_premium or (consultas_usadas < limite_gratis) or st.session_state.caso_activo

    # BANNER SUPERIOR
    col_a, col_b = st.columns([1, 5])
    with col_a:
        mostrar_logo(width=120)
    with col_b:
        st.markdown(f'''
            <div class="header-banner">
                <div>
                    <h1>PATU AI <span class="badge-pro">v4.0 PRO</span></h1>
                    <p>Bienvenido, <b>{user.get('nombre', 'Doctor(a)')}</b> — Asistente Diagnóstico</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)

    # DASHBOARD INTERACTIVO DEL PACIENTE ACTIVO
    if st.session_state.caso_activo:
        color_riesgo = "#2ECC71" if st.session_state.paciente_riesgo == "Bajo" else "#F1C40F" if st.session_state.paciente_riesgo == "Medio" else "#E74C3C"
        st.markdown(f'''
            <div class="ficha-paciente">
                <div class="ficha-item">
                    <small>Estado</small>
                    <div><span class="status-pulse"></span>Activo</div>
                </div>
                <div class="ficha-item">
                    <small>Paciente</small>
                    <div>{st.session_state.paciente_nombre}</div>
                </div>
                <div class="ficha-item">
                    <small>Edad / Etapa</small>
                    <div>{st.session_state.paciente_edad} años ({st.session_state.paciente_etapa})</div>
                </div>
                <div class="ficha-item">
                    <small>Riesgo Detectado</small>
                    <div style="color: {color_riesgo};">{st.session_state.paciente_riesgo}</div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

    # BARRA LATERAL
    with st.sidebar:
        st.markdown(f"👤 **Usuario:** `{user.get('nombre', 'Usuario')}`")
        if es_premium:
            st.markdown("🌟 **Plan:** `PREMIUM UNLIMITED`")
        else:
            st.markdown("🌱 **Plan:** `FREE TRIAL`")
            st.markdown("---")
            restantes = max(0, limite_gratis - consultas_usadas)
            st.write(f"📊 **Créditos disponibles:** {restantes}/{limite_gratis}")
            st.progress(restantes / limite_gratis)

        if st.session_state.caso_activo:
            if st.button("🔄 Reiniciar Paciente"):
                limpiar_caso_actual()
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if not puede_consultar and not st.session_state.res_analizador_clinico:
        st.warning("⚠️ Has consumido tus créditos libres de evaluación.")
        link_pago, msg_pago = crear_preferencia_pago(user["id"], user["email"])
        if link_pago:
            st.link_button("🚀 Recargar +10 Créditos por S/. 2.00", link_pago)

    # PESTAÑAS
    tabs = st.tabs([
        "📋 Analizador Clínico", 
        "🧪 Buscador de Pruebas", 
        "🎯 Plan de Tratamiento", 
        "📄 Generador de Informes", 
        "🎙️ Analizador de Sesiones", 
        "📚 Psicoeducación", 
        "📝 Corrector Psicométrico", 
        "📂 Mi Historial"
    ])

    # ==========================================
    # 1. ANALIZADOR CLÍNICO
    # ==========================================
    with tabs[0]:
        st.subheader("📋 Diagnóstico Multiaxial, Brechas e Hipótesis")
        
        c_p1, c_p2, c_p3 = st.columns([2, 1, 1])
        with c_p1:
            nombre_input = st.text_input("👤 Nombre / Iniciales:", value=st.session_state.paciente_nombre if st.session_state.paciente_nombre != "Paciente Anónimo" else "Paciente J.P.", key="ac_nombre")
        with c_p2:
            edad = st.number_input("🎂 Edad (años):", min_value=1, max_value=120, value=25, key="ac_edad")
        with c_p3:
            etapa = st.selectbox("👶 / 🧑 Etapa:", ["Infantil", "Adolescente", "Adulto", "Adulto Mayor"], key="ac_etapa")

        st.write("---")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            archivo = st.file_uploader("📷 Cargar ficha o informe (.docx, .txt):", type=["docx", "txt"], key="uploader_ac")
        with col_f2:
            audio_input = st.audio_input("🎙️ Dictar nota de voz (Máx. 25 MB):", key="audio_voice_ac")

        if audio_input is not None:
            audio_bytes = audio_input.getvalue()
            if st.session_state.get("last_audio_bytes_ac") != audio_bytes:
                with st.spinner("🎙️ Transcribiendo audio con Whisper..."):
                    transcripcion = transcribir_audio_groq(audio_input, api_key_env)
                    if transcripcion and not str(transcripcion).startswith("Error"):
                        st.session_state.texto_narrativa = str(transcripcion).strip()
                        st.session_state["last_audio_bytes_ac"] = audio_bytes
                        st.success("✅ Transcripción cargada en la narrativa.")
                    else:
                        st.error(f"Error al transcribir: {transcripcion}")

        instrucciones = st.text_area(
            "✍️ Narrativa del Motivo de Consulta y Sintomatología:",
            value=st.session_state.texto_narrativa,
            placeholder="Escribe o dicta el motivo de consulta...",
            key="txt_ac"
        )
        st.session_state.texto_narrativa = instrucciones

        # EVALUACIÓN AUTOMÁTICA EN TIEMPO REAL
        riesgo_detectado = evaluar_nivel_riesgo_automatico(instrucciones)
        st.session_state.paciente_riesgo = riesgo_detectado

        if riesgo_detectado == "Alto":
            st.error("🚨 **Nivel de Riesgo Inicial Detectado AUTOMÁTICAMENTE: ALTO** — Se identificaron indicadores críticos de urgencia (ideación/intento suicida, violencia o autolesiones).")
        elif riesgo_detectado == "Medio":
            st.warning("⚠️ **Nivel de Riesgo Inicial Detectado AUTOMÁTICAMENTE: MEDIO** — Se identificó sintomatología moderada a severa (ansiedad, crisis de pánico o consumo).")
        else:
            st.info("🟢 **Nivel de Riesgo Inicial Detectado AUTOMÁTICAMENTE: BAJO** — Sin indicadores de emergencia en la narrativa.")

        if st.button("Procesar Análisis Clínico Completo", key="btn_ac"):
            if not puede_consultar:
                st.error("❌ Créditos agotados. Por favor realiza una recarga.")
            else:
                texto_a_procesar = instrucciones.strip()
                if not texto_a_procesar and audio_input is not None:
                    transcripcion = transcribir_audio_groq(audio_input, api_key_env)
                    if transcripcion and not str(transcripcion).startswith("Error"):
                        texto_a_procesar = str(transcripcion).strip()

                if archivo or texto_a_procesar:
                    with st.spinner("Procesando caso clínico..."):
                        narrativa_final = f"Paciente: {nombre_input}, {edad} años ({etapa}). Riesgo Detectado: {riesgo_detectado}. Motivo: {texto_a_procesar}"
                        
                        if archivo:
                            res = procesar_analisis(archivo, f"Paciente: {nombre_input}, {edad} años ({etapa}). Motivo: {texto_a_procesar}")
                        else:
                            res = analizar_caso_inicial(narrativa_final, api_key_env)
                        
                        if res and not res.startswith("❌"):
                            st.session_state.res_analizador_clinico = res
                            st.session_state.paciente_nombre = nombre_input
                            st.session_state.paciente_edad = edad
                            st.session_state.paciente_etapa = etapa
                            st.session_state.paciente_riesgo = riesgo_detectado
                            guardar_en_historial("Analizador Clínico", narrativa_final, res)
                            
                            if not st.session_state.caso_activo:
                                st.session_state.caso_activo = True
                                if not es_premium:
                                    nuevas = incrementar_consultas(user["id"])
                                    if nuevas is not None:
                                        st.session_state.user["consultas_usadas"] = nuevas
                            st.rerun()
                        else:
                            st.error(res)
                else:
                    st.warning("Por favor ingresa o dicta la narrativa del caso.")

        if st.session_state.res_analizador_clinico:
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_analizador_clinico)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 2. BUSCADOR DE PRUEBAS
    # ==========================================
    with tabs[1]:
        st.subheader("🧪 Batería Psicométrica Recomendada")
        c1, c2 = st.columns(2)
        with c1:
            edad_bp = st.number_input("Edad exacta:", min_value=1, max_value=120, value=st.session_state.paciente_edad if st.session_state.paciente_edad != "--" else 25, key="bp_edad")
        with c2:
            etapa_bp = st.selectbox("Etapa de desarrollo:", ["Infantil", "Adolescente", "Adulto", "Adulto Mayor"], key="bp_etapa")
        
        caso_bp = st.text_area("Sintomatología o variables a evaluar:", placeholder="Ej: Sintomatología depresiva, inatención, fobia social...", key="bp_caso")

        if st.button("Filtrar Batería Psicométrica", key="btn_bp"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Créditos agotados.")
            elif caso_bp.strip():
                with st.spinner("Seleccionando instrumentos normados por edad..."):
                    res = obtener_pruebas_psicometricas(caso_bp, edad_bp, etapa_bp, api_key_env)
                    if res and not res.startswith("❌"):
                        st.session_state.res_buscador_pruebas = res
                        guardar_en_historial("Buscador de Pruebas", f"Edad: {edad_bp}, Caso: {caso_bp}", res)
                        st.rerun()
                    else:
                        st.error(res)
            else:
                st.warning("Ingresa los síntomas a evaluar.")

        if st.session_state.res_buscador_pruebas:
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_buscador_pruebas)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 3. PLAN DE TRATAMIENTO
    # ==========================================
    with tabs[2]:
        st.subheader("🎯 Diseñador de Plan de Intervención y Objetivos Terapéuticos")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            enfoque_terapia = st.selectbox("Modelo / Enfoque Terapéutico:", ["Cognitivo-Conductual (TCC)", "Sistémico-Familiar", "Terapia de Aceptación y Compromiso (ACT)", "Humanista-Existencial"], key="pt_enfoque")
        with col_t2:
            num_sesiones = st.slider("Estimación de Sesiones del Plan:", 4, 24, 12, key="pt_sesiones")

        diag_plan = st.text_input("Diagnóstico o Problema Blanco:", value=st.session_state.paciente_nombre if st.session_state.paciente_nombre != "Paciente Anónimo" else "", placeholder="Ej: Trastorno de Ansiedad Generalizada", key="pt_diag")
        sintomas_plan = st.text_area("Síntomas principales y metas descritas por el paciente:", placeholder="Describe metas clínicas...", key="pt_sintomas")

        if st.button("Diseñar Plan de Tratamiento", key="btn_plan"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Créditos agotados.")
            elif diag_plan.strip() or sintomas_plan.strip():
                with st.spinner("Estructurando metas, fases y tareas para casa..."):
                    prompt_plan = f"Crea un plan de tratamiento psicológico de {num_sesiones} sesiones bajo el enfoque {enfoque_terapia} para el diagnóstico/caso: {diag_plan}. Síntomas y metas: {sintomas_plan}. Incluye: 1. Objetivos a corto, mediano y largo plazo. 2. Estructura por fases de intervención. 3. Técnicas recomendadas. 4. Tareas psicoeducativas o para la casa."
                    res_plan = analizar_caso_inicial(prompt_plan, api_key_env)
                    
                    if res_plan and not res_plan.startswith("❌"):
                        st.session_state.res_plan_tratamiento = res_plan
                        st.session_state.doc_plan_descargable = crear_documento_word(f"Plan de Tratamiento - {st.session_state.paciente_nombre}", res_plan)
                        guardar_en_historial("Plan de Tratamiento", f"Enfoque: {enfoque_terapia}, Caso: {diag_plan}", res_plan)
                        st.rerun()
                    else:
                        st.error(res_plan)
            else:
                st.warning("Completa el diagnóstico o metas clínicas.")

        if st.session_state.res_plan_tratamiento:
            if st.session_state.doc_plan_descargable:
                st.download_button(
                    label="📥 Descargar Plan de Tratamiento (.docx)",
                    data=st.session_state.doc_plan_descargable,
                    file_name=f"Plan_Tratamiento_{st.session_state.paciente_nombre}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="btn_dl_plan"
                )
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_plan_tratamiento)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 4. GENERADOR DE INFORMES
    # ==========================================
    with tabs[3]:
        st.subheader("📄 Redactor de Informes Clínicos")
        col_inf1, col_inf2 = st.columns(2)
        with col_inf1:
            nombre_p = st.text_input("Paciente / Iniciales:", value=st.session_state.paciente_nombre, key="inf_nom")
            edad_p = st.text_input("Edad:", value=str(st.session_state.paciente_edad), key="inf_edad")
            genero_p = st.text_input("Género:", value="Femenino", key="inf_gen")
            ocupacion_p = st.text_input("Ocupación:", value="Estudiante", key="inf_ocup")
        with col_inf2:
            enfoque_p = st.selectbox("Enfoque del Informe:", ["Clínico", "Educativo", "Neuropsicológico"], key="inf_enf")
            plantilla_docx = st.file_uploader("Sube tu modelo (.docx) [Opcional]:", type=["docx"], key="inf_plantilla")

        motivo_p = st.text_area("Motivo de Consulta:", key="inf_motivo")
        problema_p = st.text_area("Problema Actual y Antecedentes:", key="inf_prob")
        pruebas_p = st.text_area("Pruebas Aplicadas y Puntuaciones:", key="inf_pruebas")
        obs_p = st.text_area("Observaciones Conductuales:", key="inf_obs")
        diag_p = st.text_area("Diagnóstico / Conclusiones:", key="inf_diag")

        if st.button("Generar Informe Formal", key="btn_inf"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Créditos agotados.")
            elif motivo_p.strip() or problema_p.strip():
                with st.spinner("Redactando informe formal..."):
                    plantilla_texto = extraer_texto_docx(plantilla_docx) if plantilla_docx else ""
                    datos_dict = {
                        "nombre": nombre_p, "edad": edad_p, "genero": genero_p, "ocupacion": ocupacion_p,
                        "motivo": motivo_p, "problema_actual": problema_p, "pruebas_aplicadas": pruebas_p,
                        "observaciones": obs_p, "diagnostico": diag_p
                    }

                    res_informe = generar_informe_premium(datos_dict, enfoque_p, plantilla_texto, api_key_env)
                    if res_informe and not res_informe.startswith("❌"):
                        st.session_state.res_generador_informes = res_informe
                        st.session_state.doc_informe_descargable = crear_documento_word(f"Informe Psicológico - {nombre_p}", res_informe)
                        guardar_en_historial("Generador de Informes", f"Paciente: {nombre_p}", res_informe)
                        st.rerun()
                    else:
                        st.error(res_informe)
            else:
                st.warning("Completa al menos el motivo o problema actual.")

        if st.session_state.res_generador_informes:
            if st.session_state.doc_informe_descargable:
                st.download_button(
                    label="📥 Descargar Documento (.docx)",
                    data=st.session_state.doc_informe_descargable,
                    file_name=f"Informe_{st.session_state.inf_nom}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="btn_dl_inf"
                )
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_generador_informes)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 5. ANALIZADOR DE SESIONES
    # ==========================================
    with tabs[4]:
        st.subheader("🎙️ Análisis de Transcripciones y Sesiones")
        archivo_sesion = st.file_uploader("Audio de la sesión (Máximo 25 MB):", type=["mp3", "wav", "m4a"], key="uploader_sesion")
        texto_sesion = st.text_area("O pega la transcripción escrita de la sesión:", key="txt_sesion")

        if st.button("Analizar Sesión", key="btn_sesion"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Créditos agotados.")
            else:
                transcripcion_final = texto_sesion.strip()
                if archivo_sesion and not transcripcion_final:
                    with st.spinner("Transcribiendo archivo con Whisper..."):
                        transcripcion_final = transcribir_audio_groq(archivo_sesion, api_key_env)

                if transcripcion_final and not str(transcripcion_final).startswith("Error"):
                    with st.spinner("Analizando dinámicas y afecto..."):
                        res = analizar_transcripcion_sesion(transcripcion_final, api_key_env)
                        if res and not res.startswith("❌"):
                            st.session_state.res_analizador_sesiones = res
                            guardar_en_historial("Analizador de Sesiones", "Análisis Terapéutico", res)
                            st.rerun()
                        else:
                            st.error(res)
                else:
                    st.warning("Ingresa o sube una transcripción válida.")

        if st.session_state.res_analizador_sesiones:
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_analizador_sesiones)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 6. PSICOEDUCACIÓN
    # ==========================================
    with tabs[5]:
        st.subheader("📚 Guías y Folletos Psicoeducativos")
        diag_base = st.text_input("Condición o Diagnóstico:", placeholder="Ej: TDAH, Trastorno de Ansiedad...", key="psico_diag")
        destinatario = st.selectbox("Destinatario del Material:", ["Paciente", "Familiares / Cuidadores", "Docentes / Colegio"], key="psico_dest")

        if st.button("Generar Guía", key="btn_psico"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Créditos agotados.")
            elif diag_base.strip():
                with st.spinner("Redactando material accesible..."):
                    res = generar_plantilla_psicoeducacion(diag_base, destinatario, api_key_env)
                    if res and not res.startswith("❌"):
                        st.session_state.res_psicoeducacion = res
                        st.session_state.doc_psico_descargable = crear_documento_word(f"Guía Psicoeducativa - {diag_base}", res)
                        guardar_en_historial("Psicoeducación", f"{diag_base} -> {destinatario}", res)
                        st.rerun()
                    else:
                        st.error(res)
            else:
                st.warning("Ingresa el diagnóstico base.")

        if st.session_state.res_psicoeducacion:
            if st.session_state.doc_psico_descargable:
                st.download_button(
                    label="📥 Descargar Guía (.docx)",
                    data=st.session_state.doc_psico_descargable,
                    file_name=f"Psicoeducacion_{st.session_state.psico_diag}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="btn_dl_psico"
                )
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_psicoeducacion)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 7. CORRECTOR PSICOMÉTRICO
    # ==========================================
    with tabs[6]:
        st.subheader("📝 Interpretación e Integración de Baremos")
        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            nombre_prueba = st.text_input("Prueba aplicada:", placeholder="Ej: WAIS-IV, BDI-II, MCHAT...", key="cp_nombre")
        with col_cp2:
            edad_cp = st.number_input("Edad del evaluado:", min_value=1, max_value=120, value=25, key="cp_edad")
        puntajes_texto = st.text_area("Puntuaciones y Percentiles directos:", key="cp_puntajes")

        if st.button("Interpretar Baremos", key="btn_cp"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Créditos agotados.")
            elif nombre_prueba.strip() and puntajes_texto.strip():
                with st.spinner("Analizando rangos normativos..."):
                    res = interpretar_puntajes_psicometricos(nombre_prueba, puntajes_texto, edad_cp, api_key_env)
                    if res and not res.startswith("❌"):
                        st.session_state.res_corrector_psicometrico = res
                        guardar_en_historial("Corrector Psicométrico", f"{nombre_prueba} - {puntajes_texto}", res)
                        st.rerun()
                    else:
                        st.error(res)
            else:
                st.warning("Completa el nombre de la prueba y sus puntuaciones.")

        if st.session_state.res_corrector_psicometrico:
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_corrector_psicometrico)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 8. MI HISTORIAL
    # ==========================================
    with tabs[7]:
        st.subheader("📂 Registro Histórico de Consultas")
        historial_bd = obtener_historial_usuario(user["id"], limite=100)

        if historial_bd:
            col_h1, col_h2 = st.columns([3, 1])
            with col_h1:
                st.caption(f"Mostrando {len(historial_bd)} registros guardados en la nube.")
            with col_h2:
                if st.button("🗑️ Borrar Historial", key="btn_borrar_historial"):
                    st.session_state["confirmar_borrado"] = True

            if st.session_state.get("confirmar_borrado"):
                st.warning("¿Seguro que deseas eliminar tu historial completo?")
                c_conf1, c_conf2 = st.columns(2)
                with c_conf1:
                    if st.button("✅ Confirmar", key="btn_confirmar_borrado"):
                        borrar_historial_usuario(user["id"])
                        st.session_state.historial_consultas = []
                        st.session_state["confirmar_borrado"] = False
                        st.rerun()
                with c_conf2:
                    if st.button("❌ Cancelar", key="btn_cancelar_borrado"):
                        st.session_state["confirmar_borrado"] = False
                        st.rerun()

            for item in historial_bd:
                fecha = item.get("creado_en", "")
                with st.expander(f"📌 [{item['modulo']}] - {fecha[:16].replace('T', ' ')}"):
                    st.write("**Entrada de consulta:**")
                    st.info(item["entrada"])
                    st.write("**Resultado:**")
                    st.markdown(item["resultado"])
        else:
            st.info("Aún no tienes consultas registradas en tu historial.")
