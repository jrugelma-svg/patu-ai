import requests
import json

def llamar_gemini_directo(prompt, api_key):
    """
    Llama directamente a la API REST de Gemini evitando problemas de librerías y versiones.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = data.get('error', {}).get('message', 'Error desconocido')
            return f"⚠️ Error de la API ({response.status_code}): {error_msg}"
            
    except Exception as e:
        return f"⚠️ Error de conexión: {str(e)}"


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
    return llamar_gemini_directo(prompt, api_key)


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
    return llamar_gemini_directo(prompt, api_key)


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
    return llamar_gemini_directo(prompt, api_key)
