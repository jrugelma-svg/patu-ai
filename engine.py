import groq
import docx
from io import BytesIO

def extraer_texto_docx(archivo_docx):
    """
    Lee el contenido completo de un archivo Word (.docx) subido por el usuario.
    """
    try:
        doc = docx.Document(archivo_docx)
        texto_completo = []
        for paragrafo in doc.paragraphs:
            if paragrafo.text.strip():
                texto_completo.append(paragrafo.text)
        return "\n".join(texto_completo)
    except Exception as e:
        return f"Error al leer el archivo Word: {str(e)}"


def crear_documento_word(titulo, contenido_texto):
    """
    Genera un archivo .docx en memoria a partir de un texto para su descarga directa.
    """
    doc = docx.Document()
    
    # Encabezado / Título
    doc.add_heading(titulo, level=1)
    
    # Agregar párrafos
    lineas = contenido_texto.split('\n')
    for linea in lineas:
        if linea.strip():
            if linea.startswith('###') or linea.startswith('##'):
                doc.add_heading(linea.replace('#', '').strip(), level=2)
            elif linea.startswith('*') or linea.startswith('-'):
                doc.add_paragraph(linea.replace('*', '').replace('-', '').strip(), style='List Bullet')
            else:
                doc.add_paragraph(linea.strip())
                
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio


def analizar_caso_inicial(narrativa, api_key):
    """
    Analiza la narrativa clínica inicial identificando brechas de información e hipótesis diagnósticas.
    """
    try:
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Eres un psicólogo clínico experto y supervisor de casos.
        Analiza la siguiente narrativa clínica inicial y proporciona un reporte estructurado con:
        1. Resumen Sintomático Principal
        2. Brechas de Información o Datos Faltantes Críticos
        3. Hipótesis Diagnósticas Preliminares (CIE-11 / DSM-5)
        4. Recomendaciones Inmediatas para la Siguiente Consulta

        NARRATIVA DEL CASO:
        "{narrativa}"
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al consultar la IA: {str(e)}"


def obtener_pruebas_psicometricas(narrativa, edad=25, etapa="Adulto", api_key=""):
    """
    Genera sugerencias de pruebas psicométricas con filtro estricto por edad y etapa del desarrollo.
    """
    if isinstance(edad, str) and len(edad) > 20 and not api_key:
        api_key = edad
        edad = 25

    try:
        client = groq.Groq(api_key=api_key)
        
        prompt = f"""
        Eres un psicometrista clínico experto. Analiza el siguiente caso y recomienda una batería de pruebas psicométricas adecuada.

        DATOS CRÍTICOS DEL PACIENTE:
        - EDAD EXACTA: {edad} años.
        - ETAPA DEL DESARROLLO: {etapa}.
        
        CASO CLÍNICO:
        "{narrativa}"

        REGLA DE ORO RESTRICTIVA DE EDAD (ESTRICTAMENTE OBLIGATORIA):
        1. SOLO debes sugerir pruebas cuya baremación, rango normativo y ficha técnica corresponda EXACTAMENTE a los {edad} años del paciente ({etapa}).
        2. Queda TOTALMENTE PROHIBIDO sugerir pruebas creadas para adultos a niños/adolescentes (usar WISC-V, BDI-Y, MACI, M-CHAT, BASC-3, SENA, etc., según corresponda).
        3. Queda TOTALMENTE PROHIBIDO sugerir pruebas infantiles a adultos.

        ESTRUCTURA DE TU RESPUESTA:
        ### 🧪 Batería Psicométrica Recomendada (Rango: {edad} años / {etapa})
        
        Para cada prueba recomendada, incluye:
        * **Nombre exacto de la prueba y versión válida para la edad:** (Ej: WISC-V, SENA, BASC-3, CAS-2, WAIS-IV).
        * **Rango normativo oficial:** Confirma el rango de edad de aplicación según la ficha técnica.
        * **Área evaluada:** (Ej: Coeficiente Intelectual, Ansiedad, Funciones Ejecutivas, Personalidad).
        * **Justificación clínica:** Por qué es adecuada para la problemática redactada y la edad específica de este paciente.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al consultar la IA: {str(e)}"


def generar_diagnostico_multiaxial(narrativa, datos_extra, api_key):
    """
    Formula una evaluación multiaxial completa basada en la narrativa y datos contextuales.
    """
    try:
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Eres un psiquiatra y psicólogo clínico experto.
        Genera una formulación diagnóstica estructurada considerando el modelo multiaxial/integral.

        NARRATIVA PRINCIPAL:
        "{narrativa}"

        DATOS CONTEXTUALES ADICIONALES:
        "{datos_extra}"

        Por favor, estructura el reporte indicando:
        - Eje / Dimensión 1: Trastornos Clínicos Principales
        - Eje / Dimensión 2: Aspectos de Personalidad / Desarrollo
        - Eje / Dimensión 3: Condiciones Médicas Relevantes
        - Eje / Dimensión 4: Problemas Psicosociales y Ambientales
        - Eje / Dimensión 5: Evaluación del Funcionamiento Global (EEAG/WHODAS)
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al consultar la IA: {str(e)}"


def buscar_recursos_pruebas(query_prueba, api_key):
    """
    Rastrea e identifica información y fichas técnicas sobre pruebas psicométricas.
    """
    try:
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Actúa como un bibliotecario y especialista en psicometría.
        El usuario está buscando información, fichas técnicas o recursos sobre la siguiente prueba o tema:
        "{query_prueba}"

        Proporciona un reporte detallado que incluya:
        1. Ficha Técnica Completa (Nombre, autores, año, edad de aplicación, administración, duración).
        2. Constructos y subescalas que evalúa.
        3. Dónde o cómo encontrar legítimamente el material (editoriales oficiales como Tea Ediciones, Pearson, Paidós, u organizaciones dominio público).
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al consultar la IA: {str(e)}"


def generar_informe_premium(datos_dict, enfoque, plantilla_texto="", api_key=""):
    """
    Redacta un informe psicológico adaptándose estrictamente a la plantilla provista (.docx o texto).
    """
    try:
        client = groq.Groq(api_key=api_key)
        
        if plantilla_texto and plantilla_texto.strip():
            instruccion_plantilla = f"""
            ESTRUCTURA OBLIGATORIA Extraída de la Plantilla Subida por el Usuario:
            Debes utilizar EXACTAMENTE la siguiente estructura, títulos, secciones y estilo de redacción provisto en el archivo subido por el usuario. Rellena cada sección con los datos clínicos correspondientes del paciente:

            --- INICIO PLANTILLA SUBIDA ---
            {plantilla_texto}
            --- FIN PLANTILLA SUBIDA ---
            """
        else:
            instruccion_plantilla = """
            ESTRUCTURA ESTÁNDAR:
            Usa el modelo formal estándar: I. Datos de Filiación, II. Motivo de Consulta, III. Observaciones Conductuales, IV. Pruebas Aplicadas, V. Resultados e Interpretación, VI. Conclusiones Diagnósticas y VII. Recomendaciones.
            """

        prompt = f"""
        Eres un psicólogo clínico experto en redacción de informes diagnósticos.
        Redacta el informe psicológico completo utilizando un enfoque {enfoque}.

        DATOS DEL PACIENTE:
        - Nombre/Iniciales: {datos_dict.get('nombre')}
        - Edad: {datos_dict.get('edad')}
        - Género: {datos_dict.get('genero')}
        - Ocupación: {datos_dict.get('ocupacion')}

        CONTENIDO CLÍNICO:
        - Motivo de consulta: {datos_dict.get('motivo')}
        - Problema actual / Antecedentes: {datos_dict.get('problema_actual')}
        - Pruebas aplicadas: {datos_dict.get('pruebas_aplicadas')}
        - Observaciones conductuales: {datos_dict.get('observaciones')}
        - Conclusiones / Diagnóstico: {datos_dict.get('diagnostico')}

        {instruccion_plantilla}

        REGLAS:
        1. Mantén un lenguaje clínico formal y profesional.
        2. No omitas ninguna sección de la plantilla del usuario.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al consultar la IA: {str(e)}"


def transcribir_audio_groq(archivo_audio, api_key):
    """
    Transcribe un archivo de audio (o grabado en vivo) mediante la API de Whisper en Groq.
    """
    try:
        client = groq.Groq(api_key=api_key)
        
        # Verificar si viene de st.audio_input o subida de archivos
        nombre_archivo = getattr(archivo_audio, 'name', 'dictado_voz.wav')
        
        transcription = client.audio.transcriptions.create(
            file=(nombre_archivo, archivo_audio.read()),
            model="whisper-large-v3",
            response_format="text",
            language="es"
        )
        return transcription
    except Exception as e:
        return f"Error en la transcripción: {str(e)}"


def analizar_transcripcion_sesion(transcripcion, api_key):
    """
    Analiza clínicamente la transcripción de una sesión de terapia.
    """
    try:
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Eres un supervisor clínico. Analiza la siguiente transcripción de una sesión psicológica:

        TRANSCRIPCIÓN:
        "{transcripcion}"

        Proporciona:
        1. Temas clave abordados.
        2. Estado afectivo y patrones de pensamiento detectados en el paciente.
        3. Intervenciones principales del terapeuta y su efectividad.
        4. Tareas o aspectos a dar seguimiento en la próxima sesión.
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al consultar la IA: {str(e)}"


def generar_plantilla_psicoeducacion(diag_base, destinatario, api_key):
    """
    Genera una guía o folleto psicoeducativo según el diagnóstico y el destinatario.
    """
    try:
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Crea un documento psicoeducativo claro, empático y profesional sobre el siguiente tema/diagnóstico:
        "{diag_base}"

        DESTINATARIO: {destinatario}

        Estructura el material con:
        - ¿Qué es y qué no es esta condición? (Explicado de forma accesible)
        - Síntomas comunes expuestos amigablemente
        - Estrategias de afrontamiento o manejo práctico diario
        - Mitos comunes vs. Realidades
        - Palabras de apoyo / Cierre empático
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al consultar la IA: {str(e)}"


def interpretar_puntajes_psicometricos(nombre_prueba, puntajes_texto, edad_paciente, api_key):
    """
    Interpreta puntajes directos, escalares, percentiles o puntuaciones T de pruebas psicológicas.
    """
    try:
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Actúa como un psicometrista clínico senior experto en baremación y psicometría aplicada.
        
        DATOS DE LA EVALUACIÓN:
        - Prueba Aplicada: {nombre_prueba}
        - Edad del Paciente: {edad_paciente} años
        - Puntajes Ingresados por el Clínico: 
        "{puntajes_texto}"

        Genera un informe psicométrico de corrección e interpretación que incluya:
        1. **Clasificación y Rango Normativo:** Para cada puntaje/subescala (ej. Muy Alto, Superior, Promedio, Bajo, Clínicamente Significativo).
        2. **Análisis Cualitativo e Interpretación:** Significado clínico de los hallazgos en relación con las funciones cognitivas, emocionales o conductuales evaluadas.
        3. **Sugerencia de Síntesis para el Informe:** Un párrafo listo para copiar y pagar en la sección de "Resultados Psicométricos" de un informe clínico.
        """
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al interpretar puntajes: {str(e)}"
