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
    evaluar_nivel_riesgo_automatico,
    generar_genograma_familiar,
    generar_supervision_coterapeuta,
    generar_compromiso_vida,
    generar_plan_tratamiento_psicologico
)

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="PATU AI - Workstation Clínico v4.0 PRO",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS CSS REVOLUCIONARIOS (DESPEJADO Y PASTELES CON CONTRASTE)
# ==========================================
st.markdown("""
    <style>
    /* Fondo general malva pastel continuo */
    .stApp { 
        background: linear-gradient(135deg, #F5EFFB 0%, #EAE0F7 100%) !important; 
        color: #43335A !important; 
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    /* Barra lateral estilo Glassmorphism */
    section[data-testid="stSidebar"] { 
        background: rgba(235, 224, 250, 0.9) !important; 
        border-right: 2px solid #D8C7F0 !important; 
    }
    
    /* Tipografía y Encabezados */
    h1, h2, h3, h4, label, p, span, div { color: #43335A !important; }
    h1, h2, h3 { color: #6C3CB5 !important; font-weight: 800 !important; }
    
    /* Banner Principal de Bienvenida */
    .header-banner {
        background: linear-gradient(120deg, #7C42D1 0%, #8A93FF 50%, #FF85B8 100%);
        padding: 20px 28px;
        border-radius: 20px;
        color: white !important;
        box-shadow: 0 8px 20px rgba(124, 66, 209, 0.2);
        margin-bottom: 20px;
    }
    .header-banner h1, .header-banner p { color: white !important; margin: 0; }
    
    /* Tarjeta Ficha del Paciente (Color Pastel con Contraste) */
    .ficha-paciente-card {
        background: #EFE6FA !important;
        border: 2px solid #D1BFF0 !important;
        border-radius: 16px !important;
        padding: 16px 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 12px rgba(108, 60, 181, 0.08) !important;
    }
    
    /* Cajas de Insumos / Tarjetas Internas */
    .caja-paso {
        background: #FFFFFF !important;
        border: 1.5px solid #D8C7F0 !important;
        border-radius: 14px !important;
        padding: 18px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
    }

    /* Botones Pastel Vibrantes */
    div.stButton > button { 
        background: linear-gradient(135deg, #8A93FF 0%, #7C42D1 100%) !important; 
        color: #FFFFFF !important; 
        border-radius: 12px !important; 
        border: none !important; 
        font-weight: 700 !important; 
        padding: 12px 28px !important;
        box-shadow: 0 4px 14px rgba(138, 147, 255, 0.35) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #FF85B8 0%, #8A93FF 100%) !important;
        transform: translateY(-2px);
    }
    
    /* Contenedor de Resultados con Borde Destacado */
    .resultado-ia { 
        background-color: #FFFFFF !important; 
        padding: 26px !important; 
        border-radius: 18px !important; 
        border: 2px solid #D1BFF0 !important; 
        border-left: 8px solid #7C42D1 !important; 
        margin-top: 15px !important; 
        box-shadow: 0px 6px 20px rgba(108, 60, 181, 0.1) !important; 
    }
    
    .badge-pro { 
        background: rgba(255, 255, 255, 0.3); 
        color: #FFFFFF !important; 
        padding: 4px 14px; 
        border-radius: 20px; 
        font-size: 0.8rem; 
        font-weight: 700; 
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

# Datos dinámicos del Paciente
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
    "res_plan_tratamiento", "res_genograma", "res_coterapeuta", "res_compromiso_vida",
    "doc_informe_descargable", "doc_psico_descargable", "doc_plan_descargable", "doc_compromiso_descargable"
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

def mostrar_logo(width=130):
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=width)
    else:
        st.markdown("<h2 style='margin:0;'>🐾 <b>PATU AI</b></h2>", unsafe_allow_html=True)

def guardar_en_historial(modulo, entrada, resultado):
    st.session_state.historial_consultas.append({"modulo": modulo, "entrada": entrada, "resultado": resultado})
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
        "res_plan_tratamiento", "res_genograma", "res_coterapeuta", "res_compromiso_vida",
        "doc_informe_descargable", "doc_psico_descargable", "doc_plan_descargable", "doc_compromiso_descargable"
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
                    <p>Psychologists United Across America — Asistente Clínico Inteligente</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)

    opcion = st.sidebar.radio("Navegación", ["Iniciar Sesión", "Registrarse"])

    if opcion == "Iniciar Sesión":
        st.subheader("🔑 Acceso al Workstation")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")

        if st.button("🚀 Iniciar Sesión"):
            if email and password:
                exito, usuario, msg = verificar_login(email, password)
                if exito:
                    st.session_state.user = usuario
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    elif opcion == "Registrarse":
        st.subheader("📝 Crear nueva cuenta")
        nombre = st.text_input("Nombre Completo")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")

        if st.button("✨ Registrarse"):
            if nombre and email and password:
                exito, msg = registrar_usuario(nombre, email, password)
                if exito:
                    st.success(msg)
                else:
                    st.error(msg)

# ==========================================
# PANEL PRINCIPAL DESPEJADO Y DESPLEGABLE
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
        mostrar_logo(width=110)
    with col_b:
        st.markdown(f'''
            <div class="header-banner">
                <div>
                    <h1>PATU AI <span class="badge-pro">v4.0 PRO</span></h1>
                    <p>Bienvenido, <b>{user.get('nombre', 'Doctor(a)')}</b> — Workstation Despejado e Intuitivo</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)

    # FICHA EN VIVO DEL PACIENTE ACTIVO
    if st.session_state.caso_activo:
        color_riesgo = "#2ECC71" if st.session_state.paciente_riesgo == "Bajo" else "#F1C40F" if st.session_state.paciente_riesgo == "Medio" else "#E74C3C"
        st.markdown(f'''
            <div class="ficha-paciente-card">
                <div style="display:flex; justify-content:space-around; text-align:center;">
                    <div><small style="color:#6C3CB5; font-weight:bold;">PACIENTE ACTIVO</small><br><b>{st.session_state.paciente_nombre}</b></div>
                    <div><small style="color:#6C3CB5; font-weight:bold;">EDAD / ETAPA</small><br><b>{st.session_state.paciente_edad} años ({st.session_state.paciente_etapa})</b></div>
                    <div><small style="color:#6C3CB5; font-weight:bold;">RIESGO DETECTADO</small><br><b style="color:{color_riesgo};">{st.session_state.paciente_riesgo}</b></div>
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
            st.write(f"📊 **Créditos libres:** {restantes}/{limite_gratis}")
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

    # ==========================================
    # NAVEGACIÓN EN 3 FASES PRINCIPALES (SIN PESTAÑAS AMONTONADAS)
    # ==========================================
    fase_seleccionada = st.radio(
        "📌 **Selecciona la Fase de Trabajo Clínico:**",
        [
            "🔬 FASE 1: Evaluación e Historial Familiar",
            "🎯 FASE 2: Intervención, Sesiones y Co-Terapia",
            "📄 FASE 3: Redactor de Informes y Psicoeducación",
            "📂 Mi Historial en Nube"
        ],
        horizontal=True
    )
    st.write("---")

    # ==========================================
    # FASE 1: EVALUACIÓN E HISTORIAL
    # ==========================================
    if "FASE 1" in fase_seleccionada:
        st.subheader("🔬 Fase 1: Diagnóstico Multiaxial y Estructura Familiar")
        
        modulo_f1 = st.selectbox("👉 Elige la herramienta de evaluación:", [
            "1. Analizador Clínico y Detección de Riesgo",
            "2. Genograma y Estructura Familiar (NUEVO)",
            "3. Buscador de Pruebas y Baremos"
        ])

        if "1. Analizador" in modulo_f1:
            st.markdown("<div class='caja-paso'><b>PASO 1: Datos Generales</b></div>", unsafe_allow_html=True)
            c_p1, c_p2, c_p3 = st.columns([2, 1, 1])
            with c_p1:
                nombre_input = st.text_input("👤 Paciente / Iniciales:", value=st.session_state.paciente_nombre if st.session_state.paciente_nombre != "Paciente Anónimo" else "Paciente J.P.", key="ac_nombre")
            with c_p2:
                edad = st.number_input("🎂 Edad (años):", min_value=1, max_value=120, value=25, key="ac_edad")
            with c_p3:
                etapa = st.selectbox("👶 / 🧑 Etapa:", ["Infantil", "Adolescente", "Adulto", "Adulto Mayor"], key="ac_etapa")

            st.markdown("<div class='caja-paso'><b>PASO 2: Insumos de la Consulta (Voz, Archivo o Texto)</b></div>", unsafe_allow_html=True)
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                archivo = st.file_uploader("📷 Cargar ficha o documento (.docx, .txt):", type=["docx", "txt"], key="uploader_ac")
            with col_f2:
                audio_input = st.audio_input("🎙️ Dictar nota de voz (Máx. 25 MB):", key="audio_voice_ac")

            if audio_input is not None:
                audio_bytes = audio_input.getvalue()
                if st.session_state.get("last_audio_bytes_ac") != audio_bytes:
                    with st.spinner("Transcribiendo audio..."):
                        transcripcion = transcribir_audio_groq(audio_input, api_key_env)
                        if transcripcion and not str(transcripcion).startswith("Error"):
                            st.session_state.texto_narrativa = str(transcripcion).strip()
                            st.session_state["last_audio_bytes_ac"] = audio_bytes
                            st.success("✅ Transcripción cargada.")

            instrucciones = st.text_area("✍️ Narrativa del Motivo de Consulta y Sintomatología:", value=st.session_state.texto_narrativa, placeholder="Escribe o dicta el motivo de consulta...", key="txt_ac")
            st.session_state.texto_narrativa = instrucciones

            # Detección Automática de Riesgo
            riesgo_detectado = evaluar_nivel_riesgo_automatico(instrucciones)
            st.session_state.paciente_riesgo = riesgo_detectado

            if riesgo_detectado == "Alto":
                st.error("🚨 **Nivel de Riesgo Detectado AUTOMÁTICAMENTE: ALTO** — Se identificaron indicadores críticos de urgencia (ideación/intento suicida o autolesiones).")
                if st.button("📄 Generar Contrato de Compromiso con la Vida (.docx)", key="btn_compromiso"):
                    res_comp = generar_compromiso_vida(nombre_input, api_key_env)
                    st.session_state.res_compromiso_vida = res_comp
                    st.session_state.doc_compromiso_descargable = crear_documento_word(f"Compromiso de Vida - {nombre_input}", res_comp)
                    st.rerun()

                if st.session_state.res_compromiso_vida:
                    st.download_button("📥 Descargar Compromiso con la Vida", data=st.session_state.doc_compromiso_descargable, file_name=f"Compromiso_Vida_{nombre_input}.docx", key="dl_comp")
                    st.markdown(st.session_state.res_compromiso_vida)

            elif riesgo_detectado == "Medio":
                st.warning("⚠️ **Nivel de Riesgo Detectado AUTOMÁTICAMENTE: MEDIO** — Sintomatología moderada.")
            else:
                st.info("🟢 **Nivel de Riesgo Detectado AUTOMÁTICAMENTE: BAJO** — Sin indicadores inmediatos de peligro.")

            if st.button("🚀 Procesar Análisis Clínico Completo", key="btn_ac"):
                if not puede_consultar:
                    st.error("❌ Créditos agotados.")
                else:
                    texto_a_procesar = instrucciones.strip()
                    if archivo or texto_a_procesar:
                        with st.spinner("Procesando caso clínico..."):
                            narrativa_final = f"Paciente: {nombre_input}, {edad} años ({etapa}). Riesgo: {riesgo_detectado}. Motivo: {texto_a_procesar}"
                            res = procesar_analisis(archivo, f"Paciente: {nombre_input}, {edad} años ({etapa}). Motivo: {texto_a_procesar}") if archivo else analizar_caso_inicial(narrativa_final, api_key_env)
                            
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

            if st.session_state.res_analizador_clinico:
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_analizador_clinico)
                st.markdown('</div>', unsafe_allow_html=True)

        elif "2. Genograma" in modulo_f1:
            st.markdown("#### 🧬 Generador de Genograma y Dinámica Familiar")
            texto_familia = st.text_area("Describe la estructura y relaciones familiares del paciente:", placeholder="Ej: Padre alcohólico (relación distante), madre con depresión, 2 hermanos mayores con alianzas...", key="gf_texto")
            if st.button("🧬 Estructurar Genograma Familiar", key="btn_genograma"):
                if texto_familia.strip():
                    with st.spinner("Analizando dinámica sistémica..."):
                        res_geno = generar_genograma_familiar(texto_familia, api_key_env)
                        st.session_state.res_genograma = res_geno
                        guardar_en_historial("Genograma Familiar", texto_familia, res_geno)
                        st.rerun()

            if st.session_state.res_genograma:
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_genograma)
                st.markdown('</div>', unsafe_allow_html=True)

        elif "3. Buscador" in modulo_f1:
            st.markdown("#### 🧪 Buscador y Corrector de Pruebas Psicométricas")
            tab_bp1, tab_bp2 = st.tabs(["🔎 Buscar Pruebas", "📝 Corrector de Baremos"])
            
            with tab_bp1:
                caso_bp = st.text_area("Sintomatología o variables a evaluar:", placeholder="Ej: Ansiedad social, inatención, rasgos obsesivos...", key="bp_caso")
                if st.button("🔎 Recomendar Pruebas", key="btn_bp"):
                    if caso_bp.strip():
                        res = obtener_pruebas_psicometricas(caso_bp, st.session_state.paciente_edad if st.session_state.paciente_edad != "--" else 25, st.session_state.paciente_etapa if st.session_state.paciente_etapa != "--" else "Adulto", api_key_env)
                        st.session_state.res_buscador_pruebas = res
                        st.rerun()

                if st.session_state.res_buscador_pruebas:
                    st.markdown(st.session_state.res_buscador_pruebas)

            with tab_bp2:
                nombre_prueba = st.text_input("Prueba aplicada:", placeholder="Ej: WAIS-IV, BDI-II...", key="cp_nombre")
                puntajes_texto = st.text_area("Puntuaciones y Percentiles directos:", key="cp_puntajes")
                if st.button("📊 Interpretar Baremos", key="btn_cp"):
                    if nombre_prueba.strip() and puntajes_texto.strip():
                        res = interpretar_puntajes_psicometricos(nombre_prueba, puntajes_texto, st.session_state.paciente_edad if st.session_state.paciente_edad != "--" else 25, api_key_env)
                        st.session_state.res_corrector_psicometrico = res
                        st.rerun()

                if st.session_state.res_corrector_psicometrico:
                    st.markdown(st.session_state.res_corrector_psicometrico)

    # ==========================================
    # FASE 2: INTERVENCIÓN Y SEGUIMIENTO
    # ==========================================
    elif "FASE 2" in fase_seleccionada:
        st.subheader("🎯 Fase 2: Plan Terapéutico, Análisis de Sesiones y Co-Terapia")
        modulo_f2 = st.selectbox("👉 Elige la herramienta de intervención:", [
            "1. Diseñador de Plan de Tratamiento",
            "2. Analizador de Transcripción de Sesiones",
            "3. Co-Terapeuta IA y Supervisión de Casos (NUEVO)"
        ])

        if "1. Diseñador" in modulo_f2:
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                enfoque_terapia = st.selectbox("Modelo Terapéutico:", ["Cognitivo-Conductual (TCC)", "Sistémico-Familiar", "Terapia de Aceptación y Compromiso (ACT)", "Humanista-Existencial"], key="pt_enfoque")
            with col_t2:
                num_sesiones = st.slider("Sesiones estimadas:", 4, 24, 12, key="pt_sesiones")

            diag_plan = st.text_input("Diagnóstico / Problema Blanco:", value=st.session_state.paciente_nombre if st.session_state.paciente_nombre != "Paciente Anónimo" else "", key="pt_diag")
            sintomas_plan = st.text_area("Síntomas y metas clínicas:", key="pt_sintomas")

            if st.button("🚀 Crear Plan de Tratamiento", key="btn_plan"):
                if diag_plan.strip() or sintomas_plan.strip():
                    prompt_plan = f"Crea un plan de tratamiento psicológico de {num_sesiones} sesiones bajo el enfoque {enfoque_terapia} para el caso: {diag_plan}. Síntomas: {sintomas_plan}."
                    res_plan = analizar_caso_inicial(prompt_plan, api_key_env)
                    st.session_state.res_plan_tratamiento = res_plan
                    st.session_state.doc_plan_descargable = crear_documento_word(f"Plan de Tratamiento - {st.session_state.paciente_nombre}", res_plan)
                    guardar_en_historial("Plan de Tratamiento", f"Enfoque: {enfoque_terapia}", res_plan)
                    st.rerun()

            if st.session_state.res_plan_tratamiento:
                st.download_button("📥 Descargar Plan (.docx)", data=st.session_state.doc_plan_descargable, file_name=f"Plan_{st.session_state.paciente_nombre}.docx", key="dl_plan")
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_plan_tratamiento)
                st.markdown('</div>', unsafe_allow_html=True)

        elif "2. Analizador" in modulo_f2:
            archivo_sesion = st.file_uploader("Audio de la sesión (Máx 25 MB):", type=["mp3", "wav", "m4a"], key="uploader_sesion")
            texto_sesion = st.text_area("O pega la transcripción escrita de la sesión:", key="txt_sesion")

            if st.button("🔍 Analizar Dinámica de la Sesión", key="btn_sesion"):
                transcripcion_final = texto_sesion.strip()
                if archivo_sesion and not transcripcion_final:
                    transcripcion_final = transcribir_audio_groq(archivo_sesion, api_key_env)

                if transcripcion_final and not str(transcripcion_final).startswith("Error"):
                    res = analizar_transcripcion_sesion(transcripcion_final, api_key_env)
                    st.session_state.res_analizador_sesiones = res
                    guardar_en_historial("Analizador de Sesiones", "Análisis de Sesión", res)
                    st.rerun()

            if st.session_state.res_analizador_sesiones:
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_analizador_sesiones)
                st.markdown('</div>', unsafe_allow_html=True)

        elif "3. Co-Terapeuta" in modulo_f2:
            st.markdown("#### 💬 Co-Terapeuta y Supervisión de Estrategias")
            consulta_supervisor = st.text_area("Escribe tu duda técnica o dilema sobre el manejo del paciente activo:", placeholder="Ej: Mi paciente se resiste a realizar los registros de pensamiento en TCC, ¿cómo abordo la alianza en la siguiente sesión?", key="txt_sup")
            if st.button("💬 Consultar con Co-Terapeuta IA", key="btn_coterapeuta"):
                if consulta_supervisor.strip():
                    with st.spinner("Consultando supervisor clínico..."):
                        res_sup = generar_supervision_coterapeuta(st.session_state.paciente_nombre, consulta_supervisor, api_key_env)
                        st.session_state.res_coterapeuta = res_sup
                        guardar_en_historial("Co-Terapeuta", consulta_supervisor, res_sup)
                        st.rerun()

            if st.session_state.res_coterapeuta:
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_coterapeuta)
                st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # FASE 3: DOCUMENTACIÓN Y REPORTES
    # ==========================================
    elif "FASE 3" in fase_seleccionada:
        st.subheader("📄 Fase 3: Redactor de Informes Oficiales y Psicoeducación")
        modulo_f3 = st.selectbox("👉 Elige la herramienta de documentación:", [
            "1. Redactor de Informes Clínicos",
            "2. Generador de Material Psicoeducativo"
        ])

        if "1. Redactor" in modulo_f3:
            col_inf1, col_inf2 = st.columns(2)
            with col_inf1:
                nombre_p = st.text_input("Paciente / Iniciales:", value=st.session_state.paciente_nombre, key="inf_nom")
                edad_p = st.text_input("Edad:", value=str(st.session_state.paciente_edad), key="inf_edad")
                genero_p = st.text_input("Género:", value="Femenino", key="inf_gen")
                ocupacion_p = st.text_input("Ocupación:", value="Estudiante", key="inf_ocup")
            with col_inf2:
                enfoque_p = st.selectbox("Enfoque del Informe:", ["Clínico", "Educativo", "Neuropsicológico"], key="inf_enf")
                plantilla_docx = st.file_uploader("Sube tu plantilla (.docx) [Opcional]:", type=["docx"], key="inf_plantilla")

            motivo_p = st.text_area("Motivo de Consulta:", key="inf_motivo")
            problema_p = st.text_area("Problema Actual:", key="inf_prob")
            pruebas_p = st.text_area("Pruebas Aplicadas:", key="inf_pruebas")
            obs_p = st.text_area("Observaciones Conductuales:", key="inf_obs")
            diag_p = st.text_area("Diagnóstico / Conclusiones:", key="inf_diag")

            if st.button("📄 Generar Informe Oficial", key="btn_inf"):
                if motivo_p.strip() or problema_p.strip():
                    plantilla_texto = extraer_texto_docx(plantilla_docx) if plantilla_docx else ""
                    datos_dict = {
                        "nombre": nombre_p, "edad": edad_p, "genero": genero_p, "ocupacion": ocupacion_p,
                        "motivo": motivo_p, "problema_actual": problema_p, "pruebas_aplicadas": pruebas_p,
                        "observaciones": obs_p, "diagnostico": diag_p
                    }

                    res_informe = generar_informe_premium(datos_dict, enfoque_p, plantilla_texto, api_key_env)
                    st.session_state.res_generador_informes = res_informe
                    st.session_state.doc_informe_descargable = crear_documento_word(f"Informe Psicológico - {nombre_p}", res_informe)
                    guardar_en_historial("Generador de Informes", f"Paciente: {nombre_p}", res_informe)
                    st.rerun()

            if st.session_state.res_generador_informes:
                st.download_button("📥 Descargar Informe en Word (.docx)", data=st.session_state.doc_informe_descargable, file_name=f"Informe_{st.session_state.inf_nom}.docx", key="dl_inf")
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_generador_informes)
                st.markdown('</div>', unsafe_allow_html=True)

        elif "2. Generador" in modulo_f3:
            diag_base = st.text_input("Diagnóstico o Condición:", placeholder="Ej: TDAH, Ansiedad Generalizada...", key="psico_diag")
            destinatario = st.selectbox("Destinatario del Material:", ["Paciente", "Familiares / Cuidadores", "Docentes / Colegio"], key="psico_dest")

            if st.button("📚 Generar Folleto Psicoeducativo", key="btn_psico"):
                if diag_base.strip():
                    res = generar_plantilla_psicoeducacion(diag_base, destinatario, api_key_env)
                    st.session_state.res_psicoeducacion = res
                    st.session_state.doc_psico_descargable = crear_documento_word(f"Guía Psicoeducativa - {diag_base}", res)
                    guardar_en_historial("Psicoeducación", f"{diag_base} -> {destinatario}", res)
                    st.rerun()

            if st.session_state.res_psicoeducacion:
                st.download_button("📥 Descargar Guía en Word (.docx)", data=st.session_state.doc_psico_descargable, file_name=f"Psicoeducacion_{st.session_state.psico_diag}.docx", key="dl_psico")
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_psicoeducacion)
                st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # MI HISTORIAL EN NUBE
    # ==========================================
    elif "Mi Historial" in fase_seleccionada:
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
