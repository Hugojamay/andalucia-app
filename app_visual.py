import streamlit as st
from datetime import datetime
import urllib.parse
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 1. TU CLASE CLIENTE (Adaptada para leer fechas guardadas)
# =========================================================
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco, Fecha_Compra=None):
        self.Nombre_Cliente = Nombre_Cliente
        self.Tel_Correo = Tel_Correo
        self.Precio_Especial = Precio_Especial
        self.Cantidad_Frasco = Cantidad_Frasco
        
        # Si la fecha viene de la base de datos, la convertimos; si es nuevo, toma la fecha de hoy
        if Fecha_Compra:
            if isinstance(Fecha_Compra, str):
                self.Fecha_Compra = datetime.strptime(Fecha_Compra, "%Y-%m-%d %H:%M:%S")
            else:
                self.Fecha_Compra = Fecha_Compra
        else:
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
# 2. CONEXIÓN A LA BASE DE DATOS (Google Sheets)
# =========================================================
# Creamos la conexión con la hoja en la nube
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para leer los datos actuales de la nube
def cargar_clientes_nube():
    try:
        # Lee la hoja de cálculo
        df = conn.read(ttl="5s") # Se actualiza cada 5 segundos para ver cambios del otro celular
        clientes = []
        for index, row in df.iterrows():
            if pd.notna(row['Nombre']):
                c = Cliente(
                    Nombre_Cliente=row['Nombre'],
                    Tel_Correo=str(row['Telefono']),
                    Precio_Especial=int(row['Precio']),
                    Cantidad_Frasco=int(row['Cantidad']),
                    Fecha_Compra=row['Fecha']
                )
                clientes.append(c)
        return clientes
    except Exception:
        # Si la hoja está vacía al principio, regresa una lista vacía
        return []

# Función para guardar un nuevo cliente en la nube
def guardar_cliente_nube(nuevo_cliente):
    # 1. Traer los datos existentes para no borrarlos
    try:
        df_existente = conn.read()
    except Exception:
        df_existente = pd.DataFrame(columns=['Nombre', 'Telefono', 'Precio', 'Cantidad', 'Fecha'])
    
    # 2. Crear el nuevo renglón
    nuevo_renglon = pd.DataFrame([{
        'Nombre': nuevo_cliente.Nombre_Cliente,
        'Telefono': nuevo_cliente.Tel_Correo,
        'Precio': nuevo_cliente.Precio_Especial,
        'Cantidad': nuevo_cliente.Cantidad_Frasco,
        'Fecha': nuevo_cliente.Fecha_Compra.strftime("%Y-%m-%d %H:%M:%S")
    }])
    
    # 3. Juntar todo y subirlo de regreso a la nube
    df_final = pd.concat([df_existente, nuevo_renglon], ignore_index=True)
    conn.update(data=df_final)


# =========================================================
# 3. INTERFAZ GRÁFICA (Andalucía Beauty)
# =========================================================

# Contenedor estilizado elegante
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
            ">Control de Clientes y Seguimiento de Alta Gama</p>
        </div>
        """,
        unsafe_allow_html=True
    )

pestaña1, pestaña2 = st.tabs(["📝 Registrar Cliente", "📊 Alertas y Seguimiento"])

# --- PESTAÑA 1: FORMULARIO DE REGISTRO ---
with pestaña1:
    st.header("Nuevo Registro")
    
    nombre = st.text_input("Nombre del Cliente:")
    telefono = st.text_input("Teléfono (ej. 52133xxxxxxx):")
    precio = st.number_input("Precio Especial ($):", min_value=0, value=0)
    cantidad = st.number_input("Cantidad de Frascos:", min_value=1, value=1)
    
    if st.button("Guardar Cliente"):
        if nombre and telefono:
            with st.spinner("Guardando de forma segura en la nube..."):
                # Creamos el objeto cliente
                nuevo = Cliente(nombre, telefono, precio, cantidad)
                # Lo mandamos directo a Google Sheets
                guardar_cliente_nube(nuevo)
                st.success(f"¡{nombre} guardado en la base de datos con éxito!")
        else:
            st.error("Por favor, escribe el nombre y el teléfono.")

# --- PESTAÑA 2: LISTA DE SEGUIMIENTO ---
with pestaña2:
    st.header("Clientes en Seguimiento (Tiempo Real)")
    
    # Cargamos en tiempo real lo que esté guardado en la nube
    mis_clientes = cargar_clientes_nube()
    
    if len(mis_clientes) == 0:
        st.info("No hay clientes registrados todavía en la base de datos.")
    else:
        # Dibujamos las tarjetas visuales
        for cliente in mis_clientes:
            with st.container():
                st.write(f"### 👤 {cliente.Nombre_Cliente}")
                st.write(f"**Frascos:** {cliente.Cantidad_Frasco} | **Precio:** ${cliente.Precio_Especial}")
                st.write(cliente.verificar_alerta_visual())
                
                link = cliente.generar_link_whatsapp()
                st.link_button("💬 Enviar WhatsApp", link)
                st.divider()