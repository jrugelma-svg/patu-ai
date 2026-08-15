import groq

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
    Soporta argumentos flexibles para evitar errores de tipo (TypeError).
    """
    # Manejo de compatibilidad por si la API key se envía en lugar de edad o al final
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
        2. Queda TOTALMENTE PROHIBIDO sugerir pruebas creadas para adultos a niños/adolescentes (por ejemplo, NO sugerir WAIS, BDI-II estándar, MMPI-2 a niños o adolescentes tempranos; usar WISC-V, BDI-Y, MACI, M-CHAT, BASC-3, SENA, etc., según corresponda).
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
    Rastrea e identifica información, fichas técnicas y fuentes directas sobre pruebas psicométricas.
    """
    try:
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Actúa como un bibliotecario especializado en psicometría clínica y recursos de evaluación.
        El usuario requiere información técnica y fuentes para acceder a la siguiente prueba o recurso psicométrico:
        "{query_prueba}"

        INSTRUCCIONES DE BÚSQUEDA Y FORMATO:
        Proporciona una respuesta clara, estructurada y sin rodeos. NUNCA respondas diciendo "no se encontraron enlaces directos" o "no puedo buscar en internet". En su lugar, entrega la información bibliográfica exacta y los portales donde se localiza el recurso.

        ESTRUCTURA OBLIGATORIA DE RESPUESTA:

        ### 🧪 Ficha Técnica: {query_prueba}
        * **Nombre Completo:** (Nombre oficial y sigla)
        * **Autor(es) y Año:** (Creadores y versión actual)
        * **Rango de Edad:** (Edades exactas de aplicación)
        * **Tiempo de Administración:** (Minutos estimados)
        * **Áreas / Subescalas que evalúa:** (Listado de variables)

        ### 📌 Dónde Encontrar el Material Oficial
        Indica los distribuidores o editoriales oficiales autorizadas para la adquisición del juego completo (manual, cuadernillos y claves):
        * **Editorial Oficial:** (Ej: Pearson Clinical, TEA Ediciones, El Manual Moderno, Paidós).
        * **Enlace de Búsqueda Directa:** [Buscar en TEA Ediciones](https://www.web.teaediciones.com/Inicio.aspx) | [Buscar en Pearson Clinical](https://www.pearsonclinical.es/)

        ### 📚 Fuentes Académicas y Documentos Consultables (PDF / Artículos)
        Proporciona enlaces de búsqueda directa a repositorios científicos donde los psicólogos pueden consultar la validez, propiedades psicométricas o fichas técnicas de esta prueba:
        * 🔗 [Buscar manuales/artículos en Redalyc](https://www.redalyc.org/busquedaArticuloFiltros.oa?q={query_prueba.replace(' ', '%20')})
        * 🔗 [Buscar validaciones en Dialnet](https://dialnet.unirioja.es/buscar/documentos?query_s={query_prueba.replace(' ', '%20')})
        * 🔗 [Buscar en Google Académico](https://scholar.google.com/scholar?q={query_prueba.replace(' ', '%20')}+propiedades+psicometricas)

        ### 💡 Alternativas o Recurso de Uso Libre (Si aplica)
        Si la prueba consultada es de catálogo cerrado/pago, sugiere una alternativa de dominio público o de acceso libre validada académicamente para evaluar el mismo constructo en la práctica clínica.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al consultar la IA: {str(e)}"


def generar_informe_premium(datos_dict, enfoque, api_key):
    """
    Redacta un informe psicológico estructurado profesional.
    """
    try:
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Eres un psicólogo clínico redactor de informes periciales y clínicos.
        Redacta un informe psicológico completo con un enfoque {enfoque}.

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

        Genera el informe formal con las secciones típicas: I. Datos de Filiación, II. Motivo de Consulta, III. Observaciones, IV. Pruebas Aplicadas, V. Resultados e Interpretación, VI. Conclusiones Diagnósticas y VII. Recomendaciones.
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
    Transcribe un archivo de audio mediante la API de Whisper en Groq.
    """
    try:
        client = groq.Groq(api_key=api_key)
        transcription = client.audio.transcriptions.create(
            file=(archivo_audio.name, archivo_audio.read()),
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
