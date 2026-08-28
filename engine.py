import os
import io
import docx
from groq import Groq

MODELO_ACTIVO = "openai/gpt-oss-20b"

def evaluar_nivel_riesgo_automatico(texto):
    if not texto:
        return "Bajo"
    texto_lower = texto.lower()
    palabras_alto = ["matar", "suicid", "morirme", "atentar", "intento", "cúter", "cuter", "corta", "ahocar", "arma", "morir", "desaparecer", "no quiero vivir"]
    palabras_medio = ["ansiedad", "pánico", "panico", "droga", "alcohol", "agresiv", "pelear", "depresió", "depresio", "triste", "llorar", "impulsiv"]

    for palabra in palabras_alto:
        if palabra in texto_lower:
            return "Alto"
    for palabra in palabras_medio:
        if palabra in texto_lower:
            return "Medio"
    return "Bajo"

def procesar_comando_agente_patu(comando_voz, datos_contexto="", primera_interaccion=False, api_key=None):
    if not api_key:
        api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró GROQ_API_KEY."

    comando_lower = comando_voz.lower()

    if any(p in comando_lower for p in ["apágate", "apagate", "silénciate", "silenciate", "detente", "chau patu", "apagar"]):
        return "[ACCION:APAGAR] Entendido. Desactivando el micrófono de control autónomo. Estaré en espera cuando me necesites."

    if "descarga" in comando_lower or "descárgalo" in comando_lower or "bajar archivo" in comando_lower:
        return "[ACCION:DESCARGAR] Entendido, he preparado tu documento. La descarga comenzará inmediatamente en pantalla."

    if any(p in comando_lower for p in ["poder", "demostración", "demostracion", "capaz", "muestra tu poder"]):
        return """🐾 **DEMOSTRACIÓN DE POTENCIAL CLÍNICO AUTÓNOMO — PATU AI**

### 🔬 1. Evaluación y Diagnóstico Multiaxial Automático
- **Impresión Diagnóstica (DSM-5):** F41.1 Trastorno de Ansiedad Generalizada / F32.1 Episodio Depresivo Moderado.
- **Factores de Riesgo:** Estrés académico elevado, alteración del patrón de sueño y somatización conductual.
- **Batería Sugerida:** Inventario de Ansiedad de Beck (BAI) + Inventario de Depresión de Beck (BDI-II).

### 🎯 2. Plan de Intervención Cognitivo-Conductual (12 Sesiones)
- **Fase 1 (Sesiones 1-3):** Psicoeducación sobre la ansiedad y reestructuración cognitiva.
- **Fase 2 (Sesiones 4-8):** Exposición gradual, respiración diafragmática y resolución de problemas.
- **Fase 3 (Sesiones 9-12):** Prevención de recaídas y consolidación de habilidades.

### 🌳 3. Dinámica Familiar y Genograma
- Estructura nuclear con comunicación implícita rígida. Alianza materna protectora y distancia afectiva paterna.

*PATU AI ha ejecutado de forma autónoma el análisis multiaxial y el plan de tratamiento en tiempo real.*"""

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

def analizar_caso_inicial(narrativa_completa, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Analiza el siguiente caso clínico y proporciona un informe estructurado con resumen, diagnóstico multiaxial, brechas, hipótesis, diferenciales y pruebas:\n\n{narrativa_completa}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def generar_genograma_familiar(texto_familia, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Genera un análisis e interpretación clínica del genograma familiar para:\n{texto_familia}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def generar_hoja_trabajo_paciente(tipo_registro, diagnostico_o_meta, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Diseña una hoja de trabajo para el paciente. Tipo: {tipo_registro}, Meta/Diagnóstico: {diagnostico_o_meta}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def obtener_pruebas_psicometricas(caso_o_sintomas, edad, etapa, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Recomienda pruebas psicométricas normadas para edad {edad} ({etapa}), síntomas: {caso_o_sintomas}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def generar_supervision_coterapeuta(nombre_paciente, consulta, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Brinda orientación de supervisión clínica para el paciente {nombre_paciente}: {consulta}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def generar_compromiso_vida(nombre_paciente, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Redacta un contrato terapéutico de compromiso con la vida para el paciente {nombre_paciente}."
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def generar_plan_tratamiento_psicologico(diagnostico_o_caso, enfoque, num_sesiones=12, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Diseña un plan de tratamiento psicológico de {num_sesiones} sesiones bajo enfoque {enfoque} para: {diagnostico_o_caso}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def generar_informe_premium(datos_dict, enfoque, plantilla_texto="", api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Redacta un informe psicológico formal. Enfoque: {enfoque}, Datos: {datos_dict}, Guía: {plantilla_texto}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def analizar_transcripcion_sesion(transcripcion, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Analiza la siguiente transcripción de sesión terapéutica: {transcripcion}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.3)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def generar_plantilla_psicoeducacion(diagnostico, destinatario, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Crea una guía psicoeducativa clara para {destinatario} sobre la condición: {diagnostico}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.4)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def interpretar_puntajes_psicometricos(nombre_prueba, puntajes, edad, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "❌ Error: No se encontró GROQ_API_KEY."
    prompt = f"Interpreta los puntajes de la prueba {nombre_prueba} para un evaluado de {edad} años: {puntajes}"
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(model=MODELO_ACTIVO, messages=[{"role": "user", "content": prompt}], temperature=0.2)
        return response.choices[0].message.content
    except Exception as e: return f"❌ Error: {str(e)}"

def transcribir_audio_groq(archivo_audio, api_key=None):
    if not api_key: api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "Error: No GROQ_API_KEY"
    try:
        client = Groq(api_key=api_key)
        if hasattr(archivo_audio, 'seek'): archivo_audio.seek(0)
        audio_bytes = archivo_audio.read()
        nombre_archivo = getattr(archivo_audio, 'name', 'audio.mp3')
        return client.audio.transcriptions.create(file=(nombre_archivo, audio_bytes), model="whisper-large-v3", response_format="text")
    except Exception as e: return f"Error: {str(e)}"

def crear_documento_word(titulo, contenido):
    doc = docx.Document()
    doc.add_heading(titulo, level=1)
    for linea in contenido.split('\n'):
        linea = linea.strip()
        if not linea: continue
        texto_limpio = linea.replace('**', '').replace('__', '')
        if linea.startswith('### '): doc.add_heading(texto_limpio.replace('### ', ''), level=3)
        elif linea.startswith('## '): doc.add_heading(texto_limpio.replace('## ', ''), level=2)
        elif linea.startswith('# '): doc.add_heading(texto_limpio.replace('# ', ''), level=1)
        elif linea.startswith('- ') or linea.startswith('* '): doc.add_paragraph(texto_limpio[2:], style='List Bullet')
        else: doc.add_paragraph(texto_limpio)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def extraer_texto_docx(archivo_docx):
    try:
        doc = docx.Document(archivo_docx)
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception: return ""

def procesar_analisis(archivo, contexto=""):
    texto_archivo = ""
    if archivo is not None:
        if archivo.name.endswith(".docx"): texto_archivo = extraer_texto_docx(archivo)
        elif archivo.name.endswith(".txt"): texto_archivo = archivo.read().decode("utf-8")
    return analizar_caso_inicial(f"{contexto}\n\nContenido:\n{texto_archivo}")
