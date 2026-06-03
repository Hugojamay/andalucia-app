import streamlit as st
from datetime import datetime
import urllib.parse
import pandas as pd
import requests

# =========================================================
# 1. TU CLASE CLIENTE
# =========================================================
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco, Fecha_Compra=None):
        self.Nombre_Cliente = Nombre_Cliente
        self.Tel_Correo = Tel_Correo
        self.Precio_Especial = Precio_Especial
        self.Cantidad_Frasco = Cantidad_Frasco
        
        if Fecha_Compra:
            if isinstance(Fecha_Compra, str):
                try:
                    self.Fecha_Compra = datetime.strptime(Fecha_Compra, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        self.Fecha_Compra = datetime.strptime(Fecha_Compra, "%Y-%m-%d")
                    except ValueError:
                        self.Fecha_Compra = datetime.now()
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
# 2. CONEXIÓN A LA BASE DE DATOS (Lectura y Escritura Activa)
# =========================================================
def cargar_clientes_nube():
    try:
        # Intentamos obtener la url desde secrets (Nube o local)
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            url_base = st.secrets["connections"]["gsheets"]["spreadsheet"]
        else:
            # Respaldo directo por si pruebas en localhost sin archivo local de secrets
            url_base = "https://docs.google.com/spreadsheets/d/1aSRk8GJE5kOJKahGkqea0SHa1x-i61v3UCJV-YUkI-Y/edit?usp=sharing"
            
        if "/edit" in url_base:
            url_csv = url_base.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
        else:
            url_csv = url_base

        df = pd.read_csv(url_csv)
        clientes = []
        
        # Mapeo flexible de columnas basado en tu imagen real de Drive
        col_nombre = 'NOMBRE' if 'NOMBRE' in df.columns else ('Nombre' if 'Nombre' in df.columns else None)
        col_telef  = 'TELEFONO' if 'TELEFONO' in df.columns else ('Telefono' if 'Telefono' in df.columns else None)
        col_precio = 'PRECIO' if 'PRECIO' in df.columns else ('Precio' if 'Precio' in df.columns else None)
        col_cant   = 'CANTIDAD' if 'CANTIDAD' in df.columns else ('Cantidad' if 'Cantidad' in df.columns else None)
        col_fecha  = 'FECHA' if 'FECHA' in df.columns else ('Fecha' if 'Fecha' in df.columns else None)
        
        if col_nombre:
            for index, row in df.iterrows():
                if pd.notna(row[col_nombre]) and str(row[col_nombre]).strip() != "":
                    c = Cliente(
                        Nombre_Cliente=row[col_nombre],
                        Tel_Correo=str(row[col_telef]) if col_telef else "",
                        Precio_Especial=int(row[col_precio]) if col_precio and pd.notna(row[col_precio]) else 0,
                        Cantidad_Frasco=int(row[col_cant]) if col_cant and pd.notna(row[col_cant]) else 1,
                        Fecha_Compra=row[col_fecha] if col_fecha and pd.notna(row[col_fecha]) else None
                    )
                    clientes.append(c)
        return clientes
    except Exception as e:
        return []

def guardar_cliente_nube(nuevo_cliente):
    try:
        # Intentamos jalar la URL del script de automatización
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"] and "script_url" in st.secrets["connections"]["gsheets"]:
            url_script = st.secrets["connections"]["gsheets"]["script_url"]
        else:
            # Respaldo para que funcione también en tu localhost si no tienes secrets local
            url_script = "https://script.google.com/macros/s/AKfycbkpz00uOvEAo_EK3jQy6lwzLh1dn6qDIYTywr7qbqxFwqwJWlXYKGVwraOBk57AalGUA/exec"
            
        datos = {
            "Nombre": nuevo_cliente.Nombre_Cliente,
            "Telefono": nuevo_cliente.Tel_Correo,
            "Precio": nuevo_cliente.Precio_Especial,
            "Cantidad": nuevo_cliente.Cantidad_Frasco,
            "Fecha": nuevo_cliente.Fecha_Compra.strftime("%Y-%m-%d %H:%M:%S")
        }
        response = requests.post(url_script, json=datos)
        return response.status_code == 200
    except Exception as e:
        return False


# =========================================================
# 3. INTERFAZ GRÁFICA (Andalucía Beauty)
# =========================================================
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

with pestaña1:
    st.header("Nuevo Registro")
    nombre = st.text_input("Nombre del Cliente:")
    telefono = st.text_input("Teléfono (ej. 52133xxxxxxx):")
    precio = st.number_input("Precio Especial ($):", min_value=0, value=0)
    cantidad = st.number_input("Cantidad de Frascos:", min_value=1, value=1)
    
    if st.button("Guardar Cliente"):
        if nombre and telefono:
            nuevo = Cliente(nombre, telefono, precio, cantidad)
            with st.spinner("Guardando en la base de datos de Google Drive..."):
                exito = guardar_cliente_nube(nuevo)
            if exito:
                st.success(f"¡{nombre} registrado con éxito en Google Drive!")
            else:
                st.error("Error de conexión. Revisa que el Apps Script de Google esté bien configurado.")
        else:
            st.error("Por favor, escribe el nombre y el teléfono.")

with pestaña2:
    st.header("Clientes en Seguimiento (Base de Datos)")
    
    with st.spinner("Cargando clientes en tiempo real desde Google Drive..."):
        mis_clientes = cargar_clientes_nube()
    
    if len(mis_clientes) == 0:
        st.info("No hay clientes registrados todavía en tu archivo de Excel o las columnas no coinciden.")
    else:
        for cliente in mis_clientes:
            with st.container():
                st.write(f"### 👤 {cliente.Nombre_Cliente}")
                st.write(f"**Teléfono:** {cliente.Tel_Correo} | **Frascos:** {cliente.Cantidad_Frasco} | **Precio:** ${cliente.Precio_Especial}")
                st.write(cliente.verificar_alerta_visual())
                
                link = cliente.generar_link_whatsapp()
                st.link_button(f"💬 Enviar WhatsApp a {cliente.Nombre_Cliente}", link)
                st.divider()
