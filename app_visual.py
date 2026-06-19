import streamlit as st
from datetime import datetime
import urllib.parse
import pandas as pd
import requests

# ==========================================
# 1. TU CLASE CLIENTE (Sin cambios en lógica)
# ==========================================
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco, Fecha_Compra=None):
        self.Nombre_Cliente = Nombre_Cliente
        self.Tel_Correo = Tel_Correo
        self.Precio_Especial = Precio_Especial
        self.Cantidad_Frasco = Cantidad_Frasco
        
        if Fecha_Compra and Fecha_Compra != "":
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
@st.cache_data(ttl=60) # Añadimos caché para que refresque cada minuto
def cargar_clientes_nube():
    try:
        url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqDrMcAlzp02km9pBIMls0I8OxKgRMySxN5GhbWgd08nj6sj5hn8BstFTti5go4g7T6x1NsHUUU_BE/pub?output=csv"
        df = pd.read_csv(url_csv, keep_default_na=False)
        
        if df.empty:
            return []
            
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        clientes = []
        for index, row in df.iterrows():
            nombre_val = str(row.get('NOMBRE', '')).strip()
            if nombre_val == "" or nombre_val.upper() == "NOMBRE":
                continue
            
            # FIX: Capturamos la fecha como texto crudo, si viene vacía no forzamos 'hoy' aquí
            fecha_raw = str(row.get('FECHA', '')).strip()
            
            c = Cliente(
                Nombre_Cliente=nombre_val,
                Tel_Correo=str(row.get('TELEFONO', '')).strip(),
                Precio_Especial=int(float(row.get('PRECIO', 0) or 0)),
                Cantidad_Frasco=int(float(row.get('CANTIDAD', 1) or 1)),
                Fecha_Compra=fecha_raw 
            )
            clientes.append(c)
        return clientes
    except Exception as e:
        st.error(f"Error al conectar: {e}")
        return []

def registrar_cliente_script(nombre, telefono, precio, cantidad):
    try:
        url_script = st.secrets["connections"]["gsheets"]["spreadsheet"]
        payload = {"nombre": nombre, "telefono": telefono, "precio": precio, "cantidad": cantidad}
        response = requests.post(url_script, json=payload, timeout=10)
        return response.status_code == 200
    except:
        return False

# ==========================================
# 3. INTERFAZ VISUAL
# ==========================================
st.set_page_config(page_title="Andalucía Beauty - Control", page_icon="✨", layout="centered")

st.markdown("""
    <div style="background-color: #798670; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; font-family: 'Georgia', serif; font-size: 60px; margin: 0; font-weight: normal; border-bottom: 1px solid rgba(255,255,255,0.4); display: inline-block; padding-bottom: 5px; width: 80px;">A</h1>
        <h2 style="color: white; font-family: 'Arial', sans-serif; font-size: 24px; letter-spacing: 4px; margin-top: 15px; margin-bottom: 5px; font-weight: 300;">ANDALUCÍA BEAUTY</h2>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Registrar Cliente", "📊 Alertas y Seguimiento"])

with tab1:
    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("Nombre del Cliente:")
        telefono = st.text_input("Teléfono (ej. 52133xxxxxxxx):")
        precio = st.number_input("Precio ($):", min_value=0, value=435)
        cantidad = st.number_input("Frascos:", min_value=1, value=1)
        if st.form_submit_button("Guardar"):
            if nombre and telefono:
                if registrar_cliente_script(nombre, telefono, precio, cantidad):
                    st.success(f"¡{nombre} registrado!")
                else:
                    st.error("Error de conexión.")

with tab2:
    lista_clientes = cargar_clientes_nube()
    if not lista_clientes:
        st.info("Sin datos.")
    else:
        for cliente in lista_clientes:
            # Cálculo corregido
            dias_pasados = (datetime.now() - cliente.Fecha_Compra).days
            
            st.write(f"### 👤 {cliente.Nombre_Cliente}")
            if dias_pasados >= 25:
                st.error(f"🚨 URGENTE: {dias_pasados} días sin comprar.")
            elif dias_pasados >= 15:
                st.warning(f"⚠️ Seguimiento: {dias_pasados} días.")
            else:
                st.success(f"✅ Reciente: {dias_pasados} días.")
            
            st.write(f"**Fecha Compra:** {cliente.Fecha_Compra.strftime('%Y-%m-%d')}")
            texto_wa = f"Hola {cliente.Nombre_Cliente}, ¿cómo va tu tratamiento con Andalucía Beauty?"
            st.link_button("💬 WhatsApp", f"https://wa.me/{cliente.Tel_Correo}?text={urllib.parse.quote(texto_wa)}")
            st.divider()
