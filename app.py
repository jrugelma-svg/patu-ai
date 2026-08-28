import streamlit as st
import os
import io
import docx
from database import verificar_login, registrar_usuario, obtener_usuario_por_id, guardar_consulta, obtener_historial_usuario
from engine import procesar_comando_agente_patu, transcribir_audio_groq, crear_documento_word, analizar_caso_inicial

st.set_page_config(page_title="PATU AI - Agente Autónomo", page_icon="🐾", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #F4EEFB 0%, #E9DEFA 100%) !important; }
    .header-banner { background: linear-gradient(120deg, #7C42D1 0%, #8A93FF 50%, #FF85B8 100%); padding: 20px; border-radius: 18px; color: white !important; }
    .resultado-ia { background-color: #FFFFFF !important; padding: 22px !important; border-radius: 16px !important; border-left: 6px solid #7C42D1 !important; margin-top: 15px !important; }
    .patu-holograma-box { background: #FFFFFF; border: 3px solid #7C42D1; border-radius: 20px; padding: 15px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state: st.session_state.user = None
if "patu_encendido" not in st.session_state: st.session_state.patu_encendido = True
if "primera_interaccion_patu" not in st.session_state: st.session_state.primera_interaccion_patu = True
if "res_patu_live" not in st.session_state: st.session_state.res_patu_live = None

# Autenticación simplificada
if not st.session_state.user:
    st.subheader("🔑 Acceso PATU AI Workstation")
    email = st.text_input("Correo Electrónico")
    password = st.text_input("Contraseña", type="password")
    if st.button("🚀 Iniciar Sesión"):
        exito, usuario, msg = verificar_login(email, password)
        if exito:
            st.session_state.user = usuario
            st.rerun()
        else:
            st.error(msg)
else:
    api_key_env = os.getenv("GROQ_API_KEY")

    st.markdown('<div class="header-banner"><h1>🐾 PATU AI Workstation PRO</h1><p>Agente Virtual Interactivo en Vivo</p></div>', unsafe_allow_html=True)

    fase = st.radio("Fase:", ["🐾 PATU LIVE (Modo Conversacional)", "🔬 Módulos Clínicos"], horizontal=True)

    if "PATU LIVE" in fase:
        st.subheader("🎙️ Agente de Voz Autónomo en Escucha Activa")
        st.caption("Habla con PATU. Cuando quieras finalizar la conversación en vivo, dile: 'Patu, apágate'.")

        col_av, col_ctrl = st.columns([1, 2])
        
        with col_av:
            st.markdown('<div class="patu-holograma-box">', unsafe_allow_html=True)
            estado_txt = "🟢 EN ESCUCHA ACTIVA" if st.session_state.patu_encendido else "🔴 PATU APAGADO / EN ESPERA"
            st.markdown(f"### 🐾 PATU AI<br><small>{estado_txt}</small>", unsafe_allow_html=True)
            
            if not st.session_state.patu_encendido:
                if st.button("🟢 Volver a Encender a PATU"):
                    st.session_state.patu_encendido = True
                    st.session_state.primera_interaccion_patu = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col_ctrl:
            if st.session_state.patu_encendido:
                audio_input = st.audio_input("Presiona el micrófono y habla naturalmente con PATU:", key="mic_patu_live")

                if audio_input is not None:
                    audio_bytes = audio_input.getvalue()
                    if st.session_state.get("last_patu_audio") != audio_bytes:
                        with st.spinner("🐱 PATU escuchando y procesando respuesta..."):
                            comando = transcribir_audio_groq(audio_input, api_key_env)
                            if comando and not str(comando).startswith("Error"):
                                st.session_state["last_patu_audio"] = audio_bytes
                                resp = procesar_comando_agente_patu(str(comando), "", st.session_state.primera_interaccion_patu, api_key_env)
                                st.session_state.primera_interaccion_patu = False
                                
                                # Si el comando detectó apagado
                                if "[ACCION:APAGAR]" in resp:
                                    st.session_state.patu_encendido = False
                                
                                st.session_state.res_patu_live = {"pregunta": str(comando), "respuesta": resp}
                                st.rerun()

        # Presentación de respuesta y sintesis
        if st.session_state.res_patu_live:
            st.markdown('<div class="resultado-ia">', unsafe_allow_html=True)
            st.markdown(f"🗣️ **Tú / Público:** *\"{st.session_state.res_patu_live['pregunta']}\"*")
            
            resp_texto = st.session_state.res_patu_live['respuesta']
            
            if "[ACCION:APAGAR]" in resp_texto:
                st.warning("🔴 **PATU AI ha desactivado su modo de escucha activa por orden de voz.**")
                st.markdown(resp_texto.replace("[ACCION:APAGAR]", ""))
            elif "[ACCION:DESCARGAR]" in resp_texto:
                st.success("⚡ **Acción Ejecutada:** Generando documento solicitado...")
                doc_clean = resp_texto.replace("[ACCION:DESCARGAR]", "")
                st.download_button("📥 Descargar Archivo Word", data=crear_documento_word("Documento PATU AI", doc_clean), file_name="Documento_PATU.docx")
                st.markdown(doc_clean)
            else:
                st.markdown(f"🐾 **PATU AI:** {resp_texto.replace('[ACCION:DEMOSTRACION]', '')}")

            # Síntesis de voz hablada
            voz_clean = resp_texto.replace("[ACCION:APAGAR]", "").replace("[ACCION:DESCARGAR]", "").replace("[ACCION:DEMOSTRACION]", "").replace('*', '').replace('#', '')
            js_speak = f"""
            <script>
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{voz_clean[:250]}");
            msg.lang = 'es-ES';
            msg.rate = 1.0;
            msg.pitch = 1.1;
            window.speechSynthesis.speak(msg);
            </script>
            """
            st.components.v1.html(js_speak, height=0)
            st.markdown('</div>', unsafe_allow_html=True)
