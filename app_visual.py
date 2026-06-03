import streamlit as st
from datetime import datetime
import urllib.parse

# =========================================================
# 1. TU CLASE CLIENTE (Lógica de negocio ya integrada)
# =========================================================
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco):
        self.Nombre_Cliente = Nombre_Cliente
        self.Tel_Correo = Tel_Correo
        self.Precio_Especial = Precio_Especial
        self.Cantidad_Frasco = Cantidad_Frasco
        self.Fecha_Compra = datetime.now()
        
    def verificar_alerta_visual(self):
        fecha_actual = datetime.now()
        diferencia = fecha_actual - self.Fecha_Compra
        dias_pasados = diferencia.days
        if dias_pasados >= 15:
            return f"⚠️ ¡ALERTA! Venta hace {dias_pasados} días. Toca seguimiento."
        else:
            return f"✅ Al corriente. Compró hace {dias_pasados} días. (Faltan {15 - dias_pasados} días)."

    def generar_link_whatsapp(self):
        mensaje = (
            f"Hola, {self.Nombre_Cliente}! ✨ Espero que te encuentres de maravilla. ❤️ "
            f"Te escribo para darte seguimiento a tu tratamiento de nuestra crema facial Beauty Andalucia. "
            f"¿Cómo te has sentido? ¿Cómo va tu rostro hermoso? ¡Un abrazo!"
        )
        mensaje_codificado = urllib.parse.quote(mensaje)
        return f"https://wa.me/{self.Tel_Correo}?text={mensaje_codificado}"


# =========================================================
# 2. MEMORIA DE LA APP (Para que no se borren al hacer clic)
# =========================================================
if "mis_clientes" not in st.session_state:
    st.session_state.mis_clientes = []


# =========================================================
# 3. INTERFAZ GRÁFICA (Diseño de Alta Gama para Andalucía Beauty)
# =========================================================

# Contenedor estilizado que simula el branding físico con código CSS de alta calidad
with st.container():
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #8F9779 0%, #6E755E 100%);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        ">
            <h1 style="
                color: #FFFFFF;
                font-family: 'Playfair Display', 'Didot', 'Georgia', serif;
                font-size: 3.2rem;
                font-weight: 300;
                letter-spacing: 5px;
                margin: 0;
                padding-bottom: 5px;
            ">A</h1>
            <div style="
                width: 40px;
                height: 1px;
                background-color: rgba(255,255,255,0.4);
                margin: 10px auto;
            "></div>
            <h2 style="
                color: #F5F5F0;
                font-family: 'Montserrat', 'Helvetica', sans-serif;
                font-size: 1.6rem;
                font-weight: 400;
                letter-spacing: 7px;
                margin: 5px 0 0 0;
                text-transform: uppercase;
            ">Andalucía Beauty</h2>
            <p style="
                color: #E2E4DC;
                font-family: sans-serif;
                font-size: 0.9rem;
                font-style: italic;
                margin-top: 10px;
                margin-bottom: 0;
                opacity: 0.8;
            ">Control de Clientes y Seguimiento</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Creamos dos pestañas para que la app se vea ordenada
pestaña1, pestaña2 = st.tabs(["📝 Registrar Cliente", "📊 Alertas y Seguimiento"])

# --- PESTAÑA 1: FORMULARIO DE REGISTRO ---
with pestaña1:
    st.header("Nuevo Registro")
    
    # Creamos las cajas de texto y números en la pantalla
    nombre = st.text_input("Nombre del Cliente:")
    telefono = st.text_input("Teléfono (ej. 52133xxxxxxx):")
    precio = st.number_input("Precio Especial ($):", min_value=0, value=0)
    cantidad = st.number_input("Cantidad de Frascos:", min_value=1, value=1)
    
    # Botón para guardar
    if st.button("Guardar Cliente"):
        if nombre and telefono:
            # Creamos el cliente y lo metemos a la lista de memoria
            nuevo = Cliente(nombre, telefono, precio, cantidad)
            st.session_state.mis_clientes.append(nuevo)
            st.success(f"¡{nombre} registrado con éxito!")
        else:
            st.error("Por favor, escribe el nombre y el teléfono.")

# --- PESTAÑA 2: LISTA DE SEGUIMIENTO ---
with pestaña2:
    st.header("Clientes en Seguimiento")
    
    if len(st.session_state.mis_clientes) == 0:
        st.info("No hay clientes registrados todavía.")
    else:
        # Dibujamos una tarjeta visual por cada cliente en la lista
        for cliente in st.session_state.mis_clientes:
            with st.container():
                st.write(f"### 👤 {cliente.Nombre_Cliente}")
                st.write(f"**Frascos:** {cliente.Cantidad_Frasco} | **Precio:** ${cliente.Precio_Especial}")
                
                # Muestra si está al corriente o en alerta
                st.write(cliente.verificar_alerta_visual())
                
                # Crea el botón azul de internet que abre su WhatsApp directo
                link = cliente.generar_link_whatsapp()
                st.link_button("💬 Enviar WhatsApp", link)
                # se corre con streamlit run app_visual.py
                st.divider() # Línea para separar un cliente de otro