import os
import io
import base64
import groq
import docx
from io import BytesIO

try:
    import pypdf
except ImportError:
    pypdf = None


def extraer_texto_docx(archivo_docx):
    """Lee el contenido completo de un archivo Word (.docx)."""
    try:
        doc = docx.Document(archivo_docx)
        texto_completo = []
        for paragrafo in doc.paragraphs:
            if paragrafo.text.strip():
                texto_completo.append(paragrafo.text)
        return "\n".join(texto_completo)
    except Exception as e:
        return f"Error al leer el archivo Word: {str(e)}"


def extraer_texto_pdf(archivo_pdf):
    """Lee el contenido completo de un archivo PDF."""
    try:
        if pypdf is None:
            return "Librería pypdf no disponible."
        reader = pypdf.PdfReader(archivo_pdf)
        texto = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                texto.append(t)
        return "\n".join(texto)
    except Exception as e:
        return f"Error al leer PDF: {str(e)}"


def crear_documento_word(titulo, contenido_texto):
    """Genera un archivo .docx en memoria para su descarga directa."""
    doc = docx.Document()
    doc.add_heading(titulo, level=1)
    
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


def transcribir_audio_groq(archivo_audio, api_key=None):
    """Transcribe un archivo de audio mediante Whisper en Groq."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    try:
        client = groq.Groq(api_key=api_key)
        nombre_archivo = getattr(archivo_audio, 'name', 'dictado_voz.wav')
        
        if hasattr(archivo_audio, 'read'):
            audio_bytes = archivo_audio.read()
            if hasattr(archivo_audio, 'seek'):
                archivo_audio.seek(0)
        else:
            audio_bytes = archivo_audio

        transcription = client.audio.transcriptions.create(
            file=(nombre_archivo, audio_bytes),
            model="whisper-large-v3-turbo",
            response_format="text",
            language="es"
        )
        return str(transcription).strip()
    except Exception as e:
        return f"Error en la transcripción: {str(e)}"


def analizar_caso_inicial(narrativa_completa, api_key=None):
    """Analiza el caso clínico devolviendo evaluación multiaxial, códigos, brechas y pruebas recomendadas."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Eres un psicólogo clínico senior y experto en psicodiagnóstico. Analiza detalladamente el siguiente caso clínico y redacta una evaluación clínica estructurada obligatoriamente en las siguientes secciones exactas:

    ### 1. Resumen Sintomático Principal
    (Síntesis cualitativa de la clínica expresada, afecto, conducta y pensamiento)

    ### 2. Brechas de Información y Datos Faltantes Críticos
    (Información relevante indispensable por indagar)

    ### 3. Preguntas Sugeridas para la Siguiente Consulta
    (Listado de preguntas clínicas clave para profundizar)

    ### 4. Evaluación Diagnóstica y Formulación Multiaxial (DSM-5 / CIE-10 / CIE-11)
    - **Eje I / Trastornos Clínicos:** (Incluir nombre exacto y códigos DSM-5 y CIE-10/CIE-11)
    - **Eje II / Trastornos de la Personalidad y Desarrollo:** (Incluir diagnósticos o rasgos con códigos)
    - **Eje III / Condiciones Médicas Generales:** (Enfermedades físicas o hallazgos somáticos)
    - **Eje IV / Problemas Psicosociales y Ambientales:** (Factores de estrés, red de apoyo, estresores)
    - **Eje V / Evaluación de la Actividad Global (GAF/EEAG):** (Estimación del nivel de funcionamiento actual)

    ### 5. Batería de Pruebas Psicométricas Sugeridas
    (Listado de tests e inventarios normados recomendados para confirmar la hipótesis, indicando qué evalúa cada uno y por qué se aplica a este caso)

    CASO CLÍNICO:
    "{narrativa_completa}"
    """
    try:
        client = groq.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error en análisis clínico: {str(e)}"


def obtener_pruebas_psicometricas(caso_o_sintomas, edad, etapa, api_key=None):
    """Recomienda batería de pruebas psicométricas estandarizadas."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Actúa como un psicómetra experto. Recomienda una batería de pruebas psicométricas estandarizadas y validadas para el siguiente paciente:
    - Edad: {edad} años ({etapa})
    - Síntomas / Constructo a evaluar: {caso_o_sintomas}

    Para cada prueba incluye: Nombre completo y acrónimo, Qué evalúa, Rango de edad de aplicación, y Justificación clínica.
    """
    try:
        client = groq.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al obtener pruebas: {str(e)}"


def generar_informe_premium(datos_dict, enfoque, plantilla_texto="", api_key=None):
    """Genera un informe psicológico estructurado o adaptado a plantilla."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    instrucciones_plantilla = ""
    if plantilla_texto.strip():
        instrucciones_plantilla = f"\nUSA LA SIGUIENTE ESTRUCTURA Y ESTILO DE PLANTILLA:\n{plantilla_texto}\n"

    prompt = f"""
    Redacta un informe psicológico formal bajo un enfoque {enfoque}.
    {instrucciones_plantilla}

    DATOS DEL PACIENTE Y CASO:
    - Nombre / Iniciales: {datos_dict.get('nombre')}
    - Edad: {datos_dict.get('edad')}
    - Género: {datos_dict.get('genero')}
    - Ocupación: {datos_dict.get('ocupacion')}
    - Motivo de Consulta: {datos_dict.get('motivo')}
    - Problema Actual y Antecedentes: {datos_dict.get('problema_actual')}
    - Pruebas Aplicadas: {datos_dict.get('pruebas_aplicadas')}
    - Observaciones: {datos_dict.get('observaciones')}
    - Conclusiones y Diagnóstico: {datos_dict.get('diagnostico')}

    Utiliza lenguaje profesional, técnico y redacta el informe listo para firma profesional.
    """
    try:
        client = groq.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al generar informe: {str(e)}"


def analizar_transcripcion_sesion(transcripcion, api_key=None):
    """Analiza la dinámica, afecto y temáticas de una sesión psicológica."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Como terapeuta supervisor, analiza esta transcripción o notas de sesión clínica:
    "{transcripcion}"

    Proporciona:
    1. Temas Principales Abordados
    2. Estado Afectivo y Conducta del Paciente
    3. Intervenciones Clave del Terapeuta y su Efectividad
    4. Resistencias o Mecanismos de Defensa Observados
    5. Recomendaciones y Objetivos para la Próxima Sesión
    """
    try:
        client = groq.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al analizar sesión: {str(e)}"


def generar_plantilla_psicoeducacion(diagnostico, destinatario, api_key=None):
    """Genera material psicoeducativo en formato folleto/guía."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Crea una guía psicoeducativa clara, empática y rigurosa sobre el diagnóstico o condición: "{diagnostico}".
    El material está dirigido a: {destinatario}.

    Estructura:
    - ¿Qué es y qué no es esta condición?
    - Síntomas y manifestaciones habituales
    - Estrategias de afrontamiento y manejo práctico
    - Mitos comunes
    - Pautas de apoyo y cuándo buscar ayuda de emergencia
    """
    try:
        client = groq.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al generar psicoeducación: {str(e)}"


def interpretar_puntajes_psicometricos(nombre_prueba, puntajes_texto, edad, api_key=None):
    """Interpreta cualitativamente puntajes psicométricos."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    prompt = f"""
    Como experto psicómetra, interpreta los siguientes resultados psicométricos:
    - Nombre de la Prueba: {nombre_prueba}
    - Edad del Paciente: {edad} años
    - Puntajes / Resultados: {puntajes_texto}

    Genera:
    1. Clasificación Cualitativa por Subescala/Dimensión (Bajo, Promedio, Alto, etc.)
    2. Análisis cualitativo e integración de los resultados
    3. Párrafo redactado listo para insertar en un informe psicológico
    """
    try:
        client = groq.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al interpretar puntajes: {str(e)}"


def analizar_imagen_clinica(archivo_imagen, prompt_instrucciones, api_key=None):
    """Procesa imágenes usando Llama Vision."""
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    try:
        client = groq.Groq(api_key=api_key)
        image_bytes = archivo_imagen.read()
        if hasattr(archivo_imagen, 'seek'):
            archivo_imagen.seek(0)
            
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analiza clínicamente la siguiente imagen según estas instrucciones: {prompt_instrucciones}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.2
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error al analizar la imagen: {str(e)}"


def procesar_analisis(archivo, instrucciones):
    """Función de procesamiento general para documentos e imágenes."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró la variable GROQ_API_KEY."

    try:
        contenido_texto = ""
        nombre = getattr(archivo, 'name', '').lower() if archivo else ""

        if nombre.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            prompt_vis = f"{instrucciones}. Incluye Formulación Multiaxial DSM-5/CIE-10/CIE-11 con códigos y Pruebas Psicométricas Sugeridas."
            return analizar_imagen_clinica(archivo, prompt_vis, api_key)

        if nombre.endswith('.docx'):
            contenido_texto = extraer_texto_docx(archivo)
        elif nombre.endswith('.pdf'):
            contenido_texto = extraer_texto_pdf(archivo)
        elif nombre.endswith('.txt'):
            contenido_texto = archivo.read().decode('utf-8')

        client = groq.Groq(api_key=api_key)
        
        prompt = f"""
        Eres un asistente analista experto en psicología clínica.
        Analiza el siguiente caso de forma exhaustiva:

        INSTRUCCIONES Y CONTEXTO:
        "{instrucciones}"

        DOCUMENTO ADICIONAL:
        "{contenido_texto}"

        Asegúrate de incluir obligatoriamente:
        1. Resumen Sintomático.
        2. Brechas de Información.
        3. Preguntas para la Siguiente Consulta.
        4. Evaluación Multiaxial DSM-5 / CIE-10 / CIE-11 (Ejes I al V con códigos diagnósticos).
        5. Batería de Pruebas Psicométricas Recomendadas.
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al procesar el análisis: {str(e)}"
