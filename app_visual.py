import streamlit as st
from datetime import datetime
import urllib.parse
import pandas as pd
import requests

# ==========================================
# 1. TU CLASE CLIENTE ORIGINAL
# ==========================================
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco, Fecha_Compra=None):
        self.Nombre_Cliente = Nombre_Cliente
        self.Tel_Correo = Tel_Correo
        self.Precio_Especial = Precio_Especial
        self.Cantidad_Frasco = Cantidad_Frasco
        
        if Fecha_Compra:
            if isinstance(Fecha_Compra, str):
                try:
                    fecha_limpia = Fecha_Compra.split(".")[0].strip()
                    self.Fecha_Compra = datetime.strptime(fecha_limpia, "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        self.Fecha_Compra = datetime.strptime(Fecha_Compra.split(" ")[0].strip(), "%Y-%m-%d")
                    except:
                        self.Fecha_Compra = datetime.now()
            else:
                self.Fecha_Compra = Fecha_Compra
        else:
            self.Fecha_Compra = datetime.now()

# ==========================================
# 2. FUNCIONES DE CONEXIÓN CORREGIDAS
# ==========================================
def cargar_clientes_nube():
    try:
        # Leemos el archivo usando la URL de exportación directa en formato CSV
        # Esto soluciona la pestaña de seguimiento sin usar la librería 'st-gsheets-connection'
        url_csv = "https://docs.google.com/spreadsheets/d/1aSRk8GJE5kOJKahGkqea0SHa1x-i61v3UCJV-YUkI-Y/gviz/tq?tqx=out:csv"
        df = pd.read_csv(url_csv, keep_default_na=False)
        clientes = []
        
        if not df.empty:
            # Forzamos que las columnas se lean limpias y en mayúsculas
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            if 'NOMBRE' in df.columns:
                for index, row in df.iterrows():
                    nombre_val = str(row['NOMBRE']).strip()
                    # Ignoramos filas vacías o renglones repetidos del encabezado
                    if nombre_val == "" or nombre_val.upper() == "NOMBRE":
                        continue
                    
                    tel_val = str(row['TELEFONO']).strip() if 'TELEFONO' in df.columns else ""
                    
                    try:
                        precio_val = int(float(str(row['PRECIO']))) if 'PRECIO' in df.columns and str(row['PRECIO']).strip() != "" else 0
                    except:
                        precio_val = 0
                        
                    try:
                        cantidad_val = int(float(str(row['CANTIDAD']))) if 'CANTIDAD' in df.columns and str(row['CANTIDAD']).strip() != "" else 1
                    except:
                        cantidad_val = 1
                        
                    fecha_val = str(row['FECHA']).strip() if 'FECHA' in df.columns else None
                    
                    c = Cliente(
                        Nombre_Cliente=nombre_val,
                        Tel_Correo=tel_val,
                        Precio_Especial=precio_val,
                        Cantidad_Frasco=cantidad_val,
                        Fecha_Compra=fecha_val
                    )
                    clientes.append(c)
        return clientes
    except Exception as e:
        # Si hay un error de lectura, mostramos un aviso discreto en la consola
        return []

def registrar_cliente_script(nombre, telefono, precio, cantidad):
    try:
        # Volvemos a jalar la URL exactamente como la tenías en tus Secrets originales
        url_script = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        payload = {
            "nombre": nombre,
            "telefono": telefono,
            "precio": precio,
            "cantidad": cantidad
        }
        
        response = requests.post(url_script, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

# ==========================================
# 3. INTERFAZ VISUAL DE STREAMLIT (Sintaxis limpia)
# ==========================================
st.set_page_config(page_title="Andalucía Beauty - Control", page_icon="✨", layout="centered")

# Tu Logo Verde Original
st.markdown("""
    <div style="background-color: #798670; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; font-family: 'Georgia', serif; font-size: 60px; margin: 0; font-weight: normal; border-bottom: 1px solid rgba(255,255,255,0.4); display: inline-block; padding-bottom: 5px; width: 80px;">A</h1>
        <h2 style="color: white; font-family: 'Arial', sans-serif; font-size: 24px; letter-spacing: 4px; margin-top: 15px; margin-bottom: 5px; font-weight: 300;">ANDALUCÍA BEAUTY</h2>
        <p style="color: #E2E8F0; font-style: italic; font-size: 14px; margin: 0;">Control de Clientes y Seguimiento de Alta Gama</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Registrar Cliente", "📊 Alertas y Seguimiento"])

with tab1:
    st.subheader("Nuevo Registro")
    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("Nombre del Cliente:")
        telefono = st.text_input("Teléfono (ej. 52133xxxxxxxx):")
        precio = st.number_input("Precio Especial ($):", min_value=0, value=435)
        cantidad = st.number_input("Cantidad de Frascos:", min_value=1, value=1)
        
        enviado = st.form_submit_button("Guardar Cliente")
        
        if enviado:
            if nombre and telefono:
                with st.spinner("Guardando registro..."):
                    exito = registrar_cliente_script(nombre, telefono, precio, cantidad)
                if exito:
                    st.success(f"¡{nombre} procesado con éxito!")
                    st.balloons()
                else:
                    st.error("Error al conectar con la base de datos de Google. Verifica tu Apps Script.")
            else:
                st.warning("Por favor, llena los campos obligatorios (Nombre y Teléfono).")

with tab2:
    st.subheader("Clientes en Seguimiento (Base de Datos)")
    
    lista_clientes = cargar_clientes_nube()
    
    if not lista_clientes:
        st.info("No hay clientes registrados todavía o la pestaña principal está vacía.")
    else:
        for cliente in lista_clientes:
            dias_pasados = (datetime.now() - cliente.Fecha_Compra).days
            
            if dias_pasados >= 25:
                st.error(f"🚨 **{cliente.Nombre_Cliente}** — ¡URGENTE! Hace {dias_pasados} días que no compra.")
            elif dias_pasados >= 15:
                st.warning(f"⚠️ **{cliente.Nombre_Cliente}** — Seguimiento Intermedio ({dias_pasados} días).")
            else:
                st.success(f"✅ **{cliente.Nombre_Cliente}** — Compra reciente hace {dias_pasados} días.")
            
            st.write(f"**Teléfono:** {cliente.Tel_Correo} | **Última Compra:** {cliente.Fecha_Compra.strftime('%Y-%m-%d')} | **Frascos:** {cliente.Cantidad_Frasco}")
            
            texto_wa = f"¡Hola {cliente.Nombre_Cliente}! Te saludamos de Andalucía Beauty. Esperamos que estés disfrutando los resultados de tu crema. Cuéntanos, ¿cómo va tu tratamiento?"
            texto_encoded = urllib.parse.quote(texto_wa)
            link_whatsapp = f"https://wa.me/{cliente.Tel_Correo}?text={texto_encoded}"
            
            st.link_button(f"💬 Contactar a {cliente.Nombre_Cliente} por WhatsApp", link_whatsapp)
            st.divider()
