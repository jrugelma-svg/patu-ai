import io
import os
from groq import Groq
from duckduckgo_search import DDGS

# =========================================================
# 1. BÚSQUEDA WEB REAL DE PRUEBAS PSICOMÉTRICAS
# =========================================================
def buscar_recursos_pruebas(prueba_query, api_key):
    """
    Realiza una búsqueda en tiempo real usando DuckDuckGo para encontrar
    enlaces directos, PDFs y fichas técnicas, y luego los sintetiza con Groq.
    """
    try:
        # 1. Búsqueda en vivo en todo internet mediante DuckDuckGo
        resultados_raw = []
        with DDGS() as ddgs:
            query_busqueda = f"test psicometrico {prueba_query} manual PDF ficha tecnica"
            results = ddgs.text(query_busqueda, max_results=6)
            
            if results:
                for r in results:
                    resultados_raw.append(f"- **[{r['title']}]({r['href']})**:\n  _{r['body']}_")

        if resultados_raw:
            contexto_busqueda = "\n\n".join(resultados_raw)
        else:
            contexto_busqueda = "No se encontraron enlaces directos en la búsqueda en vivo en este momento."

        # 2. Sintetizar y dar formato con la API de Groq
        client = Groq(api_key=api_key)
        
        prompt = f"""
Eres un asistente experto en psicometría. El usuario busca información sobre la prueba o test: '{prueba_query}'.

A continuación tienes los resultados REALES extraídos de internet en tiempo real:
{contexto_busqueda}

Tu tarea es organizar la información y responder con la siguiente estructura en Markdown:

### 🧪 Ficha Técnica y Enlaces de Consulta: {prueba_query.upper()}

1. **Ficha Técnica Rápida:**
   - **Nombre Oficial / Acrónimo:** (Basado en tu conocimiento clínico sobre la prueba)
   - **Objetivo principal:** (Qué evalúa)
   - **Población / Edad de aplicación:** 

2. **🔗 Enlaces y Fuentes Reales Encontradas en la Web:**
   Presenta CADA UNO de los enlaces extraídos arriba formateados limpiamente como hipervínculos funcionales `[Título del sitio](URL)`, añadiendo una breve síntesis de 1 línea sobre el contenido del enlace (ej. documento PDF, artículo académico, ficha técnica, etc.).
"""

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ No se pudo realizar la búsqueda web en este momento: {str(e)}"


# =========================================================
# 2. ANÁLISIS CLÍNICO INICIAL Y MULTIAXIAL
# =========================================================
def analizar_caso_inicial(narrativa_caso, api_key):
    """Analiza la narrativa del caso, hallando semejanzas y brechas de información."""
    try:
        client = Groq(api_key=api_key)
        prompt = f"""
Eres un asistente clínico avanzado. Revisa la siguiente narrativa de un paciente (puede incluir lenguaje coloquial):
"{narrativa_caso}"

Realiza lo siguiente:
1. **Semejanzas Diagnósticas:** Identifica posibles cuadros clínicos o hipótesis diagnósticas preliminares según DSM-5/CIE-11.
2. **Brechas de Información / Faltantes:** Indica qué datos clave faltan por indagar en la entrevista (antecedentes, tiempo de evolución, estresores, etc.).

Formatea la respuesta en Markdown con encabezados claros y viñetas.
"""
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en API de Groq: {str(e)}"


def obtener_pruebas_psicometricas(narrativa_caso, api_key):
    """Recomienda baterías y pruebas psicométricas según la narrativa."""
    try:
        client = Groq(api_key=api_key)
        prompt = f"""
Basándote en la siguiente información clínica:
"{narrativa_caso}"

Recomienda de 3 a 5 instrumentos o pruebas psicométricas/proyectivas pertinentes para evaluar el caso. 
Por cada prueba incluye:
- Nombre completo y acrónimo.
- Qué evalúa específicamente.
- Justificación clínica de su elección.
"""
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en API de Groq: {str(e)}"


def generar_diagnostico_multiaxial(narrativa_caso, datos_extra, api_key):
    """Genera una evaluación diagnóstica integrando contexto y multiaxialidad."""
    try:
        client = Groq(api_key=api_key)
        prompt = f"""
Integra la siguiente información para formular una evaluación diagnóstica multiaxial estructurada:

**Narrativa Principal:** "{narrativa_caso}"
**Datos Contextuales Adicionales:** "{datos_extra}"

Estructura el resultado en Markdown abarcando:
- **Eje I / Cuadro Principal:** Trastornos clínicos.
- **Eje II:** Aspectos de personalidad o del desarrollo.
- **Eje III:** Condiciones médicas pertinentes.
- **Eje IV:** Problemas psicosociales y ambientales.
- **Eje V / EEAG:** Evaluación de la actividad global estimada.
- **Impresión Síntesis / Recomendaciones Terapéuticas.**
"""
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en API de Groq: {str(e)}"


# =========================================================
# 3. MÓDULO PREMIUM: GENERADOR DE INFORMES
# =========================================================
def generar_informe_premium(datos_dict, enfoque, api_key):
    """Genera la redacción integral de un informe psicológico formal."""
    try:
        client = Groq(api_key=api_key)
        prompt = f"""
Redacta un informe psicológico profesional y formal con un enfoque **{enfoque}**.

**Datos de Filiación:**
- Nombre/Iniciales: {datos_dict.get('nombre')}
- Edad: {datos_dict.get('edad')}
- Género/Sexo: {datos_dict.get('genero')}
- Ocupación: {datos_dict.get('ocupacion')}

**Contenido del Caso:**
- Motivo de Consulta: {datos_dict.get('motivo')}
- Problema Actual / Antecedentes: {datos_dict.get('problema_actual')}
- Pruebas / Instrumentos Aplicados: {datos_dict.get('pruebas_aplicadas')}
- Observaciones Conductuales: {datos_dict.get('observaciones')}
- Impresión Diagnóstica / Conclusiones: {datos_dict.get('diagnostico')}

Organiza el informe en Markdown técnico y formal con las secciones tradicionales (I. Datos de Filiación, II. Motivo de Consulta, III. Observaciones Conductuales, IV. Pruebas Aplicadas, V. Resultados e Interpretación, VI. Conclusiones Diagnósticas y VII. Recomendaciones).
"""
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en API de Groq: {str(e)}"


# =========================================================
# 4. TRANSCRIPCIÓN DE AUDIO Y ANÁLISIS DE SESIÓN
# =========================================================
def transcribir_audio_groq(archivo_audio, api_key):
    """Transcribe un archivo de audio usando el modelo Whisper en Groq."""
    try:
        client = Groq(api_key=api_key)
        
        # Obtener extensión y bytes del archivo
        nombre_archivo = getattr(archivo_audio, "name", "audio.mp3")
        bytes_audio = archivo_audio.read()
        
        transcription = client.audio.transcriptions.create(
            file=(nombre_archivo, bytes_audio),
            model="whisper-large-v3",
            response_format="text"
        )
        return transcription
    except Exception as e:
        return f"⚠️ Error al transcribir el audio: {str(e)}"


def analizar_transcripcion_sesion(transcripcion_texto, api_key):
    """Analiza el diálogo de una sesión transcrita buscando afecto, riesgos y temas clave."""
    try:
        client = Groq(api_key=api_key)
        prompt = f"""
Analiza la siguiente transcripción/registro verbal de una sesión terapéutica:

"{transcripcion_texto}"

Extrae en formato Markdown:
1. **Puntos Clave y Temáticas Recurrentes:**
2. **Estado Afectivo y Tono Emocional Predominante:**
3. **Alertas de Riesgo o Indicadores Críticos (si existen):**
4. **Resumen Síntesis para la Historia Clínica:**
"""
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en API de Groq: {str(e)}"


# =========================================================
# 5. GENERADOR DE GUÍA PSICOEDUCATIVA
# =========================================================
def generar_plantilla_psicoeducacion(diagnostico_texto, destinatario, api_key):
    """Convierte lenguaje técnico en una guía psicoeducativa empática."""
    try:
        client = Groq(api_key=api_key)
        prompt = f"""
Crea una guía psicoeducativa accesible, empática y fácil de entender dirigida a: **{destinatario}**.

**Diagnóstico o Cuadro Clínico Base:**
"{diagnostico_texto}"

La guía debe contener:
1. **¿Qué es esto que está pasando?** (Explicación clara usando metáforas o analogías, sin tecnicismos complejos).
2. **Síntomas Habituales:** (Explicar por qué siente/experimenta esto).
3. **Pautas de Afrontamiento / Cómo Ayudar en el Día a Día:** (Estrategias concretas).
4. **Mensaje de Cierre y Esperanza:**

Usa un tono cálido, comprensivo y estructurado en Markdown.
"""
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error en API de Groq: {str(e)}"
