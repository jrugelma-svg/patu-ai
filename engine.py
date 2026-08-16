import os
import io
import base64
import groq
import docx
from io import BytesIO
from PIL import Image

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
        
        # Obtener los bytes del archivo de audio
        if hasattr(archivo_audio, 'read'):
            audio_bytes = archivo_audio.read()
            # Reiniciar puntero por si se vuelve a usar
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


def analizar_imagen_clinica(archivo_imagen, prompt_instrucciones, api_key):
    """Procesa e interpreta imágenes (fichas, capturas, notas) usando Llama Vision."""
    try:
        client = groq.Groq(api_key=api_key)
        
        # Convertir imagen a base64
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
    """Procesa archivos subidos (DOCX, PDF, TXT, Imágenes) y la narrativa con Llama 3."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró la variable GROQ_API_KEY en los Secrets de Streamlit."

    try:
        contenido_texto = ""
        nombre = getattr(archivo, 'name', '').lower() if archivo else ""

        # Manejar imágenes con Vision API
        if nombre.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            return analizar_imagen_clinica(archivo, instrucciones, api_key)

        # Manejar documentos de texto
        if nombre.endswith('.docx'):
            contenido_texto = extraer_texto_docx(archivo)
        elif nombre.endswith('.pdf'):
            contenido_texto = extraer_texto_pdf(archivo)
        elif nombre.endswith('.txt'):
            contenido_texto = archivo.read().decode('utf-8')

        client = groq.Groq(api_key=api_key)
        
        prompt = f"""
        Eres un asistente analista experto en psicología clínica y ciencias del comportamiento.
        Analiza el siguiente caso basándote en la información proporcionada.

        DATOS E INSTRUCCIONES DEL PACIENTE:
        "{instrucciones}"

        CONTENIDO EXTRAÍDO DEL DOCUMENTO:
        "{contenido_texto}"
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al procesar el análisis: {str(e)}"
