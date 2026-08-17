import os
import io
import docx
from groq import Groq

# Modelo global activo en la API de Groq
MODELO_GROQ = "llama-3.1-8b-instant"

# ==========================================
# 1. ANALIZADOR CLÍNICO
# ==========================================
def analizar_caso_inicial(narrativa_completa, api_key=None):
    """Genera diagnóstico, brechas, hipótesis y batería sugerida."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Eres un asistente clínico experto en psicología y psicodiagnóstico.
    Analiza el siguiente caso clínico y proporciona un informe estructurado que contenga:
    
    ### 1. Resumen Clínico del Caso
    ### 2. Impresión Diagnóstica Multiaxial (CIE-11 / DSM-5)
    ### 3. Brechas de Información y Preguntas Recomendadas para la Entrevista
    ### 4. Hipótesis Explicativas del Caso
    ### 5. Diagnósticos Diferenciales y Posibles Trastornos a Descartar
    ### 6. Batería de Pruebas Psicométricas Sugeridas
    
    CASO CLÍNICO:
    "{narrativa_completa}"
    """

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODELO_GROQ,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error en análisis clínico: {str(e)}"

# ==========================================
# 2. BUSCADOR DE PRUEBAS
# ==========================================
def obtener_pruebas_psicometricas(caso_o_sintomas, edad, etapa, api_key=None):
    """Recomienda batería de pruebas psicométricas estandarizadas."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Eres un psicómetra experto. Recomienda las pruebas psicométricas y proyectivas normadas más adecuadas para el siguiente caso.
    
    Datos del Paciente:
    - Edad: {edad} años
    - Etapa de desarrollo: {etapa}
    - Sintomatología/Motivo: {caso_o_sintomas}
    
    Por favor indica:
    1. Nombre oficial de la prueba y sigla.
    2. Lo que evalúa (variables/dimensiones).
    3. Justificación de su elección para este caso particular.
    4. Rango de edad normado de la prueba.
    """

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODELO_GROQ,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al buscar pruebas: {str(e)}"

# ==========================================
# 3. GENERADOR DE INFORMES PREMIUM
# ==========================================
def generar_informe_premium(datos_dict, enfoque, plantilla_texto="", api_key=None):
    """Genera un informe psicológico profesional redactado formalmente."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Eres un psicólogo clínico redactor senior. Redacta un informe psicológico formal basado en los datos proporcionados.
    
    Enfoque de Redacción: {enfoque}
    
    Datos del Paciente y Evaluación:
    - Nombre: {datos_dict.get('nombre')}
    - Edad: {datos_dict.get('edad')}
    - Género: {datos_dict.get('genero')}
    - Ocupación: {datos_dict.get('ocupacion')}
    - Motivo de Consulta: {datos_dict.get('motivo')}
    - Problema Actual y Antecedentes: {datos_dict.get('problema_actual')}
    - Pruebas Aplicadas y Resultados: {datos_dict.get('pruebas_aplicadas')}
    - Observaciones Conductuales: {datos_dict.get('observaciones')}
    - Conclusiones y Diagnóstico: {datos_dict.get('diagnostico')}
    
    Guía de estilo/plantilla adicional (si aplica): {plantilla_texto}
    
    Estructura el informe con formalidad clínica, excelente lenguaje técnico y apartados claros.
    """

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODELO_GROQ,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al generar informe: {str(e)}"

# ==========================================
# 4. ANALIZADOR DE SESIONES
# ==========================================
def analizar_transcripcion_sesion(transcripcion, api_key=None):
    """Analiza la dinámica, afecto y temas clave de una sesión."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Eres un supervisor clínico. Analiza la siguiente transcripción de sesión terapéutica:
    
    TRANSCRIPCIÓN:
    "{transcripcion}"
    
    Proporciona:
    1. Temas principales abordados.
    2. Estado afectivo y lenguaje no verbal/verbal del paciente.
    3. Intervenciones clave del terapeuta y su efectividad.
    4. Patrones de pensamiento o defensas detectadas.
    5. Recomendaciones o focos para la siguiente sesión.
    """

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODELO_GROQ,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error en análisis de sesión: {str(e)}"

# ==========================================
# 5. PSICOEDUCACIÓN
# ==========================================
def generar_plantilla_psicoeducacion(diagnostico, destinatario, api_key=None):
    """Genera un folleto/guía psicoeducativa adaptada."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Crea un documento psicoeducativo claro, empático y profesional.
    
    - Condición/Diagnóstico: {diagnostico}
    - Dirigido a: {destinatario}
    
    Incluye:
    1. ¿Qué es y qué no es esta condición? (Lenguaje accesible)
    2. Síntomas comunes expuestos con empatía.
    3. Estrategias de afrontamiento y pautas prácticas diarias.
    4. ¿Cuándo buscar ayuda de emergencia?
    5. Mitos vs. Realidades.
    """

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODELO_GROQ,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al generar psicoeducación: {str(e)}"

# ==========================================
# 6. CORRECTOR PSICOMÉTRICO
# ==========================================
def interpretar_puntajes_psicometricos(nombre_prueba, puntajes, edad, api_key=None):
    """Interpreta los puntajes brutos/escalares de una prueba."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Eres un psicómetra. Interpreta los siguientes datos de evaluación psicométrica:
    
    - Prueba: {nombre_prueba}
    - Edad del evaluado: {edad} años
    - Puntajes/Puntuaciones: {puntajes}
    
    Por favor detalla:
    1. Conversión/Ubicación en baremos o rangos (Severidad, Percentiles, Desviaciones según corresponda).
    2. Interpretación clínica cualitativa de cada área evaluada.
    3. Conclusión psicométrica integradora.
    """

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODELO_GROQ,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al interpretar puntajes: {str(e)}"

# ==========================================
# FUNCIONES DE APOYO (AUDIO Y DOCUMENTOS)
# ==========================================
def transcribir_audio_groq(archivo_audio, api_key=None):
    """Transcribe archivos de audio utilizando Whisper en Groq."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: No se encontró GROQ_API_KEY."

    try:
        client = Groq(api_key=api_key)
        audio_bytes = archivo_audio.read()
        nombre_archivo = getattr(archivo_audio, 'name', 'audio.mp3')
        
        transcription = client.audio.transcriptions.create(
            file=(nombre_archivo, audio_bytes),
            model="whisper-large-v3",
            response_format="text"
        )
        return transcription
    except Exception as e:
        return f"Error en transcripción: {str(e)}"

def crear_documento_word(titulo, contenido):
    """Convierte el texto generado en un archivo .docx para descargar."""
    doc = docx.Document()
    doc.add_heading(titulo, level=1)
    
    lineas = contenido.split('\n')
    for linea in lineas:
        if linea.startswith('### '):
            doc.add_heading(linea.replace('### ', ''), level=2)
        elif linea.startswith('## '):
            doc.add_heading(linea.replace('## ', ''), level=2)
        elif linea.startswith('# '):
            doc.add_heading(linea.replace('# ', ''), level=1)
        else:
            doc.add_paragraph(linea)
            
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def extraer_texto_docx(archivo_docx):
    """Extrae el texto de un archivo .docx de plantilla."""
    try:
        doc = docx.Document(archivo_docx)
        texto_completo = []
        for p in doc.paragraphs:
            texto_completo.append(p.text)
        return "\n".join(texto_completo)
    except Exception:
        return ""

def procesar_analisis(archivo, contexto=""):
    """Soporte legacy para procesamiento con archivos."""
    texto_archivo = ""
    if archivo is not None:
        if archivo.name.endswith(".docx"):
            texto_archivo = extraer_texto_docx(archivo)
        elif archivo.name.endswith(".txt"):
            texto_archivo = archivo.read().decode("utf-8")
    
    narrativa = f"{contexto}\n\nContenido del documento:\n{texto_archivo}"
    return analizar_caso_inicial(narrativa)
