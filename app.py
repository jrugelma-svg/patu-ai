import streamlit as st
import io
import os
import docx
from docx import Document
import engine  # Módulo personalizado para consultar la API de Groq

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Workstation Psicología - Diagnóstico e Informes",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTADOS DE SESIÓN (SESSION STATE)
# ---------------------------------------------------------
if "historial" not in st.session_state:
    st.session_state.historial = []

if "caso_actual" not in st.session_state:
    st.session_state.caso_actual = ""

if "datos_extra" not in st.session_state:
    st.session_state.datos_extra = ""

if "resultado_semejanzas" not in st.session_state:
    st.session_state.resultado_semejanzas = None

if "resultado_pruebas" not in st.session_state:
    st.session_state.resultado_pruebas = None

if "resultado_multiaxial" not in st.session_state:
    st.session_state.resultado_multiaxial = None

if "modo_premium" not in st.session_state:
    st.session_state.modo_premium = False

if "ultimo_informe" not in st.session_state:
    st.session_state.ultimo_informe = None

if "ultimo_nombre_paciente" not in st.session_state:
    st.session_state.ultimo_nombre_paciente = "Paciente"

if "texto_transcrito_temp" not in st.session_state:
    st.session_state.texto_transcrito_temp = None

if "ultimo_psicoeducacion" not in st.session_state:
    st.session_state.ultimo_psicoeducacion = None

# ---------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (COMPATIBLES CON MODO OSCURO Y CLARO)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Tarjetas adaptables al tema */
    .split-card, .premium-card {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #CBD5E1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }

    /* Asegurar contraste de texto dentro de tarjetas */
    .split-card *, .premium-card * {
        color: #1E293B !important;
    }

    .split-card h1, .split-card h2, .split-card h3,
    .premium-card h1, .premium-card h2, .premium-card h3 {
        color: #0F172A !important;
        font-weight: 700;
    }

    /* Badges */
    .premium-badge {
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Botones */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# FUNCIÓN AUXILIAR: GENERAR DOCUMENTO WORD DESDE MARKDOWN
# ---------------------------------------------------------
def generar_word_desde_markdown(texto_markdown):
    doc = Document()
    
    lineas = texto_markdown.split('\n')
    for linea in lineas:
        linea_str = linea.strip()
        if not linea_str:
            continue
            
        if linea_str.startswith('# '):
            doc.add_heading(linea_str[2:], level=1)
        elif linea_str.startswith('## '):
            doc.add_heading(linea_str[3:], level=2)
        elif linea_str.startswith('### '):
            doc.add_heading(linea_str[4:], level=3)
        elif linea_str.startswith('* ') or linea_str.startswith('- '):
            doc.add_paragraph(linea_str[2:], style='List Bullet')
        else:
            doc.add_paragraph(linea_str)
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# ---------------------------------------------------------
# BARRA LATERAL (SIDEBAR) - CONFIGURACIÓN DE API KEY DIRECTA
# ---------------------------------------------------------

# 🔑 >>> PEGA TU API KEY DE GROQ AQUÍ ENTRE LAS COMILLAS <<<
GROQ_API_KEY_DIRECTA = "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"

# Lógica para usar la clave ingresada o los secrets si existieran
api_key = GROQ_API_KEY_DIRECTA.strip()

if not api_key or api_key == "gsk_TU_CLAVE_AQUI_PEGA_AQ":
    # Intentar buscar en st.secrets si no se ha pegado arriba
    try:
        if "GROQ_API_KEY" in st.secrets:
            api_key = str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/387/387561.png", width=65)
    st.title("Workstation Clínico")
    st.caption("Asistente para Psicólogos y Evaluadores")

    st.markdown("---")

    st.subheader("⚙️ Módulo de Trabajo")
    if st.button("⭐ Conmutar Vista Premium / Rápida", use_container_width=True):
        st.session_state.modo_premium = not st.session_state.modo_premium
        st.rerun()

    if st.session_state.modo_premium:
        st.info("Modo Activo: **Módulo Premium**")
    else:
        st.info("Modo Activo: **Workstation Rápido**")

    st.markdown("---")
    st.caption("v2.5 • Desarrollado con Streamlit & Groq AI")


# =========================================================
# VISTA 1: EDITOR DE INFORMES PREMIUM & HERRAMIENTAS AVANZADAS
# =========================================================
if st.session_state.modo_premium:

    col_nav, _ = st.columns([0.3, 0.7])
    with col_nav:
        if st.button("⬅️ Volver a Workstation Rápido", type="secondary"):
            st.session_state.modo_premium = False
            st.rerun()

    st.markdown('''
    <div style="text-align: center; margin-top: 10px; margin-bottom: 25px;">
        <span class="premium-badge">⭐ MÓDULO PREMIUM</span>
        <h2 style="margin: 5px 0;">Herramientas Diagnósticas e Informes Integrados</h2>
        <p>Genera reportes técnicos, procesa audios, elabora material psicoeducativo y consulta baterías psicométricas.</p>
    </div>
    ''', unsafe_allow_html=True)

    tab_informe, tab_transcripcion, tab_psicoed, tab_pruebas = st.tabs([
        "📄 Generador de Informes (.docx)", 
        "🎙️ Analizador de Audios y Transcripciones", 
        "📘 Psicoeducación para Pacientes/Familias",
        "🧪 Buscador de Pruebas"
    ])

    # PESTAÑA 1: GENERADOR DE INFORMES
    with tab_informe:
        col_form, col_resultado = st.columns([0.45, 0.55], gap="large")

        with col_form:
            st.markdown("### 📝 Datos del Caso / Evaluación")
            
            enfoque = st.selectbox(
                "🎯 Selecciona el Enfoque del Informe:",
                ["Clínico", "Educativo", "Organizacional"]
            )

            st.markdown("---")
            st.markdown("##### 👤 Datos de Filiación")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                nombre = st.text_input("Nombre / Iniciales:", placeholder="Ej. J.P.")
                edad = st.text_input("Edad:", placeholder="Ej. 28 años")
            with col_f2:
                genero = st.text_input("Sexo / Género:", placeholder="Ej. Femenino")
                ocupacion = st.text_input("Ocupación / Escolaridad:", placeholder="Ej. Estudiante universitario")

            st.markdown("---")
            st.markdown("##### 📋 Contenido Clínico")
            
            motivo = st.text_area("1. Motivo de Consulta:", placeholder="Ej: Ansiedad, problemas para dormir...", height=70)
            problema_actual = st.text_area("2. Problema Actual / Antecedentes:", placeholder="Ej: Rompimiento reciente...", height=80)
            pruebas_aplicadas = st.text_area("3. Pruebas / Instrumentos Aplicados:", placeholder="Ej: BDI-II, HAM-A...", height=70)
            observaciones = st.text_area("4. Observaciones Conductuales:", placeholder="Ej: Contacto visual escaso...", height=70)
            diagnostico = st.text_area("5. Impresión Diagnóstica / Conclusiones:", placeholder="Ej: Sospecha de episodio depresivo...", height=70)

            btn_generar_informe = st.button("🚀 Redactar e Integrar Informe con IA", type="primary", use_container_width=True)

        with col_resultado:
            st.subheader("📄 Vista Previa del Documento")

            if btn_generar_informe:
                if not api_key:
                    st.error("⚠️ Configura tu API Key en la línea 105 de app.py")
                else:
                    datos_dict = {
                        "nombre": nombre, "edad": edad, "genero": genero, "ocupacion": ocupacion,
                        "motivo": motivo, "problema_actual": problema_actual,
                        "pruebas_aplicadas": pruebas_aplicadas, "observaciones": observaciones,
                        "diagnostico": diagnostico
                    }
                    with st.spinner(f"Sintetizando e integrando el informe con enfoque {enfoque}..."):
                        informe_final = engine.generar_informe_premium(datos_dict, enfoque, api_key)
                        st.session_state.ultimo_informe = informe_final
                        st.session_state.ultimo_nombre_paciente = nombre if nombre.strip() else "Paciente"

            if st.session_state.ultimo_informe:
                st.markdown('<div class="split-card">', unsafe_allow_html=True)
                st.markdown(st.session_state.ultimo_informe)
                st.markdown('</div>', unsafe_allow_html=True)

                docx_buffer = generar_word_desde_markdown(st.session_state.ultimo_informe)
                nombre_archivo = f"Informe_Psicologico_{st.session_state.ultimo_nombre_paciente}.docx"

                st.download_button(
                    label="📥 Descargar Informe en Word (.docx)",
                    data=docx_buffer,
                    file_name=nombre_archivo,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.markdown('''
                <div class="split-card" style="text-align: center; padding: 50px 20px;">
                    <p style="font-size: 3rem; margin-bottom: 10px;">📄</p>
                    <h3>Espacio de Trabajo Premium</h3>
                    <p style="color: #475569 !important; font-size: 0.95rem; max-width: 420px; margin: 0 auto;">
                        Completa los campos de la izquierda y presiona <b>Redactar e Integrar Informe con IA</b>.
                    </p>
                </div>
                ''', unsafe_allow_html=True)

    # PESTAÑA 2: ANALIZADOR DE AUDIOS
    with tab_transcripcion:
        col_t_left, col_t_right = st.columns([0.45, 0.55], gap="large")

        with col_t_left:
            st.markdown("### 🎙️ Procesador de Sesión Extensa")
            st.caption("Sube la grabación de audio de la consulta o pega directamente las notas/transcripción.")

            opcion_entrada = st.radio(
                "Selecciona el origen de la sesión:",
                ["📁 Subir Grabación de Audio", "✍️ Pegar Texto / Notas Directas"],
                horizontal=True
            )

            transcripcion_para_analizar = ""

            if "Subir Grabación" in opcion_entrada:
                audio_file = st.file_uploader(
                    "Carga el archivo de audio (.mp3, .m4a, .wav, .ogg):",
                    type=["mp3", "m4a", "wav", "ogg", "mp4"]
                )
                if audio_file:
                    st.audio(audio_file)
                    btn_procesar_audio = st.button("⚡ Transcribir Audio y Analizar con IA", type="primary", use_container_width=True)
                    
                    if btn_procesar_audio:
                        if not api_key:
                            st.error("⚠️ Configura tu API Key en la línea 105 de app.py")
                        else:
                            with st.spinner("1/2 Transcribiendo audio con Whisper AI..."):
                                texto_transcrito = engine.transcribir_audio_groq(audio_file, api_key)
                                
                            if texto_transcrito.startswith("⚠️"):
                                st.error(texto_transcrito)
                            else:
                                st.success("✅ Transcripción completada con éxito.")
                                st.session_state.texto_transcrito_temp = texto_transcrito
                                transcripcion_para_analizar = texto_transcrito

            else:
                transcripcion_input = st.text_area(
                    "Transcripción o Registro Verbal de la Sesión:",
                    placeholder="[Paciente 10:15]: Siento que ya no puedo con la presión del trabajo...\n[Terapeuta 10:16]: ¿Qué situaciones específicas han detonado esta sensación?...",
                    height=280
                )
                btn_analizar_texto = st.button("🔍 Analizar Texto de Sesión", type="primary", use_container_width=True)
                if btn_analizar_texto:
                    transcripcion_para_analizar = transcripcion_input

        with col_t_right:
            st.subheader("📊 Análisis Diagnóstico Cualitativo")

            if transcripcion_para_analizar.strip():
                if not api_key:
                    st.error("⚠️ Configura tu API Key en la línea 105 de app.py")
                else:
                    with st.spinner("2/2 Analizando discurso, detectando afecto y evaluando alertas de riesgo..."):
                        resultado_transcripcion = engine.analizar_transcripcion_sesion(transcripcion_para_analizar, api_key)
                        
                        if st.session_state.texto_transcrito_temp:
                            with st.expander("📄 Ver Transcripción Literal Generada"):
                                st.write(st.session_state.texto_transcrito_temp)
                        
                        st.markdown('<div class="split-card">', unsafe_allow_html=True)
                        st.markdown(resultado_transcripcion)
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('''
                <div class="split-card" style="text-align: center; padding: 50px 20px;">
                    <p style="font-size: 3rem; margin-bottom: 10px;">🎙️</p>
                    <h3>Analizador de Audio y Diálogo Terapéutico</h3>
                    <p style="color: #475569 !important; font-size: 0.95rem; max-width: 420px; margin: 0 auto;">
                        Sube la <b>grabación de audio</b> o pega las <b>notas de la sesión</b> a la izquierda para extraer automáticamente <b>alertas de riesgo, afecto, palabras recurrentes y puntos clave</b>.
                    </p>
                </div>
                ''', unsafe_allow_html=True)

    # PESTAÑA 3: PSICOEDUCACIÓN
    with tab_psicoed:
        col_p_left, col_p_right = st.columns([0.45, 0.55], gap="large")

        with col_p_left:
            st.markdown("### 📘 Generador de Guía Psicoeducativa")
            st.caption("Convierte diagnósticos o notas clínicas técnicas en una guía clara, empática y fácil de comprender.")

            destinatario = st.selectbox(
                "🎯 Dirigido a:",
                ["Paciente", "Padres / Cuidadores", "Familiar / Pareja"]
            )

            diagnostico_psico = st.text_area(
                "Diagnóstico o Cuadro Clínico a Traducir:",
                placeholder="Ej. Trastorno de Ansiedad Generalizada con ataques de pánico intermitentes y evitación conductual...",
                height=180
            )

            btn_generar_psicoed = st.button("✨ Generar Guía Psicoeducativa", type="primary", use_container_width=True)

        with col_p_right:
            st.subheader("📄 Guía Traducida y Empática")

            if btn_generar_psicoed:
                if not api_key:
                    st.error("⚠️ Configura tu API Key en la línea 105 de app.py")
                elif not diagnostico_psico.strip():
                    st.warning("⚠️ Ingresa la información clínica o diagnóstico a traducir.")
                else:
                    with st.spinner("Traduciendo concepto técnico a un lenguaje empático y accesible..."):
                        guia_generada = engine.generar_plantilla_psicoeducacion(diagnostico_psico, destinatario, api_key)
                        st.session_state.ultimo_psicoeducacion = guia_generada

            if st.session_state.ultimo_psicoeducacion:
                st.markdown('<div class="split-card">', unsafe_allow_html=True)
                st.markdown(st.session_state.ultimo_psicoeducacion)
                st.markdown('</div>', unsafe_allow_html=True)

                docx_buffer_psico = generar_word_desde_markdown(st.session_state.ultimo_psicoeducacion)
                st.download_button(
                    label="📥 Descargar Guía Psicoeducativa en Word (.docx)",
                    data=docx_buffer_psico,
                    file_name=f"Guia_Psicoeducativa_{destinatario.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary",
                    use_container_width=True
                )
            else:
                st.markdown('''
                <div class="split-card" style="text-align: center; padding: 50px 20px;">
                    <p style="font-size: 3rem; margin-bottom: 10px;">📘</p>
                    <h3>Material de Apoyo para Paciente y Familia</h3>
                    <p style="color: #475569 !important; font-size: 0.95rem; max-width: 420px; margin: 0 auto;">
                        Ingresa el diagnóstico o cuadro a la izquierda para generar un documento descargable en Word con <b>lenguaje empático, explicaciones analógicas y pautas de apoyo cotidiano</b>.
                    </p>
                </div>
                ''', unsafe_allow_html=True)

    # PESTAÑA 4: BUSCADOR DE PRUEBAS
    with tab_pruebas:
        st.markdown("### 🔗 Buscador de Fuentes y Enlaces de Pruebas")
        col_b1, col_b2 = st.columns([0.7, 0.3])
        with col_b1:
            prueba_query = st.text_input("Buscar prueba psicométrica:", placeholder="Ej. STAI, WAIS-IV, Beck Depression...", label_visibility="collapsed")
        with col_b2:
            btn_buscar_prueba = st.button("🔎 Buscar Recursos", type="secondary", use_container_width=True)

        if btn_buscar_prueba:
            if not api_key:
                st.error("⚠️ Configura tu API Key en la línea 105 de app.py")
            elif not prueba_query.strip():
                st.warning("⚠️ Escribe el nombre o acrónimo de la prueba a buscar.")
            else:
                with st.spinner(f"Buscando ficha técnica y referencias para {prueba_query}..."):
                    resultado_busqueda = engine.buscar_recursos_pruebas(prueba_query, api_key)
                    st.markdown('<div class="split-card">', unsafe_allow_html=True)
                    st.markdown(resultado_busqueda)
                    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# VISTA 2: WORKSTATION RÁPIDO (EVALUACIÓN EN TRES PASOS)
# =========================================================
else:
    st.markdown('''
    <div style="text-align: center; margin-top: 5px; margin-bottom: 25px;">
        <h2>Workstation Clínico Integrado</h2>
        <p style="color: #94A3B8 !important;">Análisis progresivo de casos: del lenguaje coloquial al diagnóstico multiaxial.</p>
    </div>
    ''', unsafe_allow_html=True)

    col_izq, col_der = st.columns([0.45, 0.55], gap="large")

    # COLUMNA IZQUIERDA: FORMULARIO DE ENTRADA
    with col_izq:
        st.markdown("### 📥 1. Narrativa o Motivo de Consulta")
        
        texto_caso_input = st.text_area(
            "Escribe o pega la narrativa clínica (acepta lenguaje coloquial):",
            value=st.session_state.caso_actual,
            placeholder="Ejemplo: Paciente de 32 años refiere que desde hace 4 meses siente palpitaciones constantes, miedo intenso a salir a lugares concurridos y dificultad para conciliar el sueño...",
            height=180
        )
        st.session_state.caso_actual = texto_caso_input

        btn_paso1 = st.button("🔎 PASO 1: Analizar Semejanzas y Brechas", type="primary", use_container_width=True)

        # Bloque de datos adicionales
        if st.session_state.resultado_semejanzas:
            st.markdown("---")
            st.markdown("### 📋 2. Contexto Adicional para Multiaxial")
            
            datos_extra_input = st.text_area(
                "Ingresa antecedentes médicos, estresores psicosociales o notas extra:",
                value=st.session_state.datos_extra,
                placeholder="Ejemplo: Problemas financieros recientes, antecedente familiar de depresión, examen médico general sin alteraciones sintomáticas...",
                height=120
            )
            st.session_state.datos_extra = datos_extra_input

            col_btn2, col_btn3 = st.columns(2)
            with col_btn2:
                btn_paso2 = st.button("🧪 Recomendar Pruebas", use_container_width=True)
            with col_btn3:
                btn_paso3 = st.button("🎯 Generar Multiaxial", type="primary", use_container_width=True)

    # COLUMNA DERECHA: RESULTADOS CLÍNICOS
    with col_der:
        st.markdown("### 📊 Panel de Análisis Clínico")

        if btn_paso1:
            if not api_key:
                st.error("⚠️ Configura tu API Key en la línea 105 de app.py")
            elif not st.session_state.caso_actual.strip():
                st.warning("⚠️ Escriba una narrativa o caso clínico primero.")
            else:
                with st.spinner("Analizando semejanzas diagnósticas y detectando brechas de información..."):
                    res = engine.analizar_caso_inicial(st.session_state.caso_actual, api_key)
                    st.session_state.resultado_semejanzas = res

        if 'btn_paso2' in locals() and btn_paso2:
            if not api_key:
                st.error("⚠️ Configura tu API Key en la línea 105 de app.py")
            else:
                with st.spinner("Generando sugerencias de baterías y pruebas psicométricas..."):
                    res_p = engine.obtener_pruebas_psicometricas(st.session_state.caso_actual, api_key)
                    st.session_state.resultado_pruebas = res_p

        if 'btn_paso3' in locals() and btn_paso3:
            if not api_key:
                st.error("⚠️ Configura tu API Key en la línea 105 de app.py")
            else:
                with st.spinner("Integrando datos y formulando evaluación multiaxial completa..."):
                    res_m = engine.generar_diagnostico_multiaxial(
                        st.session_state.caso_actual, 
                        st.session_state.datos_extra, 
                        api_key
                    )
                    st.session_state.resultado_multiaxial = res_m

        # Renderizado de Resultados en Tarjetas
        if st.session_state.resultado_semejanzas:
            st.markdown('<div class="split-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.resultado_semejanzas)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.resultado_pruebas:
            st.markdown('<div class="split-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.resultado_pruebas)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.resultado_multiaxial:
            st.markdown('<div class="split-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.resultado_multiaxial)
            st.markdown('</div>', unsafe_allow_html=True)

        if not st.session_state.resultado_semejanzas:
            st.markdown('''
            <div class="split-card" style="text-align: center; padding: 50px 20px;">
                <p style="font-size: 3rem; margin-bottom: 10px;">📋</p>
                <h3>Panel de Control Clínico Vacío</h3>
                <p style="color: #475569 !important; font-size: 0.95rem; max-width: 400px; margin: 0 auto;">
                    Escribe la narrativa del paciente en el panel de la izquierda y presiona <b>PASO 1</b> para iniciar la evaluación diagnóstica.
                </p>
            </div>
            ''', unsafe_allow_html=True)
