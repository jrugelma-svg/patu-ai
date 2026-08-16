def procesar_analisis(archivo, instrucciones):
    """
    Función genérica para analizar archivos subidos desde el formulario principal de app.py
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "❌ Error: No se encontró la variable GROQ_API_KEY en las configuraciones (Secrets)."

    try:
        contenido_texto = ""
        nombre = getattr(archivo, 'name', '').lower()

        # Extraer texto según la extensión
        if nombre.endswith('.docx'):
            contenido_texto = extraer_texto_docx(archivo)
        elif nombre.endswith('.txt'):
            contenido_texto = archivo.read().decode('utf-8')
        else:
            contenido_texto = f"Archivo cargado: {nombre}"

        # Consultar la IA
        client = groq.Groq(api_key=api_key)
        prompt = f"""
        Eres un asistente analista experto en psicología y ciencias del comportamiento.
        Analiza el siguiente contenido basándote en las instrucciones provistas.

        INSTRUCCIONES DEL USUARIO:
        "{instrucciones}"

        CONTENIDO DEL DOCUMENTO:
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
