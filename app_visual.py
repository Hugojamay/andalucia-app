import streamlit as st
from datetime import datetime
import urllib.parse
import pandas as pd
import requests

# ==========================================
# 1. TU CLASE CLIENTE
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
                    # Intenta limpiar formatos comunes de fecha
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
# 2. FUNCIONES DE CONEXIÓN (Carga de Datos)
# ==========================================
def cargar_clientes_nube():
    try:
        # Tu enlace directo de exportación CSV público
        url_csv = "https://docs.google.com/spreadsheets/d/1aSRk8GJE5kOJKahGkqea0SHa1x-i61v3UCJV-YUkI-Y/export?format=csv&gid=0"
        
        # Leemos los datos directamente de la nube de Google
        df = pd.read_csv(url_csv, keep_default_na=False)
        clientes = []
        
        if not df.empty:
            # Forzamos que los nombres de las columnas estén en mayúsculas y sin espacios
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            if 'NOMBRE' in df.columns:
                for index, row in df.iterrows():
                    nombre_val = str(row['NOMBRE']).strip()
                    if nombre_val == "" or nombre_val.upper() == "NOMBRE":
                        continue
                    
                    # Extraer Teléfono
                    tel_val = str(row['TELEFONO']).strip() if 'TELEFONO' in df.columns else ""
                    
                    # Extraer Precio
                    try:
                        precio_val = int(float(str(row['PRECIO']))) if 'PRECIO' in df.columns and str(row['PRECIO']).strip() != "" else 0
                    except:
                        precio_val = 0
                        
                    # Extraer Cantidad
                    try:
                        cantidad_val = int(float(str(row['CANTIDAD']))) if 'CANTIDAD' in df.columns and str(row['CANTIDAD']).strip() != "" else 1
                    except:
                        cantidad_val = 1
                        
                    # Extraer Fecha (Si no existe en el Excel, le asigna la de hoy automáticamente)
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
        return []

def registrar_cliente_script(nombre, telefono, precio, cantidad):
    # URL de tu macro de Google Apps Script para guardar datos
    url_script = "https://script.google.com/macros/s/AKfycbz24tc1IlClP9Nasm_e0gO9E_c0PvqgsSM1kjqlqbAH1LOus76PA3uPqRQwgQszELrUC/exec"
    payload = {
        "nombre": nombre,
        "telefono": telefono,
        "precio": precio,
        "cantidad": cantidad
    }
    try:
        response = requests.post(url_script, json=payload)
        return response.status_code == 200
    except:
        return False

# ==========================================
# 3. INTERFAZ VISUAL DE STREAMLIT
# ==========================================
st.set_page_config(page_title="Andalucía Beauty - Control", page_icon="✨", layout="centered")

# Encabezado Bonito
st.markdown("<h1 style='text-align: center; color: #4A5D4E;'>A</h1>", unsafe_allowed_html=True)
st.markdown("<h2 style='text-align: center; font-weight: 300; letter-spacing: 3px;'>ANDALUCÍA BEAUTY</h2>", unsafe_allowed_html=True)
st.markdown("<p style='text-align: center; font-style: italic; color: gray;'>Control de Clientes y Seguimiento de Alta Gama</p>", unsafe_allowed_html=True)

# Pestañas
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
    
    # Cargamos en tiempo real desde la URL pública
    lista_clientes = cargar_clientes_nube()
    
    if not lista_clientes:
        st.info("No hay clientes registrados todavía o conectando de forma directa...")
    else:
        for cliente in lista_clientes:
            dias_pasados = (datetime.now() - cliente.Fecha_Compra).days
            
            # Formatos de alerta según los días
            if dias_pasados >= 25:
                alerta_texto = f"🚨 **¡URGENTE! Hace {dias_pasados} días que no compra.** Reabastecimiento necesario."
                color_borde = "#FFD2D2"
            elif dias_pasados >= 15:
                alerta_texto = f"⚠️ **Seguimiento Intermedio ({dias_pasados} días).** Preguntar cómo va con su crema."
                color_borde = "#FFEAA7"
            else:
                alerta_texto = f"✅ **Compra reciente hace {dias_pasados} días.** Cliente al corriente."
                color_borde = "#D4EDDA"
            
            # Tarjeta visual para el cliente
            st.markdown(f"""
            <div style="border: 1px solid #DDD; background-color: {color_borde}; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <h4 style="margin:0; color: #333;">{cliente.Nombre_Cliente}</h4>
                <p style="margin:5px 0; color: #555;"><b>Teléfono:</b> {cliente.Tel_Correo} | <b>Última Compra:</b> {cliente.Fecha_Compra.strftime('%Y-%m-%d')} | <b>Frascos:</b> {cliente.Cantidad_Frasco}</p>
                <p style="margin:0; font-size: 14px;">{alerta_texto}</p>
            </div>
            """, unsafe_allowed_html=True)
            
            # Mensaje personalizado de WhatsApp
            texto_wa = f"¡Hola {cliente.Nombre_Cliente}! Te saludamos de Andalucía Beauty. Esperamos que estés disfrutando los resultados de tu crema. Cuéntanos, ¿cómo va tu tratamiento?"
            texto_encoded = urllib.parse.quote(texto_wa)
            link_whatsapp = f"https://wa.me/{cliente.Tel_Correo}?text={texto_encoded}"
            
            st.navigator = st.link_button(f"💬 Contactar a {cliente.Nombre_Cliente} por WhatsApp", link_whatsapp)
