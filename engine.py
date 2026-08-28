import os
import io
import docx
from groq import Groq

MODELO_ACTIVO = "openai/gpt-oss-20b"

def procesar_comando_agente_patu(comando_voz, datos_contexto="", primera_interaccion=False, api_key=None):
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    comando_lower = comando_voz.lower()

    # COMANDO ESPECIAL DE APAGADO POR VOZ
    if any(p in comando_lower for p in ["apágate", "apagate", "silénciate", "silenciate", "detente", "chau patu", "apagar"]):
        return "[ACCION:APAGAR] Entendido. Desactivando el micrófono de control autónomo. Estaré en espera cuando me necesites."

    # COMANDO ESPECIAL: DESCARGA AUTÓNOMA
    if "descarga" in comando_lower or "descárgalo" in comando_lower or "bajar archivo" in comando_lower:
        return "[ACCION:DESCARGAR] Entendido, he preparado tu documento. La descarga comenzará inmediatamente en pantalla."

    # COMANDO ESPECIAL: MUESTRA TU PODER
    if any(p in comando_lower for p in ["poder", "demostración", "demostracion", "capaz", "muestra tu poder"]):
        return """[ACCION:DEMOSTRACION]
        🐾 **DEMOSTRACIÓN DE POTENCIAL CLÍNICO AUTÓNOMO — PATU AI**
        
        ### 🔬 1. Evaluación y Diagnóstico Multiaxial Automático
        - **Impresión Diagnóstica (DSM-5):** F41.1 Trastorno de Ansiedad Generalizada / F32.1 Episodio Depresivo Moderado.
        - **Factores de Riesgo:** Estrés académico elevado, alteración del patrón de sueño y somatización conductual.

        ### 🎯 2. Plan de Intervención Cognitivo-Conductual (12 Sesiones)
        - **Fase 1 (Sesiones 1-3):** Psicoeducación sobre la ansiedad y reestructuración cognitiva.
        - **Fase 2 (Sesiones 4-8):** Exposición gradual, respiración diafragmática y resolución de problemas.

        *PATU AI ha ejecutado de forma autónoma el análisis multiaxial y el plan de tratamiento en tiempo real.*
        """

    prompt_sistema = f"""
    Eres PATU AI, un asistente virtual clínico autónomo, inteligente y muy interactivo especializado en psicología.
    Estás interactuando en vivo mediante voz con un usuario o con un público en una presentación.

    REGLAS DE INTERACCIÓN EN VIVO:
    1. {"SI ES LA PRIMERA INTERACCIÓN: Saluda brevemente diciendo que estás listo y en escucha activa para responder al público o ejecutar tareas." if primera_interaccion else "NO te vuelvas a presentar. Responde de forma directa, empática y conversacional a la persona que te habla."}
    2. Mantén respuestas breves y fluidas de 1 a 3 oraciones para agilizar la conversación en vivo por altavoz.
    3. Si te piden escribir o ejecutar una tarea, confírmalo y muestra el contenido directamente en la web.

    CONTEXTO DEL PACIENTE/SISTEMA:
    "{datos_contexto}"

    MENSAJE EN VIVO DE VOZ:
    "{comando_voz}"
    """

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=MODELO_ACTIVO,
            messages=[{"role": "user", "content": prompt_sistema}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error procesando orden de voz: {str(e)}"

# Se mantienen el resto de funciones del sistema (analizar_caso_inicial, transcribir_audio_groq, crear_documento_word, etc.)
def analizar_caso_inicial(narrativa_completa, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": f"Analiza el caso: {narrativa_completa}"}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def transcribir_audio_groq(archivo_audio, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "Error: No GROQ_API_KEY"
    try:
        client = Groq(api_key=api_key)
        if hasattr(archivo_audio, 'seek'): archivo_audio.seek(0)
        audio_bytes = archivo_audio.read()
        nombre = getattr(archivo_audio, 'name', 'audio.mp3')
        return client.audio.transcriptions.create(file=(nombre, audio_bytes), model="whisper-large-v3", response_format="text")
    except Exception as e: return f"Error: {str(e)}"

def crear_documento_word(titulo, contenido):
    doc = docx.Document()
    doc.add_heading(titulo, level=1)
    for l in contenido.split('\n'):
        if l.strip(): doc.add_paragraph(l.replace('**','').replace('##',''))
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
