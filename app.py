import streamlit as st
import database as db

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS PATU PRO
# ==============================================================================
st.set_page_config(
    page_title="PATU — Workstation Clínico v3.0 PRO",
    page_icon="🦆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Estilos generales y colores de la marca PATU */
    .stApp {
        background-color: #FFFDF0;
    }
    .main-header {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 6px solid #E56B55;
        margin-bottom: 2rem;
    }
    .patu-badge {
        background-color: #00A86B;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    /* Botones principales */
    .stButton>button {
        background-color: #E56B55;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #D4543D;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# INICIALIZACIÓN DE SESIÓN DE USUARIO
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ==============================================================================
# PANTALLA DE PAGO / ACTUALIZACIÓN A PREMIUM
# ==============================================================================
def mostrar_modulo_pago(user_id, email_usuario):
    st.error("🔒 Has alcanzado el límite de 4 registros de prueba en el Plan Gratuito.")
    
    st.markdown("---")
    st.markdown("## 🚀 Actualiza a PATU Premium — Acceso Ilimitado")
    st.write("Sigue estos sencillos pasos para activar tu cuenta de forma inmediata:")

    col_qr, col_form = st.columns([1, 1.2])

    with col_qr:
        st.subheader("1. Escanea y paga con Yape o Plin")
        st.info("💰 **S/ 29.90 / mes** — Registro e informes ilimitados")
        
        # Reemplaza la ruta por la imagen real de tu QR cuando la tengas en tu carpeta assets
        try:
            st.image("assets/qr_yape_plin.png", caption="Yape / Plin al: 9XX-XXX-XXX", use_column_width=True)
        except Exception:
            st.warning("📌 *Sube la imagen de tu QR a la carpeta 'assets/qr_yape_plin.png'*")
            st.markdown("""
            **Datos para transferencia manual:**
            * **Yape / Plin:** 9XX-XXX-XXX
            * **Titular:** PATU / Tu Nombre
            """)

    with col_form:
        st.subheader("2. Confirma tu pago")
        st.write("Adjunta la captura de pantalla o voucher para validar tu pago:")
        
        num_operacion = st.text_input("Número de operación (opcional):", placeholder="Ej. 12345678")
        voucher_file = st.file_uploader("Subir foto o captura del voucher (PNG, JPG)", type=["png", "jpg", "jpeg"])

        if st.button("📲 Enviar Comprobante para Activación", use_container_width=True):
            if voucher_file is not None or num_operacion.strip() != "":
                nombre_archivo = voucher_file.name if voucher_file else "Sin archivo"
                exito, msg = db.registrar_solicitud_pago(user_id, email_usuario, num_operacion, nombre_archivo)
                if exito:
                    st.success("✅ ¡Comprobante enviado con éxito! En breve revisaremos tu pago y se activará tu acceso ilimitado.")
                else:
                    st.error(f"Error al registrar el pago: {msg}")
            else:
                st.warning("⚠️ Por favor ingresa el número de operación o adjunta el voucher de pago.")

# ==============================================================================
# FORMULARIOS DE AUTENTICACIÓN (LOGIN Y REGISTRO)
# ==============================================================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>🦆 PATU — Workstation Clínico</h1>", unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

    with tab_login:
        st.subheader("Acceder a mi cuenta")
        email_input = st.text_input("Correo Electrónico:", key="login_email")
        pass_input = st.text_input("Contraseña:", type="password", key="login_pass")
        
        if st.button("Iniciar Sesión", key="btn_login"):
            if email_input and pass_input:
                exito, res = db.verificar_login(email_input, pass_input)
                if exito:
                    st.session_state.logged_in = True
                    st.session_state.user_info = res
                    st.rerun()
                else:
                    st.error(res)
            else:
                st.warning("Por favor completa todos los campos.")

    with tab_register:
        st.subheader("Crear una nueva cuenta")
        nombre_reg = st.text_input("Nombre Completo:", key="reg_nombre")
        email_reg = st.text_input("Correo Electrónico:", key="reg_email")
        pass_reg = st.text_input("Contraseña:", type="password", key="reg_pass")

        if st.button("Crear Cuenta", key="btn_reg"):
            if nombre_reg and email_reg and pass_reg:
                exito, msg = db.registrar_usuario(nombre_reg, email_reg, pass_reg)
                if exito:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Por favor completa todos los campos para el registro.")

else:
    # ==============================================================================
    # SESIÓN INICIADA: SIDEBAR Y BARRA LATERAL
    # ==============================================================================
    user = st.session_state.user_info
    usuario_id = user["id"]
    email_usuario = user["email"]
    nombre_usuario = user["nombre"]
    plan_usuario = user.get("plan", "free")

    # Obtener historial actual del usuario
    historial_actual = db.obtener_historial_usuario(usuario_id)
    total_usados = len(historial_actual)

    with st.sidebar:
        st.markdown(f"👤 **Usuario:** {nombre_usuario}")
        
        # Badge de plan
        if plan_usuario in ["admin", "premium"]:
            st.markdown(f"Plan Actual: <span class='patu-badge'>PLAN {plan_usuario.upper()}</span>", unsafe_allow_html=True)
        else:
            st.markdown("Plan Actual: 🌱 **PLAN FREE**")

        st.markdown("---")

        # Barra de progreso y contador si es PLAN FREE
        if plan_usuario == "free":
            st.caption(f"📊 Uso del Plan Gratuito: {total_usados}/{db.LIMITE_REGISTROS_FREE}")
            progreso = min(total_usados / db.LIMITE_REGISTROS_FREE, 1.0)
            st.progress(progreso)

            restantes = db.LIMITE_REGISTROS_FREE - total_usados
            if restantes > 0:
                st.info(f"Te quedan {restantes} registros de prueba.")
            else:
                st.error("🔒 Has agotado tus registros gratuitos.")

        if st.button("🚪 Cerrar Sesión"):
            st.session_state.logged_in = False
            st.session_state.user_info = None
            st.rerun()

        # ----------------------------------------------------------------------
        # PANEL ADMINISTRADOR (Solo visible para usuarios 'admin')
        # ----------------------------------------------------------------------
        if plan_usuario == "admin":
            st.markdown("---")
            with st.expander("🛠️ Admin: Gestionar Pagos"):
                st.write("Aprobar o cambiar plan de usuario:")
                target_user_id = st.text_input("ID de Usuario:", key="admin_target_id")
                target_plan = st.selectbox("Asignar Plan:", ["premium", "free", "admin"], key="admin_plan_select")
                
                if st.button("Actualizar Plan", key="btn_admin_update"):
                    if target_user_id:
                        ok_up, msg_up = db.activar_plan_premium(target_user_id, plan=target_plan)
                        if ok_up:
                            st.success(f"¡Plan actualizado a {target_plan}!")
                        else:
                            st.error(msg_up)
                    else:
                        st.warning("Ingresa un ID de usuario válido.")

    # ==============================================================================
    # HEADER PRINCIPAL Y PESTAÑAS DE TRABAJO
    # ==============================================================================
    st.markdown("""
        <div class="main-header">
            <h2>🦆 Workstation Clínico <span class="patu-badge">v3.0 PRO</span></h2>
            <p style="margin: 0; color: #555;">PATU — Psychologists United Across America</p>
        </div>
    """, unsafe_allow_html=True)

    # Verificación de límite antes de renderizar herramientas principales
    puedes_usar, msg_limite = db.verificar_limite_usuario(usuario_id, plan_usuario)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📑 Analizador Clínico", 
        "🔍 Buscador de Pruebas", 
        "📑 Generador de Informes", 
        "🗂️ Mi Historial"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: ANALIZADOR CLÍNICO
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("📋 Análisis Diagnóstico Inicial y Multiaxial")
        
        col_edad, col_etapa = st.columns([1, 2])
        with col_edad:
            edad = st.number_input("Edad del Paciente (años):", min_value=1, max_value=120, value=25)
        with col_etapa:
            etapa = "Adolescente" if edad < 18 else "Adulto"
            st.text_input("Etapa de Desarrollo:", value=etapa, disabled=True)

        narrativa = st.text_area("Narrativa o notas de la consulta inicial:", height=150,
                                 placeholder="Escribe o pega la sintomatología del paciente...")

        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔍 Analizar Caso y Brechas", use_container_width=True):
                if not puedes_usar:
                    mostrar_modulo_pago(usuario_id, email_usuario)
                elif not narrativa.strip():
                    st.warning("Por favor ingresa la narrativa del caso.")
                else:
                    # Lógica de análisis simulada / integración IA
                    res_analisis = f"**Análisis Clínico ({etapa}, {edad} años):**\n\nSintomatología reportada revisada. Se observan brechas en la evaluación del estado afectivo y psicosocial."
                    st.markdown(res_analisis)
                    
                    # Intentar guardar en historial
                    ok_g, msg_g = db.guardar_historial(usuario_id, "Análisis Clínico", f"Caso {edad} años - {etapa}", res_analisis, plan_usuario)
                    if ok_g:
                        st.success("Guardado en historial.")
                        st.rerun()
                    else:
                        st.error(msg_g)

        with col_btn2:
            if st.button("🧪 Sugerir Batería Psicométrica", use_container_width=True):
                if not puedes_usar:
                    mostrar_modulo_pago(usuario_id, email_usuario)
                elif not narrativa.strip():
                    st.warning("Por favor ingresa la narrativa del caso.")
                else:
                    res_bateria = f"### 🧪 Batería Psicométrica Recomendada (Rango: {edad} años / {etapa})\n\n1. **BDI-II** (Depresión de Beck)\n2. **BAI** (Ansiedad de Beck)\n3. **MINI / SCL-90-R** (Tamizaje Multiaxial)"
                    st.markdown(res_bateria)
                    
                    ok_g, msg_g = db.guardar_historial(usuario_id, "Batería Psicométrica", f"Batería {etapa}", res_bateria, plan_usuario)
                    if ok_g:
                        st.success("Guardado en historial.")
                        st.rerun()
                    else:
                        st.error(msg_g)

    # --------------------------------------------------------------------------
    # TAB 2: BUSCADOR DE PRUEBAS
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("🔍 Buscador de Pruebas Psicológicas")
        query_prueba = st.text_input("Buscar prueba por nombre o constructo (ej: Depresión, WAIS, MACI):")
        if st.button("Buscar Prueba"):
            st.info(f"Mostrando resultados para: '{query_prueba}'")

    # --------------------------------------------------------------------------
    # TAB 3: GENERADOR DE INFORMES
    # --------------------------------------------------------------------------
    with tab3:
        st.subheader("📑 Generador de Informes Psicológicos")
        st.write("Completa los datos para estructurar el borrador del informe clínico.")

    # --------------------------------------------------------------------------
    # TAB 4: MI HISTORIAL
    # --------------------------------------------------------------------------
    with tab4:
        st.subheader("🗂️ Mi Historial de Registros Guardados")
        registros = db.obtener_historial_usuario(usuario_id)
        if not registros:
            st.info("Aún no tienes registros guardados en tu historial.")
        else:
            for reg in registros:
                # reg: (id, tipo_registro, titulo, contenido, fecha)
                with st.expander(f"📌 {reg[1]} - {reg[2]} ({reg[4]})"):
                    st.markdown(reg[3])
