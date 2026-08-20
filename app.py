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
    procesar_analisis
)

# Configuración de la página
st.set_page_config(
    page_title="PATU AI - Workstation Clínico",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS con la paleta pastel inspirada en el logo de Patu AI
st.markdown("""
    <style>
    /* Fondo general suave crema-malva */
    .stApp { 
        background-color: #F8F5FB !important; 
        color: #5C4A72 !important; 
    }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] { 
        background-color: #F0EBFC !important; 
        border-right: 1px solid #E0D3F5 !important; 
    }
    
    /* Textos generales y etiquetas */
    h1, h2, h3, h4, label, p, span, div { 
        color: #5C4A72 !important; 
    }
    
    /* Títulos principales */
    h1, h2, h3 {
        color: #8259BF !important;
        font-weight: 700 !important;
    }
    
    /* Botones principales en Azul Lavanda */
    div.stButton > button { 
        background-color: #8B93FF !important; 
        color: #FFFFFF !important; 
        border-radius: 12px !important; 
        border: none !important; 
        font-weight: bold !important; 
        box-shadow: 0 4px 10px rgba(139, 147, 255, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    
    /* Efecto al pasar el cursor por los botones (Rosa Chicle) */
    div.stButton > button:hover {
        background-color: #FF94C2 !important;
        color: #FFFFFF !important;
    }
    
    /* Cajas de texto e insumos sobre blanco limpio */
    .stTextInput input, .stTextArea textarea, .stSelectbox select { 
        background-color: #FFFFFF !important; 
        color: #5C4A72 !important; 
        border: 1px solid #E0D3F5 !important; 
        border-radius: 10px !important; 
    }
    
    /* Badges y tarjetas destacadas */
    .badge-pro { 
        background-color: #8259BF; 
        color: #FFFFFF !important; 
        padding: 4px 12px; 
        border-radius: 12px; 
        font-size: 0.8rem; 
        font-weight: bold; 
        display: inline-block; 
    }
    
    .caja-pruebas { 
        background-color: #EFE8FA; 
        padding: 12px; 
        border-radius: 10px; 
        text-align: center; 
        font-weight: 500; 
        color: #5C4A72; 
        margin-top: 10px; 
        margin-bottom: 15px; 
        border: 1px solid #E0D3F5;
    }
    
    .resultado-ia { 
        background-color: #FFFFFF; 
        padding: 22px; 
        border-radius: 14px; 
        border: 1px solid #E0D3F5; 
        margin-top: 15px; 
        box-shadow: 0px 4px 12px rgba(130, 89, 191, 0.08); 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# ESTADOS DE SESIÓN (PERSISTENCIA Y CONTROL DE CASO)
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None

if "texto_narrativa" not in st.session_state:
    st.session_state.texto_narrativa = ""

if "historial_consultas" not in st.session_state:
    st.session_state.historial_consultas = []

# Control de Cobro por Caso Completo
if "caso_activo" not in st.session_state:
    st.session_state.caso_activo = False

# Resultados Persistentes
if "res_analizador_clinico" not in st.session_state:
    st.session_state.res_analizador_clinico = None
if "res_buscador_pruebas" not in st.session_state:
    st.session_state.res_buscador_pruebas = None
if "res_generador_informes" not in st.session_state:
    st.session_state.res_generador_informes = None
if "res_analizador_sesiones" not in st.session_state:
    st.session_state.res_analizador_sesiones = None
if "res_psicoeducacion" not in st.session_state:
    st.session_state.res_psicoeducacion = None
if "res_corrector_psicometrico" not in st.session_state:
    st.session_state.res_corrector_psicometrico = None
if "doc_informe_descargable" not in st.session_state:
    st.session_state.doc_informe_descargable = None
if "doc_psico_descargable" not in st.session_state:
    st.session_state.doc_psico_descargable = None

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

def mostrar_logo(width=160):
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=width)
    else:
        st.write("🐾 **PATU AI**")

def guardar_en_historial(modulo, entrada, resultado):
    # Se guarda en session_state para mostrarlo de inmediato en esta sesión...
    st.session_state.historial_consultas.append({
        "modulo": modulo,
        "entrada": entrada,
        "resultado": resultado
    })
    # ...y también en Supabase para que persista aunque el usuario cierre sesión.
    if st.session_state.user:
        guardar_consulta(st.session_state.user["id"], modulo, entrada, resultado)

def limpiar_caso_actual():
    """Resetea el caso actual para permitir ingresar un nuevo paciente."""
    st.session_state.caso_activo = False
    st.session_state.res_analizador_clinico = None
    st.session_state.res_buscador_pruebas = None
    st.session_state.res_generador_informes = None
    st.session_state.res_analizador_sesiones = None
    st.session_state.res_psicoeducacion = None
    st.session_state.res_corrector_psicometrico = None
    st.session_state.doc_informe_descargable = None
    st.session_state.doc_psico_descargable = None
    st.session_state.texto_narrativa = ""

# ==========================================
# LOGIN Y REGISTRO
# ==========================================
if not st.session_state.user:
    col_logo, col_header = st.columns([1, 4])
    with col_logo:
        mostrar_logo(width=140)
    with col_header:
        st.markdown('<h1>Workstation Clínico <span class="badge-pro">v3.0 PRO</span></h1>', unsafe_allow_html=True)
        st.write("**PATU AI** — Psychologists United Across America")

    opcion = st.sidebar.radio("Navegación", ["Iniciar Sesión", "Registrarse"])

    if opcion == "Iniciar Sesión":
        st.subheader("Accede a tu cuenta")
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
        st.subheader("Crea una nueva cuenta")
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

    # CABECERA
    col_a, col_b = st.columns([1, 4])
    with col_a:
        mostrar_logo(width=130)
    with col_b:
        st.markdown('<h1>Workstation Clínico <span class="badge-pro">v3.0 PRO</span></h1>', unsafe_allow_html=True)
        st.write("**PATU AI** — Psychologists United Across America")

    # BARRA LATERAL
    with st.sidebar:
        st.markdown(f"👤 **Usuario:** `{user.get('nombre', 'Usuario')}`")
        if es_premium:
            st.markdown("**Plan Actual:** 🌟 `PLAN PREMIUM`")
        else:
            st.markdown("**Plan Actual:** 🌱 `PLAN FREE`")
            st.markdown("---")
            st.write(f"📊 **Casos Utilizados:** {consultas_usadas}/{limite_gratis}")
            restantes = max(0, limite_gratis - consultas_usadas)
            st.markdown(f'<div class="caja-pruebas">Te quedan {restantes} casos/créditos disponibles.</div>', unsafe_allow_html=True)

        if st.session_state.caso_activo:
            st.success("🟢 Caso Clínico Activo (Herramientas desbloqueadas)")
            if st.button("🔄 Iniciar Nuevo Caso / Paciente"):
                limpiar_caso_actual()
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    if not puede_consultar and not st.session_state.res_analizador_clinico:
        st.warning(f"⚠️ Has agotado tus créditos disponibles.")
        st.info("Recarga 10 créditos adicionales por solo S/. 2.00 para continuar analizando nuevos casos.")
        link_pago, msg_pago = crear_preferencia_pago(user["id"], user["email"])
        if link_pago:
            st.link_button("🚀 Recargar +10 Créditos con Mercado Pago (S/. 2.00)", link_pago)

    tabs = st.tabs([
        "📋 Analizador Clínico", 
        "🧪 Buscador de Pruebas", 
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
        st.subheader("📋 Análisis Diagnóstico Inicial, Brechas, Hipótesis y Diagnósticos Diferenciales")
        col1, col2 = st.columns(2)
        with col1:
            edad = st.number_input("🎂 Edad del Paciente (años):", min_value=1, max_value=120, value=25, key="ac_edad")
        with col2:
            etapa = st.selectbox("👶 / 🧑 Etapa de Desarrollo:", ["Infantil", "Adolescente", "Adulto", "Adulto Mayor"], key="ac_etapa")

        st.write("---")
        st.write("📷 **1. Cargar Imágenes o Documentos del Motivo de Consulta:**")
        archivo = st.file_uploader(
            "Sube fotos de fichas, capturas, imágenes o PDFs:",
            type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
            key="uploader_ac"
        )

        st.write("🎙️ **2. Dictar Motivo de Consulta por Voz:**")
        audio_input = st.audio_input("Grabar notas de voz:", key="audio_voice_ac")

        if audio_input is not None:
            audio_bytes = audio_input.getvalue()
            if st.session_state.get("last_audio_bytes_ac") != audio_bytes:
                with st.spinner("🎙️ Transcribiendo nota de voz a texto..."):
                    transcripcion = transcribir_audio_groq(audio_input, api_key_env)
                    if transcripcion and not str(transcripcion).startswith("Error"):
                        st.session_state.texto_narrativa = str(transcripcion).strip()
                        st.session_state["last_audio_bytes_ac"] = audio_bytes
                        st.success("✅ ¡Voz transcrita exitosamente en el cuadro de texto!")
                    else:
                        st.error(f"Error al transcribir: {transcripcion}")

        instrucciones = st.text_area(
            "✍️ **3. Narrativa o Transcripción del Motivo de Consulta:**",
            value=st.session_state.texto_narrativa,
            placeholder="Pega o edita la narrativa aquí...",
            key="txt_ac"
        )
        st.session_state.texto_narrativa = instrucciones

        if st.button("Procesar Análisis Clínico Completo", key="btn_ac"):
            if not puede_consultar:
                st.error("❌ Has agotado tus créditos disponibles. Por favor recarga para iniciar un nuevo caso.")
            else:
                texto_a_procesar = instrucciones.strip()
                if not texto_a_procesar and audio_input is not None:
                    transcripcion = transcribir_audio_groq(audio_input, api_key_env)
                    if transcripcion and not str(transcripcion).startswith("Error"):
                        texto_a_procesar = str(transcripcion).strip()

                if archivo or texto_a_procesar:
                    with st.spinner("Generando diagnóstico multiaxial, brechas, diferenciales y batería de pruebas..."):
                        narrativa_final = f"Paciente de {edad} años ({etapa}). Motivo: {texto_a_procesar}"
                        
                        if archivo:
                            res = procesar_analisis(archivo, f"Edad del paciente: {edad} años ({etapa}). Motivo: {texto_a_procesar}")
                        else:
                            res = analizar_caso_inicial(narrativa_final, api_key_env)
                        
                        if res and not res.startswith("❌"):
                            st.session_state.res_analizador_clinico = res
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
                            st.session_state.res_analizador_clinico = None
                else:
                    st.warning("Por favor ingresa una narrativa, graba audio o sube un documento/imagen.")

        if st.session_state.res_analizador_clinico:
            st.markdown("---")
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_analizador_clinico)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 2. BUSCADOR DE PRUEBAS
    # ==========================================
    with tabs[1]:
        st.subheader("🧪 Buscador de Batería Psicométrica Estandarizada")
        c1, c2 = st.columns(2)
        with c1:
            edad_bp = st.number_input("Edad exacta del paciente:", min_value=1, max_value=120, value=25, key="bp_edad")
        with c2:
            etapa_bp = st.selectbox("Etapa de desarrollo:", ["Infantil", "Adolescente", "Adulto", "Adulto Mayor"], key="bp_etapa")
        
        caso_bp = st.text_area("Motivo de consulta o síntomas a evaluar:", placeholder="Ej: Sintomatología depresiva, inatención, ansiedad social...", key="bp_caso")

        if st.button("Buscar Pruebas Adecuadas", key="btn_bp"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Has agotado tus créditos. Recarga para continuar.")
            elif caso_bp.strip():
                with st.spinner("Filtrando pruebas psicométricas normadas por edad..."):
                    res = obtener_pruebas_psicometricas(caso_bp, edad_bp, etapa_bp, api_key_env)
                    if res and not res.startswith("❌"):
                        st.session_state.res_buscador_pruebas = res
                        guardar_en_historial("Buscador de Pruebas", f"Edad: {edad_bp}, Caso: {caso_bp}", res)
                        st.rerun()
                    else:
                        st.error(res)
                        st.session_state.res_buscador_pruebas = None
            else:
                st.warning("Ingresa los síntomas o el motivo para recomendar la batería.")

        if st.session_state.res_buscador_pruebas:
            st.markdown("---")
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_buscador_pruebas)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 3. GENERADOR DE INFORMES
    # ==========================================
    with tabs[2]:
        st.subheader("📄 Generador de Informes Psicológicos con Plantilla Personalizada")
        
        col_inf1, col_inf2 = st.columns(2)
        with col_inf1:
            nombre_p = st.text_input("Nombre / Iniciales del paciente:", value="J.P.", key="inf_nom")
            edad_p = st.text_input("Edad:", value="25 años", key="inf_edad")
            genero_p = st.text_input("Género:", value="Femenino", key="inf_gen")
            ocupacion_p = st.text_input("Ocupación:", value="Estudiante", key="inf_ocup")
        with col_inf2:
            enfoque_p = st.selectbox("Enfoque de redacción:", ["Clínico", "Educativo", "Neuropsicológico"], key="inf_enf")
            plantilla_docx = st.file_uploader("Sube tu modelo/plantilla de informe (.docx) [Opcional]:", type=["docx"], key="inf_plantilla")

        motivo_p = st.text_area("Motivo de Consulta:", placeholder="Detalla el motivo...", key="inf_motivo")
        problema_p = st.text_area("Problema Actual y Antecedentes:", placeholder="Evolución del problema...", key="inf_prob")
        pruebas_p = st.text_area("Pruebas Aplicadas y Resultados:", placeholder="Listado de pruebas y puntajes...", key="inf_pruebas")
        obs_p = st.text_area("Observaciones Conductuales:", placeholder="Conducta observada...", key="inf_obs")
        diag_p = st.text_area("Conclusiones y Diagnóstico:", placeholder="Diagnóstico e impresiones...", key="inf_diag")

        if st.button("Generar Informe Adaptado", key="btn_inf"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Has agotado tus créditos. Recarga para continuar.")
            elif motivo_p.strip() or problema_p.strip():
                with st.spinner("Redactando informe psicológico..."):
                    plantilla_texto = ""
                    if plantilla_docx:
                        plantilla_texto = extraer_texto_docx(plantilla_docx)

                    datos_dict = {
                        "nombre": nombre_p, "edad": edad_p, "genero": genero_p, "ocupacion": ocupacion_p,
                        "motivo": motivo_p, "problema_actual": problema_p, "pruebas_aplicadas": pruebas_p,
                        "observaciones": obs_p, "diagnostico": diag_p
                    }

                    res_informe = generar_informe_premium(datos_dict, enfoque_p, plantilla_texto, api_key_env)
                    
                    if res_informe and not res_informe.startswith("❌"):
                        st.session_state.res_generador_informes = res_informe
                        doc_bytes = crear_documento_word(f"Informe Psicológico - {nombre_p}", res_informe)
                        st.session_state.doc_informe_descargable = doc_bytes

                        guardar_en_historial("Generador de Informes", f"Paciente: {nombre_p}", res_informe)
                        st.rerun()
                    else:
                        st.error(res_informe)
                        st.session_state.res_generador_informes = None
                        st.session_state.doc_informe_descargable = None
            else:
                st.warning("Completa al menos el motivo de consulta o el problema actual.")

        if st.session_state.res_generador_informes:
            st.markdown("---")
            if st.session_state.doc_informe_descargable:
                st.download_button(
                    label="📥 Descargar Informe en Word (.docx)",
                    data=st.session_state.doc_informe_descargable,
                    file_name=f"Informe_{st.session_state.inf_nom}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="btn_dl_inf"
                )
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_generador_informes)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 4. ANALIZADOR DE SESIONES
    # ==========================================
    with tabs[3]:
        st.subheader("🎙️ Analizador de Sesiones Terapéuticas (Audio/Video o Texto)")
        archivo_sesion = st.file_uploader(
            "Sube la grabación de la sesión (Audio/Video hasta 500 MB):", 
            type=["mp3", "wav", "m4a", "mp4", "aac", "ogg"], key="uploader_sesion"
        )
        texto_sesion = st.text_area("O pega la transcripción/notas clínicas de la sesión:", placeholder="Transcripción de la sesión...", key="txt_sesion")

        if st.button("Procesar y Analizar Sesión", key="btn_sesion"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Has agotado tus créditos. Recarga para continuar.")
            else:
                transcripcion_final = texto_sesion.strip()
                if archivo_sesion and not transcripcion_final:
                    with st.spinner("Transcribiendo archivo de audio/video con Whisper..."):
                        transcripcion_final = transcribir_audio_groq(archivo_sesion, api_key_env)

                if transcripcion_final and not str(transcripcion_final).startswith("Error"):
                    with st.spinner("Analizando dinámica de la sesión, afecto y patrones..."):
                        res = analizar_transcripcion_sesion(transcripcion_final, api_key_env)
                        if res and not res.startswith("❌"):
                            st.session_state.res_analizador_sesiones = res
                            guardar_en_historial("Analizador de Sesiones", "Análisis de Sesión Terapéutica", res)
                            st.rerun()
                        else:
                            st.error(res)
                            st.session_state.res_analizador_sesiones = None
                else:
                    st.warning("Ingresa la transcripción o sube un archivo válido de audio/video.")

        if st.session_state.res_analizador_sesiones:
            st.markdown("---")
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_analizador_sesiones)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 5. PSICOEDUCACIÓN
    # ==========================================
    with tabs[4]:
        st.subheader("📚 Generador de Material Psicoeducativo")
        diag_base = st.text_input("Diagnóstico o Condición Base:", placeholder="Ej: Trastorno de Ansiedad Generalizada, TDAH...", key="psico_diag")
        destinatario = st.selectbox("Destinatario del Material:", ["Paciente", "Familiares / Cuidadores", "Institución Educativa / Docentes"], key="psico_dest")

        if st.button("Generar Guía Psicoeducativa", key="btn_psico"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Has agotado tus créditos. Recarga para continuar.")
            elif diag_base.strip():
                with st.spinner("Redactando folleto psicoeducativo..."):
                    res = generar_plantilla_psicoeducacion(diag_base, destinatario, api_key_env)
                    if res and not res.startswith("❌"):
                        st.session_state.res_psicoeducacion = res
                        doc_bytes = crear_documento_word(f"Guía Psicoeducativa - {diag_base}", res)
                        st.session_state.doc_psico_descargable = doc_bytes

                        guardar_en_historial("Psicoeducación", f"{diag_base} -> {destinatario}", res)
                        st.rerun()
                    else:
                        st.error(res)
                        st.session_state.res_psicoeducacion = None
                        st.session_state.doc_psico_descargable = None
            else:
                st.warning("Escribe el diagnóstico o condición base.")

        if st.session_state.res_psicoeducacion:
            st.markdown("---")
            if st.session_state.doc_psico_descargable:
                st.download_button(
                    label="📥 Descargar Guía en Word (.docx)",
                    data=st.session_state.doc_psico_descargable,
                    file_name=f"Psicoeducacion_{st.session_state.psico_diag}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key="btn_dl_psico"
                )
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_psicoeducacion)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 6. CORRECTOR PSICOMÉTRICO
    # ==========================================
    with tabs[5]:
        st.subheader("📝 Corrección e Interpretación de Puntajes Psicométricos")
        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            nombre_prueba = st.text_input("Nombre de la prueba:", placeholder="Ej: BDI-II, WAIS-IV...", key="cp_nombre")
        with col_cp2:
            edad_cp = st.number_input("Edad del paciente:", min_value=1, max_value=120, value=25, key="cp_edad")
        puntajes_texto = st.text_area("Ingresa los puntajes o puntuaciones escalares/percentiles:", key="cp_puntajes")

        if st.button("Interpretar Puntajes", key="btn_cp"):
            if not puede_consultar and not st.session_state.caso_activo:
                st.error("❌ Has agotado tus créditos. Recarga para continuar.")
            elif nombre_prueba.strip() and puntajes_texto.strip():
                with st.spinner("Analizando baremos y rangos normativos..."):
                    res = interpretar_puntajes_psicometricos(nombre_prueba, puntajes_texto, edad_cp, api_key_env)
                    if res and not res.startswith("❌"):
                        st.session_state.res_corrector_psicometrico = res
                        guardar_en_historial("Corrector Psicométrico", f"{nombre_prueba} - {puntajes_texto}", res)
                        st.rerun()
                    else:
                        st.error(res)
                        st.session_state.res_corrector_psicometrico = None
            else:
                st.warning("Ingresa el nombre de la prueba y los puntajes.")

        if st.session_state.res_corrector_psicometrico:
            st.markdown("---")
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(st.session_state.res_corrector_psicometrico)
            st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # 7. MI HISTORIAL
    # ==========================================
    with tabs[6]:
        st.subheader("📂 Mi Historial de Consultas Realizadas")
        st.write(f"Casos/Créditos consumidos en la cuenta: **{consultas_usadas}**")
        st.markdown("---")

        historial_bd = obtener_historial_usuario(user["id"], limite=100)

        if historial_bd:
            col_hist1, col_hist2 = st.columns([3, 1])
            with col_hist1:
                st.caption(f"Mostrando {len(historial_bd)} consulta(s), de la más reciente a la más antigua.")
            with col_hist2:
                if st.button("🗑️ Borrar todo mi historial", key="btn_borrar_historial"):
                    st.session_state["confirmar_borrado"] = True

            if st.session_state.get("confirmar_borrado"):
                st.warning("¿Seguro que deseas borrar TODO tu historial? Esta acción no se puede deshacer.")
                col_conf1, col_conf2 = st.columns(2)
                with col_conf1:
                    if st.button("✅ Sí, borrar", key="btn_confirmar_borrado"):
                        borrar_historial_usuario(user["id"])
                        st.session_state.historial_consultas = []
                        st.session_state["confirmar_borrado"] = False
                        st.success("Historial borrado.")
                        st.rerun()
                with col_conf2:
                    if st.button("❌ Cancelar", key="btn_cancelar_borrado"):
                        st.session_state["confirmar_borrado"] = False
                        st.rerun()

            for idx, item in enumerate(historial_bd):
                fecha = item.get("creado_en", "")
                with st.expander(f"📌 [{item['modulo']}] - {fecha[:16].replace('T', ' ')}"):
                    st.write("**Entrada:**")
                    st.info(item["entrada"])
                    st.write("**Resultado:**")
                    st.markdown(item["resultado"])
        else:
            st.info("Aún no has realizado consultas. Tu historial aparecerá aquí y se guardará automáticamente aunque cierres sesión.")
