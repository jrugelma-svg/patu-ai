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
    generar_plan_tratamiento_psicologico,
    generar_hoja_trabajo_paciente,
    procesar_comando_agente_patu
)

st.set_page_config(
    page_title="PATU AI - Workstation v4.0 PRO",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(135deg, #F4EEFB 0%, #E9DEFA 100%) !important; 
        color: #3E2F56 !important; 
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    section[data-testid="stSidebar"] { 
        background: rgba(235, 224, 252, 0.95) !important; 
        border-right: 2px solid #D8C7F0 !important; 
    }
    
    h1, h2, h3, h4, label, p, span, div { color: #3E2F56 !important; }
    h1, h2, h3 { color: #6C3CB5 !important; font-weight: 800 !important; }
    
    .header-banner {
        background: linear-gradient(120deg, #7C42D1 0%, #8A93FF 50%, #FF85B8 100%);
        padding: 22px 30px;
        border-radius: 20px;
        color: white !important;
        box-shadow: 0 8px 22px rgba(124, 66, 209, 0.2);
        margin-bottom: 20px;
    }
    .header-banner h1, .header-banner p { color: white !important; margin: 0; }
    
    .ficha-paciente-card {
        background: #EFE6FA !important;
        border: 2px solid #D1BFF0 !important;
        border-radius: 16px !important;
        padding: 16px 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 12px rgba(108, 60, 181, 0.08) !important;
    }
    
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

    .resultado-ia { 
        background-color: #FFFFFF !important; 
        padding: 26px !important; 
        border-radius: 18px !important; 
        border: 2px solid #D1BFF0 !important; 
        border-left: 8px solid #7C42D1 !important; 
        margin-top: 15px !important; 
        box-shadow: 0px 6px 20px rgba(108, 60, 181, 0.1) !important; 
    }

    .patu-holograma-box {
        background: linear-gradient(145deg, #FFFFFF 0%, #F3ECFA 100%) !important;
        border: 3px solid #7C42D1 !important;
        border-radius: 24px !important;
        padding: 20px !important;
        text-align: center !important;
        box-shadow: 0 0 25px rgba(124, 66, 209, 0.25) !important;
    }

    .cat-avatar-container {
        width: 140px;
        height: 120px;
        margin: 0 auto;
        position: relative;
        animation: floatPatuNeon 2.5s infinite ease-in-out;
    }

    .cat-head {
        width: 120px;
        height: 95px;
        background: #FFFFFF;
        border-radius: 50% 50% 45% 45%;
        position: absolute;
        bottom: 5px;
        left: 10px;
        border: 3px solid #7C42D1;
        box-shadow: 0 0 20px rgba(124, 66, 209, 0.4);
    }

    .cat-ear-left, .cat-ear-right {
        width: 0;
        height: 0;
        border-left: 18px solid transparent;
        border-right: 18px solid transparent;
        border-bottom: 35px solid #FFFFFF;
        position: absolute;
        top: -20px;
    }
    .cat-ear-left { left: 8px; transform: rotate(-15deg); }
    .cat-ear-right { right: 8px; transform: rotate(15deg); }

    .cat-eye-left, .cat-eye-right {
        width: 14px;
        height: 18px;
        background: #7C42D1;
        border-radius: 50%;
        position: absolute;
        top: 32px;
    }
    .cat-eye-left { left: 28px; }
    .cat-eye-right { right: 28px; }

    .cat-nose {
        width: 10px;
        height: 8px;
        background: #FF85B8;
        border-radius: 50%;
        position: absolute;
        top: 52px;
        left: 55px;
    }

    @keyframes floatPatuNeon {
        0%, 100% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-10px) scale(1.04); }
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

if "user" not in st.session_state: st.session_state.user = None
if "texto_narrativa" not in st.session_state: st.session_state.texto_narrativa = ""
if "historial_consultas" not in st.session_state: st.session_state.historial_consultas = []
if "caso_activo" not in st.session_state: st.session_state.caso_activo = False

if "patu_encendido" not in st.session_state: st.session_state.patu_encendido = True
if "primera_interaccion_patu" not in st.session_state: st.session_state.primera_interaccion_patu = True

if "paciente_nombre" not in st.session_state: st.session_state.paciente_nombre = "Paciente Anónimo"
if "paciente_edad" not in st.session_state: st.session_state.paciente_edad = "--"
if "paciente_etapa" not in st.session_state: st.session_state.paciente_etapa = "--"
if "paciente_riesgo" not in st.session_state: st.session_state.paciente_riesgo = "Bajo"
if "paciente_avance" not in st.session_state: st.session_state.paciente_avance = 15
if "paciente_semaforo" not in st.session_state: st.session_state.paciente_semaforo = "🟡 Evaluación / Encuadre"

for res_key in [
    "res_analizador_clinico", "res_buscador_pruebas", "res_generador_informes",
    "res_analizador_sesiones", "res_psicoeducacion", "res_corrector_psicometrico",
    "res_plan_tratamiento", "res_genograma", "res_coterapeuta", "res_compromiso_vida", "res_hoja_trabajo", "res_patu_live",
    "doc_informe_descargable", "doc_psico_descargable", "doc_plan_descargable", "doc_compromiso_descargable", "doc_hoja_descargable"
]:
    if res_key not in st.session_state: st.session_state[res_key] = None

def mostrar_logo(width=130):
    if os.path.exists("logo.jpg"): st.image("logo.jpg", width=width)
    else: st.markdown("<h2 style='margin:0;'>🐾 <b>PATU AI</b></h2>", unsafe_allow_html=True)

def guardar_en_historial(modulo, entrada, resultado):
    st.session_state.historial_consultas.append({"modulo": modulo, "entrada": entrada, "resultado": resultado})
    if st.session_state.user: guardar_consulta(st.session_state.user["id"], modulo, entrada, resultado)

def limpiar_caso_actual():
    st.session_state.caso_activo = False
    st.session_state.paciente_nombre = "Paciente Anónimo"
    st.session_state.paciente_edad = "--"
    st.session_state.paciente_etapa = "--"
    st.session_state.paciente_riesgo = "Bajo"
    st.session_state.paciente_avance = 15
    st.session_state.paciente_semaforo = "🟡 Evaluación / Encuadre"
    for res_key in [
        "res_analizador_clinico", "res_buscador_pruebas", "res_generador_informes",
        "res_analizador_sesiones", "res_psicoeducacion", "res_corrector_psicometrico",
        "res_plan_tratamiento", "res_genograma", "res_coterapeuta", "res_compromiso_vida", "res_hoja_trabajo", "res_patu_live",
        "doc_informe_descargable", "doc_psico_descargable", "doc_plan_descargable", "doc_compromiso_descargable", "doc_hoja_descargable"
    ]: st.session_state[res_key] = None
    st.session_state.texto_narrativa = ""

# LOGIN Y REGISTRO
if not st.session_state.user:
    col_logo, col_header = st.columns([1, 4])
    with col_logo: mostrar_logo(width=130)
    with col_header:
        st.markdown('''<div class="header-banner"><h1>PATU AI <span class="badge-pro">v4.0 PRO</span></h1><p>Gestión de Proyectos — Grupo 2 (Viernes) | Docente: Richard Edgar González</p></div>''', unsafe_allow_html=True)

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
                    st.rerun()
                else: st.error(msg)
    elif opcion == "Registrarse":
        st.subheader("📝 Crear nueva cuenta")
        nombre = st.text_input("Nombre Completo")
        email = st.text_input("Correo Electrónico")
        password = st.text_input("Contraseña", type="password")
        if st.button("✨ Registrarse"):
            if nombre and email and password:
                exito, msg = registrar_usuario(nombre, email, password)
                if exito: st.success(msg)
                else: st.error(msg)

# PANEL PRINCIPAL FULL
else:
    api_key_env = os.getenv("GROQ_API_KEY")
    user = obtener_usuario_por_id(st.session_state.user["id"])
    if user: st.session_state.user = user
    user = st.session_state.user

    col_a, col_b = st.columns([1, 5])
    with col_a: mostrar_logo(width=110)
    with col_b:
        st.markdown('''<div class="header-banner"><h1>PATU AI <span class="badge-pro">v4.0 PRO</span></h1><p>Desarrollado por <b>Yordán Rugel Martínez & Grupo 2 (Gestión de Proyectos)</b> | Docente: <b>Richard Edgar González</b></p></div>''', unsafe_allow_html=True)

    if st.session_state.caso_activo:
        color_riesgo = "#2ECC71" if st.session_state.paciente_riesgo == "Bajo" else "#F1C40F" if st.session_state.paciente_riesgo == "Medio" else "#E74C3C"
        st.markdown(f'''<div class="ficha-paciente-card"><div style="display:flex; justify-content:space-around; text-align:center; align-items:center;">
        <div><small style="color:#6C3CB5; font-weight:bold;">PACIENTE ACTIVO</small><br><b>{st.session_state.paciente_nombre}</b></div>
        <div><small style="color:#6C3CB5; font-weight:bold;">EDAD / ETAPA</small><br><b>{st.session_state.paciente_edad} años ({st.session_state.paciente_etapa})</b></div>
        <div><small style="color:#6C3CB5; font-weight:bold;">RIESGO INICIAL</small><br><b style="color:{color_riesgo};">{st.session_state.paciente_riesgo}</b></div>
        <div><small style="color:#6C3CB5; font-weight:bold;">SEMÁFORO TERAPÉUTICO</small><br><b>{st.session_state.paciente_semaforo}</b></div>
        </div></div>''', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"👤 **Usuario:** `{user.get('nombre', 'Usuario')}`")
        st.markdown("🌟 **Modo:** `AGENTE AUTÓNOMO`")
        if st.session_state.caso_activo:
            if st.button("🔄 Reiniciar / Nuevo Paciente"):
                limpiar_caso_actual()
                st.rerun()
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    fase_seleccionada = st.radio(
        "📌 **Selecciona la Fase de Trabajo Clínico:**",
        [
            "🐾 PATU LIVE (Agente de Voz Autónomo)",
            "🔬 FASE 1: Evaluación e Historial Familiar",
            "🎯 FASE 2: Intervención, Hojas de Trabajo y Co-Terapia",
            "📄 FASE 3: Redactor de Informes y Psicoeducación",
            "📂 Mi Historial en Nube"
        ],
        horizontal=True
    )
    st.write("---")

    # MODO PATU LIVE
    if "PATU LIVE" in fase_seleccionada:
        st.subheader("🐾 Habla en Vivo con PATU (Agente de Voz Autónomo)")
        st.caption("Pídele a PATU ejecutar tareas, responder al público o dile: 'Muestra tu poder'.")

        col_avatar, col_interaccion = st.columns([1, 2])

        with col_avatar:
            st.markdown('<div class="patu-holograma-box">', unsafe_allow_html=True)
            st.markdown("""<div class="cat-avatar-container"><div class="cat-head"><div class="cat-ear-left"></div><div class="cat-ear-right"></div><div class="cat-eye-left"></div><div class="cat-eye-right"></div><div class="cat-nose"></div></div></div>""", unsafe_allow_html=True)
            estado_txt = "🟢 EN ESCUCHA ACTIVA" if st.session_state.patu_encendido else "🔴 EN ESPERA"
            st.markdown(f"<h3 style='margin-top:10px; color:#7C42D1;'><b>PATU AI</b></h3><small><b>{estado_txt}</b></small>", unsafe_allow_html=True)
            if not st.session_state.patu_encendido:
                if st.button("🟢 Reencender PATU"):
                    st.session_state.patu_encendido = True
                    st.session_state.primera_interaccion_patu = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col_interaccion:
            st.markdown("### 🎙️ Micrófono de Control Autónomo")
            if st.session_state.patu_encendido:
                audio_comando = st.audio_input("Presiona el micrófono y habla con PATU:", key="mic_agente_patu")

                if audio_comando is not None:
                    audio_bytes_cmd = audio_comando.getvalue()
                    if st.session_state.get("last_agent_audio") != audio_bytes_cmd:
                        with st.spinner("🐱 PATU escuchando y procesando..."):
                            comando_texto = transcribir_audio_groq(audio_comando, api_key_env)
                            if comando_texto and not str(comando_texto).startswith("Error"):
                                st.session_state["last_agent_audio"] = audio_bytes_cmd
                                contexto_paciente = f"Paciente: {st.session_state.paciente_nombre}, Edad: {st.session_state.paciente_edad}"
                                respuesta_patu = procesar_comando_agente_patu(str(comando_texto), contexto_paciente, st.session_state.primera_interaccion_patu, api_key_env)
                                st.session_state.primera_interaccion_patu = False
                                
                                if "[ACCION:APAGAR]" in respuesta_patu:
                                    st.session_state.patu_encendido = False

                                st.session_state.res_patu_live = {"pregunta": str(comando_texto), "respuesta": respuesta_patu}
                                guardar_en_historial("PATU Agente Voz", str(comando_texto), respuesta_patu)
                                st.rerun()

        if st.session_state.res_patu_live:
            st.markdown("---")
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(f"🗣️ **Tú / Público:** *\"{st.session_state.res_patu_live['pregunta']}\"*")
            
            resp_clean = st.session_state.res_patu_live['respuesta']
            
            if "[ACCION:APAGAR]" in resp_clean:
                st.warning("🔴 **PATU AI ha desactivado su modo de escucha activa por orden de voz.**")
                st.markdown(resp_clean.replace("[ACCION:APAGAR]", ""))
            elif "[ACCION:DESCARGAR]" in resp_clean:
                st.success("⚡ **Acción Ejecutada:** Generando documento...")
                doc_clean = resp_clean.replace("[ACCION:DESCARGAR]", "")
                st.download_button("📥 Descargar Archivo Word", data=crear_documento_word("Documento PATU AI", doc_clean), file_name="Documento_PATU.docx")
                st.markdown(doc_clean)
            else:
                st.markdown(f"🐾 **PATU AI responde:**")
                st.markdown(resp_clean)

            voz_clean = resp_clean.replace("[ACCION:APAGAR]", "").replace("[ACCION:DESCARGAR]", "").replace('*', '').replace('#', '')
            js_code = f"""
                <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{voz_clean[:250]}");
                msg.lang = 'es-ES';
                msg.rate = 1.0;
                msg.pitch = 1.1;
                window.speechSynthesis.speak(msg);
                </script>
            """
            st.components.v1.html(js_code, height=0)
            st.markdown('</div>', unsafe_allow_html=True)

    # FASE 1
    elif "FASE 1" in fase_seleccionada:
        st.subheader("🔬 Fase 1: Diagnóstico Multiaxial y Estructura Familiar")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1: btn_mod1 = st.button("📋 1. Analizador Clínico & Riesgo", use_container_width=True)
        with col_m2: btn_mod2 = st.button("🌳 2. Genograma Familiar", use_container_width=True)
        with col_m3: btn_mod3 = st.button("🧪 3. Buscador de Pruebas & Baremos", use_container_width=True)

        if "sub_f1_active" not in st.session_state: st.session_state.sub_f1_active = "analizador"
        if btn_mod1: st.session_state.sub_f1_active = "analizador"
        elif btn_mod2: st.session_state.sub_f1_active = "genograma"
        elif btn_mod3: st.session_state.sub_f1_active = "pruebas"

        if st.session_state.sub_f1_active == "analizador":
            c_p1, c_p2, c_p3 = st.columns([2, 1, 1])
            with c_p1: nombre_input = st.text_input("👤 Paciente / Iniciales:", value=st.session_state.paciente_nombre if st.session_state.paciente_nombre != "Paciente Anónimo" else "Paciente J.P.", key="ac_nombre")
            with c_p2: edad = st.number_input("🎂 Edad (años):", min_value=1, max_value=120, value=25, key="ac_edad")
            with c_p3: etapa = st.selectbox("👶 / 🧑 Etapa:", ["Infantil", "Adolescente", "Adulto", "Adulto Mayor"], key="ac_etapa")

            instrucciones = st.text_area("✍️ Narrativa del Motivo de Consulta y Sintomatología:", value=st.session_state.texto_narrativa, placeholder="Escribe o dicta el motivo de consulta...", key="txt_ac")
            st.session_state.texto_narrativa = instrucciones

            if st.button("🚀 Procesar Análisis Clínico Completo", key="btn_ac"):
                if instrucciones.strip():
                    with st.spinner("Procesando caso clínico..."):
                        narrativa_final = f"Paciente: {nombre_input}, {edad} años ({etapa}). Motivo: {instrucciones}"
                        res = analizar_caso_inicial(narrativa_final, api_key_env)
                        st.session_state.res_analizador_clinico = res
                        st.session_state.paciente_nombre = nombre_input
                        st.session_state.paciente_edad = edad
                        st.session_state.paciente_etapa = etapa
                        st.session_state.caso_activo = True
                        guardar_en_historial("Analizador Clínico", narrativa_final, res)
                        st.rerun()

            if st.session_state.res_analizador_clinico:
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_analizador_clinico)
                st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.sub_f1_active == "genograma":
            texto_familia = st.text_area("Describe la estructura y antecedentes familiares:", key="gf_texto")
            if st.button("🌳 Estructurar Genograma Familiar", key="btn_genograma"):
                if texto_familia.strip():
                    res_geno = generar_genograma_familiar(texto_familia, api_key_env)
                    st.session_state.res_genograma = res_geno
                    guardar_en_historial("Genograma Familiar", texto_familia, res_geno)
                    st.rerun()

            if st.session_state.res_genograma:
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_genograma)
                st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.sub_f1_active == "pruebas":
            caso_bp = st.text_area("Sintomatología a evaluar:", key="bp_caso")
            if st.button("🔎 Filtrar Pruebas Normadas", key="btn_bp"):
                if caso_bp.strip():
                    res = obtener_pruebas_psicometricas(caso_bp, st.session_state.paciente_edad if st.session_state.paciente_edad != "--" else 25, st.session_state.paciente_etapa if st.session_state.paciente_etapa != "--" else "Adulto", api_key_env)
                    st.session_state.res_buscador_pruebas = res
                    st.rerun()

            if st.session_state.res_buscador_pruebas:
                st.markdown(st.session_state.res_buscador_pruebas)

    # FASE 2
    elif "FASE 2" in fase_seleccionada:
        st.subheader("🎯 Fase 2: Plan Terapéutico, Hojas de Trabajo y Co-Terapia")
        col_f2_1, col_f2_2, col_f2_3 = st.columns(3)
        with col_f2_1: btn_f2_mod1 = st.button("🎯 Plan de Tratamiento", use_container_width=True)
        with col_f2_2: btn_f2_mod2 = st.button("📝 Hojas de Trabajo", use_container_width=True)
        with col_f2_3: btn_f2_mod3 = st.button("💬 Co-Terapeuta IA", use_container_width=True)

        if "sub_f2_active" not in st.session_state: st.session_state.sub_f2_active = "plan"
        if btn_f2_mod1: st.session_state.sub_f2_active = "plan"
        elif btn_f2_mod2: st.session_state.sub_f2_active = "hojas"
        elif btn_f2_mod3: st.session_state.sub_f2_active = "coterapeuta"

        if st.session_state.sub_f2_active == "plan":
            diag_plan = st.text_input("Diagnóstico / Problema Blanco:", value=st.session_state.paciente_nombre if st.session_state.paciente_nombre != "Paciente Anónimo" else "", key="pt_diag")
            if st.button("🚀 Crear Plan de Tratamiento", key="btn_plan"):
                if diag_plan.strip():
                    res_plan = generar_plan_tratamiento_psicologico(diag_plan, "Cognitivo-Conductual", 12, api_key_env)
                    st.session_state.res_plan_tratamiento = res_plan
                    st.session_state.doc_plan_descargable = crear_documento_word(f"Plan - {st.session_state.paciente_nombre}", res_plan)
                    guardar_en_historial("Plan de Tratamiento", diag_plan, res_plan)
                    st.rerun()

            if st.session_state.res_plan_tratamiento:
                st.download_button("📥 Descargar Plan (.docx)", data=st.session_state.doc_plan_descargable, file_name=f"Plan_{st.session_state.paciente_nombre}.docx", key="dl_plan")
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_plan_tratamiento)
                st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.sub_f2_active == "hojas":
            tipo_hoja = st.selectbox("Selecciona Autorregistro:", ["Registro TCC de Pensamientos Automáticos", "Diario Terapéutico de Ansiedad"], key="ht_tipo")
            meta_hoja = st.text_input("Meta del Paciente:", key="ht_meta")

            if st.button("📝 Generar Hoja de Trabajo", key="btn_hoja"):
                if meta_hoja.strip():
                    res_hoja = generar_hoja_trabajo_paciente(tipo_hoja, meta_hoja, api_key_env)
                    st.session_state.res_hoja_trabajo = res_hoja
                    st.session_state.doc_hoja_descargable = crear_documento_word(f"Hoja - {tipo_hoja}", res_hoja)
                    guardar_en_historial("Hoja de Trabajo", meta_hoja, res_hoja)
                    st.rerun()

            if st.session_state.res_hoja_trabajo:
                st.download_button("📥 Descargar Hoja (.docx)", data=st.session_state.doc_hoja_descargable, file_name=f"Hoja_{st.session_state.paciente_nombre}.docx", key="dl_hoja")
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_hoja_trabajo)
                st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.sub_f2_active == "coterapeuta":
            consulta_sup = st.text_area("Consulta técnica:", key="txt_sup")
            if st.button("💬 Consultar Co-Terapeuta", key="btn_coterapeuta"):
                if consulta_sup.strip():
                    res_sup = generar_supervision_coterapeuta(st.session_state.paciente_nombre, consulta_sup, api_key_env)
                    st.session_state.res_coterapeuta = res_sup
                    guardar_en_historial("Co-Terapeuta", consulta_sup, res_sup)
                    st.rerun()

            if st.session_state.res_coterapeuta:
                st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
                st.markdown(st.session_state.res_coterapeuta)
                st.markdown('</div>', unsafe_allow_html=True)

    # FASE 3
    elif "FASE 3" in fase_seleccionada:
        st.subheader("📄 Fase 3: Redactor de Informes Oficiales y Psicoeducación")
        nombre_p = st.text_input("Paciente / Iniciales:", value=st.session_state.paciente_nombre, key="inf_nom")
        motivo_p = st.text_area("Motivo de Consulta:", key="inf_motivo")

        if st.button("📄 Generar Informe Oficial", key="btn_inf"):
            if motivo_p.strip():
                datos_dict = {"nombre": nombre_p, "motivo": motivo_p}
                res_inf = generar_informe_premium(datos_dict, "Clínico", "", api_key_env)
                st.session_state.res_generador_informes = res_inf
                st.session_state.doc_informe_descargable = crear_documento_word(f"Informe - {nombre_p}", res_inf)
                guardar_en_historial("Informe Clínico", nombre_p, res_inf)
                st.rerun()

        if st.session_state.res_generador_informes:
            st.download_button("📥 Descargar Informe (.docx)", data=st.session_state.doc_informe_descargable, file_name=f"Informe_{nombre_p}.docx", key="dl_inf")
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_generador_informes)
            st.markdown('</div>', unsafe_allow_html=True)

    # MI HISTORIAL EN NUBE
    elif "Mi Historial" in fase_seleccionada:
        st.subheader("📂 Registro Histórico de Consultas")
        historial_bd = obtener_historial_usuario(user["id"], limite=100)
        if historial_bd:
            for item in historial_bd:
                fecha = item.get("creado_en", "")
                with st.expander(f"📌 [{item['modulo']}] - {fecha[:16].replace('T', ' ')}"):
                    st.write("**Entrada:**")
                    st.info(item["entrada"])
                    st.write("**Resultado:**")
                    st.markdown(item["resultado"])
        else:
            st.info("Aún no tienes consultas registradas en tu historial.")
