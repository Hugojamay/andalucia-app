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
# 2. CONEXIÓN A LA BASE DE DATOS (Lectura y Escritura Alternativa)
# =========================================================
def cargar_clientes_nube():
    try:
        url_base = st.secrets["connections"]["gsheets"]["spreadsheet"]
        if "/edit" in url_base:
            url_csv = url_base.split("/edit")[0] + "/gviz/tq?tqx=out:csv"
        else:
            url_csv = url_base

        df = pd.read_csv(url_csv)
        clientes = []
        
        for index, row in df.iterrows():
            if 'Nombre' in df.columns and pd.notna(row['Nombre']):
                c = Cliente(
                    Nombre_Cliente=row['Nombre'],
                    Tel_Correo=str(row['Telefono']),
                    Precio_Especial=int(row['Precio']) if 'Precio' in df.columns else 0,
                    Cantidad_Frasco=int(row['Cantidad']) if 'Cantidad' in df.columns else 1,
                    Fecha_Compra=row['Fecha'] if 'Fecha' in df.columns else None
                )
                clientes.append(c)
        return clientes
    except Exception as e:
        return []

def guardar_cliente_nube(nuevo_cliente):
    try:
        # Intentamos usar la URL del script de automatización si está configurado en Secrets
        if "script_url" in st.secrets["connections"]["gsheets"]:
            url_script = st.secrets["connections"]["gsheets"]["script_url"]
            datos = {
                "Nombre": nuevo_cliente.Nombre_Cliente,
                "Telefono": nuevo_cliente.Tel_Correo,
                "Precio": nuevo_cliente.Precio_Especial,
                "Cantidad": nuevo_cliente.Cantidad_Frasco,
                "Fecha": nuevo_cliente.Fecha_Compra.strftime("%Y-%m-%d %H:%M:%S")
            }
            response = requests.post(url_script, json=datos)
            return response.status_code == 200
        else:
            # Si no hay script, guardamos localmente en memoria de la sesión actual temporalmente
            if "backup_clientes" not in st.session_state:
                st.session_state.backup_clientes = []
            st.session_state.backup_clientes.append(nuevo_cliente)
            return True
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
            nuevo = Cliente(nombre, telefono, precio, quantity)
            exito = guardar_cliente_nube(nuevo)
            if exito:
                st.success(f"¡{nombre} registrado con éxito y listo para seguimiento!")
            else:
                st.warning(f"Guardado localmente. Falta vincular el canal de escritura.")
        else:
            st.error("Por favor, escribe el nombre y el teléfono.")

with pestaña2:
    st.header("Clientes en Seguimiento (Base de Datos)")
    
    mis_clientes = cargar_clientes_nube()
    
    # Combinamos datos remotos de Google Drive con los agregados temporalmente en la sesión
    if "backup_clientes" in st.session_state:
        mis_clientes.extend(st.session_state.backup_clientes)
    
    if len(mis_clientes) == 0:
        st.info("No hay clientes registrados todavía. Agrega uno en la pestaña anterior.")
    else:
        for cliente in mis_clientes:
            with st.container():
                st.write(f"### 👤 {cliente.Nombre_Cliente}")
                st.write(f"**Teléfono:** {cliente.Tel_Correo} | **Frascos:** {cliente.Cantidad_Frasco}")
                st.write(cliente.verificar_alerta_visual())
                
                link = cliente.generar_link_whatsapp()
                st.link_button("💬 Enviar WhatsApp de Seguimiento", link)
                st.divider()
