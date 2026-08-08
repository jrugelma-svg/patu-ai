import requests
import json

# Modelo estrella de Groq (Llama 3.3 70B)
MODEL_NAME = "llama-3.3-70b-versatile"

def llamar_groq_api(prompt, api_key):
    """
    Realiza una solicitud HTTP directa a la API de Groq para procesamiento de texto.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            return data['choices'][0]['message']['content']
        else:
            error_msg = data.get('error', {}).get('message', 'Error desconocido')
            return f"⚠️ Error en API de Groq ({response.status_code}): {error_msg}"
            
    except Exception as e:
        return f"⚠️ Error de conexión: {str(e)}"


# =========================================================
# FUNCIONES DE WORKSTATION RÁPIDO
# =========================================================

def analizar_caso_inicial(texto_caso, api_key):
    prompt = f"""
    Actúa como un Supervisor Clínico y Experto en Diagnóstico DSM-5-TR / CIE-10.
    Analiza el siguiente motivo de consulta o caso clínico redactado en lenguaje libre/coloquial.

    CASO CLÍNICO:
    "{texto_caso}"

    POR FAVOR GENERA UN INFORME CLARO Y ESTRUCTURADO EN MARKDOWN CON ESTOS 2 BLOQUES:

    ### 📊 1. Semejanzas Diagnósticas (DSM-5-TR)
    * Mapea el lenguaje coloquial del usuario a criterios clínicos oficiales.
    * Enumera los cuadros o trastornos más semejantes (del mayor al menor probable).
    * Justifica brevemente la razón de la coincidencia.

    ### 🔍 2. Brechas de Información y Datos Faltantes
    * Enumera los síntomas, duración, contexto o criterios que Hacen Falta Observar o Indagar para confirmar/descartar la hipótesis.
    * Sugiere 2 o 3 preguntas clave para la entrevista clínica.
    """
    return llamar_groq_api(prompt, api_key)


def obtener_pruebas_psicometricas(texto_caso, api_key):
    prompt = f"""
    Como experto en Evaluación y Psicometría Clínica, analiza este caso:
    "{texto_caso}"

    Genera una lista de pruebas psicométricas, escalas o test validados recomendados para evaluar o descartar las hipótesis clínicas de este caso.

    PRESENTA LOS RESULTADOS EN EL SIGUIENTE FORMATO MARKDOWN:
    ### 🧪 Batería de Pruebas Psicométricas Recomendadas

    Para cada prueba incluye:
    * **[Nombre Oficial del Test / Acrónimo]:**
      * **Objetivo / Para qué sirve:** (Breve descripción).
      * **Propósito en este caso:** (Qué síntoma o sospecha ayuda a descartar/confirmar).
    """
    return llamar_groq_api(prompt, api_key)


def generar_diagnostico_multiaxial(texto_caso, datos_extra, api_key):
    prompt = f"""
    Con base en la narrativa clínica original y los datos contextuales adicionales brindados, formula una evaluación bajo el esquema del Diagnóstico Multiaxial (DSM-IV-TR / Adaptación DSM-5).

    NARRATIVA CLÍNICA:
    "{texto_caso}"

    DATOS ADICIONALES (Antecedentes/Estresores):
    "{datos_extra}"

    ESTRUCTURA DE SALIDA REQUERIDA (MARKDOWN):
    ### 📋 Evaluación y Diagnóstico Multiaxial Completo

    * **Eje I: Trastornos Clínicos y Otros problemas de atención clínica.**
    * **Eje II: Trastornos de la Personalidad y Mecanismos de Defensa.**
    * **Eje III: Enfermedades Médicas / Antecedentes Orgánicos.**
    * **Eje IV: Problemas Psicosociales y Ambientales (Estresores principales).**
    * **Eje V: Evaluación de la Actividad Global (Escala EEAG / GAF estimada de 1 a 100 y justificación).**
    """
    return llamar_groq_api(prompt, api_key)


# =========================================================
# FUNCIONES PREMIUM: REDACCIÓN DE INFORMES Y RECURSOS
# =========================================================

def generar_informe_premium(datos: dict, enfoque: str, api_key: str):
    """
    Transforma apuntes breves, frases sueltas o borradores en un Informe Psicológico
    formal con terminología técnica rigurosa adaptada al enfoque seleccionado.
    """
    instrucciones_enfoque = {
        "Clínico": "Énfasis en psicopatología (DSM-5-TR / CIE-11), estado mental, sintomatología, diagnóstico presuntivo y plan de intervención psicoterapéutico.",
        "Educativo": "Énfasis en estilos de aprendizaje, rendimiento académico, adaptación socioemocional escolar/universitaria, necesidades educativas (NEE) y pautas psicoeducativas.",
        "Organizacional": "Énfasis en competencias laborales, desempeño, perfil conductual, adecuación al puesto, manejo del estrés ocupacional y recomendaciones de desarrollo."
    }
    
    prompt = f"""
    Actúas como un Psicólogo Senior especialista en redacción técnica e informes profesionales.
    Tu objetivo es tomar los siguientes datos (que pueden contener notas sintéticas, frases sueltas o borradores) y redactar un **INFORME PSICOLÓGICO PROFESIONAL Y COMPLETO**.

    **ENFOQUE REQUERIDO:** {enfoque.upper()}
    **DIRECTRIZ DEL ENFOQUE:** {instrucciones_enfoque.get(enfoque, "Redacción clínica profesional.")}

    **DATOS DEL PACIENTE / EVALUADO:**
    - Nombre / Iniciales: {datos.get('nombre', 'No especificado')}
    - Edad: {datos.get('edad', 'No especificada')}
    - Sexo / Género: {datos.get('genero', 'No especificado')}
    - Ocupación / Escolaridad: {datos.get('ocupacion', 'No especificada')}

    **NOTAS Y APUNTES BRUTOS APORTADOS POR EL PROFESIONAL (PULIR, ENRIQUECER Y TRANSFORMAR CON LENGUAJE TÉCNICO):**
    1. Motivo de Consulta: {datos.get('motivo', 'No detallado')}
    2. Problema Actual / Antecedentes: {datos.get('problema_actual', 'No detallado')}
    3. Pruebas / Instrumentos Aplicados: {datos.get('pruebas_aplicadas', 'No detallado')}
    4. Observaciones Conductuales: {datos.get('observaciones', 'No detalladas')}
    5. Impresión Diagnóstica / Conclusiones: {datos.get('diagnostico', 'No detallado')}

    ---
    **REGLAS DE REDACCIÓN:**
    - Aunque el usuario haya escrito solo dos o tres palabras sueltas en algún campo, utiliza tu conocimiento clínico para redactar párrafos fluidos, elegantes y con terminología técnica experta.
    - Mantén una estructura rigurosa en Markdown utilizando los siguientes apartados:

    # 📄 INFORME PSICOLÓGICO ({enfoque.upper()})

    ### I. DATOS DE FILIACIÓN
    ### II. MOTIVO DE CONSULTA
    ### III. HISTORIA DEL PROBLEMA Y ANTECEDENTES
    ### IV. OBSERVACIONES DE LA CONDUCTA
    ### V. INSTRUMENTOS DE EVALUACIÓN APLICADOS
    ### VI. RESULTADOS E IMPRESIÓN DIAGNÓSTICA
    ### VII. RECOMENDACIONES Y PLAN DE ACCIÓN
    """
    
    return llamar_groq_api(prompt, api_key)


def buscar_recursos_pruebas(nombre_prueba: str, api_key: str):
    """
    Busca ficha técnica, enlaces de consulta y fuentes de referencia para aplicar la prueba psicométrica.
    """
    prompt = f"""
    Actúas como un experto en Psicometría y Evaluación Psicológica.
    El usuario busca información y fuentes para aplicar o consultar la siguiente prueba/test o tema psicométrico: "{nombre_prueba}".

    Proporciona una respuesta clara en Markdown estructurada así:

    ### 🧪 Ficha Técnica y Enlaces de Consulta: {nombre_prueba}

    * **📋 Ficha Técnica Rápida:**
      * **Nombre Oficial / Acrónimo:** 
      * **Autor(es) / Año:** 
      * **Edad de Aplicación:** 
      * **Objetivo Principal:** 

    * **📊 Escalas / Dimensiones que Mide:** (Describe brevemente sus componentes).

    * **🔗 Dónde Consultar o Adquirir el Test (Enlaces y Fuentes):**
      * Proporciona los nombres y URLs/sitios web oficiales (ej. TEA Ediciones, Pearson Clinical, Manual Moderno).
      * Sugiere términos exactos de búsqueda o repositorios académicos abiertos (SciELO, Redalyc, Dialnet) para encontrar los baremos, manuales o cuestionarios en PDF de dominio público.
    """
    
    return llamar_groq_api(prompt, api_key)


# =========================================================
# HERRAMIENTAS DIAGNÓSTICAS AVANZADAS (AUDIO, TRANCRIPCIÓN & PSICOEDUCACIÓN)
# =========================================================

def transcribir_audio_groq(archivo_audio, api_key: str):
    """
    Envía un archivo de audio grabado a la API de Groq usando Whisper-Large-v3-Turbo 
    y devuelve la transcripción literal en texto.
    """
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    files = {
        'file': (archivo_audio.name, archivo_audio.getvalue(), archivo_audio.type),
        'model': (None, 'whisper-large-v3-turbo'),
        'language': (None, 'es')
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, timeout=120)
        data = response.json()
        
        if response.status_code == 200:
            return data.get('text', '')
        else:
            error_msg = data.get('error', {}).get('message', 'Error desconocido')
            return f"⚠️ Error en transcripción ({response.status_code}): {error_msg}"
    except Exception as e:
        return f"⚠️ Error de conexión al procesar audio: {str(e)}"


def analizar_transcripcion_sesion(texto_transcripcion: str, api_key: str):
    """
    Procesa transcripciones extensas o notas de sesiones de larga duración (hasta 120 min)
    y extrae puntos clave, palabras recurrentes, indicadores de riesgo y estado afectivo.
    """
    prompt = f"""
    Actúas como un Supervisor Clínico y Analista Cualitativo del Discurso Terapéutico.
    Analiza minuciosamente el siguiente registro, nota o transcripción extensa de una sesión terapéutica.

    REGISTRO / TRANCRIPCIÓN DE LA SESIÓN:
    "{texto_transcripcion}"

    SINTETIZA Y GENERA UN ANÁLISIS ESTRUCTURADO EN MARKDOWN CON EL SIGUIENTE FORMATO:

    ### 🎙️ Análisis de Transcripción / Notas de Sesión

    ---

    🚨 **1. EVALUACIÓN Y ALERTAS DE RIESGO**
    * **Nivel de Riesgo Detectado:** [Bajo / Moderado / Alto / Crítico]
    * **Indicadores de Riesgo:** (Identifica expresamente si existen menciones explícitas o implícitas de ideación autolítica, autolesión, agresividad hacia terceros, violencia o consumo desadaptativo de sustancias. Si no se observan, indícalo claramente).

    ---

    💭 **2. ESTADO AFECTIVO Y TONO EMOCIONAL**
    * **Afecto / Ánimo Predominante:** (Descripción cualitativa: ej. plano, ebullicionante, lábil, disfórico, ansioso, congruente/incongruente).
    * **Fluctuaciones Terapéuticas:** (Puntos o momentos de la sesión donde el estado emocional cambió drásticamente).

    ---

    🎯 **3. PUNTOS CLAVE Y TEMAS CENTRALES**
    * Enumera los 3 a 5 ejes temáticos principales abordados durante la consulta.
    * Resume brevemente las narrativas clave manifestadas por el paciente.

    ---

    🔤 **4. PALABRAS Y REFRANES RECURRENTES**
    * Lista los conceptos, términos o muletillas más repetidos por el paciente que posean relevancia clínica.

    ---

    🌱 **5. INTERVENCIONES Y SUGERENCIAS PARA LA PRÓXIMA SESIÓN**
    * Sugiere 2 o 3 hipótesis de trabajo o hilos conductuales para profundizar en el siguiente encuentro.
    """
    return llamar_groq_api(prompt, api_key)


def generar_plantilla_psicoeducacion(diagnostico_o_caso: str, destinatario: str, api_key: str):
    """
    Traduce un diagnóstico o cuadro clínico complejo a un lenguaje empático,
    accesible y estructurado para ser entregado al paciente o a su familia.
    """
    prompt = f"""
    Actúas como un Psicólogo Clínico experto en Psicoeducación y Comunicación Empática.
    Tu tarea es traducir la siguiente información clínica a una guía psicoeducativa dirigida a: **{destinatario.upper()}**.

    INFORMACIÓN CLÍNICA / DIAGNÓSTICO BASE:
    "{diagnostico_o_caso}"

    REGLAS DE COMUNICACIÓN Y TONO:
    1. Usa un lenguaje claro, cálido, empático y profesional, evitando tecnicismos médicos/psicológicos innecesarios (o explicándolos con analogías sencillas si se usan).
    2. Mantén un enfoque de desestigmatización y validación emocional.
    3. Asegura que la estructura sea comprensible, esperanzadora y orientada a la acción.

    GENERA EL DOCUMENTO EN MARKDOWN CON LA SIGUIENTE ESTRUCTURA:

    # 📘 Guía Informativa y Psicoeducativa

    ---

    ### 🌟 1. ¿Qué es lo que está pasando?
    * Explica el cuadro o la situación clínica en palabras sencillas.
    * Utiliza una analogía clara para facilitar la comprensión de cómo se manifiesta.

    ---

    ### 🧠 2. ¿Por qué ocurre esto?
    * Explica de forma accesible los factores (emocionales, biológicos o ambientales) que influyen en este estado.
    * Normaliza las reacciones emocionales o síntomas más comunes.

    ---

    ### 🛠️ 3. Herramientas y Estrategias Prácticas para el Día a Día
    * Ofrece de 3 a 5 pautas concretas de autorregulación o manejo cotidiano aplicables para el paciente o la familia.

    ---

    ### 🤝 4. ¿Cómo pueden apoyar los seres queridos? (Red de Apoyo)
    * Pautas sobre lo que **SÍ ayuda** (ej. escucha activa, validación).
    * Pautas sobre lo que **NO ayuda** (ej. juzgar, presionar, minimizar el malestar).

    ---

    ### 💡 5. Mensaje de Cierre y Esperanza
    * Un mensaje breve que refuerce la importancia del proceso terapéutico y el pronóstico positivo con el acompañamiento adecuado.
    """
    return llamar_groq_api(prompt, api_key)
