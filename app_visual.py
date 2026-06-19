import streamlit as st
from datetime import datetime
import urllib.parse
import pandas as pd
import requests

# ... (Tu clase Cliente sigue igual) ...
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

# ... (Tus funciones cargar_clientes_nube y registrar_cliente_script siguen igual) ...
@st.cache_data(ttl=60)
def cargar_clientes_nube():
    try:
        url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqDrMcAlzp02km9pBIMls0I8OxKgRMySxN5GhbWgd08nj6sj5hn8BstFTti5go4g7T6x1NsHUUU_BE/pub?output=csv"
        df = pd.read_csv(url_csv, keep_default_na=False)
        if df.empty: return []
        df.columns = [str(c).strip().upper() for c in df.columns]
        clientes = []
        for index, row in df.iterrows():
            nombre_val = str(row.get('NOMBRE', '')).strip()
            if nombre_val == "" or nombre_val.upper() == "NOMBRE": continue
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
        st.error(f"Error: {e}"); return []

def registrar_cliente_script(nombre, telefono, precio, cantidad):
    try:
        url_script = st.secrets["connections"]["gsheets"]["spreadsheet"]
        payload = {"nombre": nombre, "telefono": telefono, "precio": precio, "cantidad": cantidad}
        response = requests.post(url_script, json=payload, timeout=10)
        return response.status_code == 200
    except: return False

# --- INTERFAZ ---
st.set_page_config(page_title="Andalucía Beauty", layout="centered")

st.markdown("""<div style="background-color: #798670; padding: 20px; border-radius: 10px; text-align: center; color: white;">
<h1>ANDALUCÍA BEAUTY</h1></div>""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Registrar Cliente", "📊 Reportes y Seguimiento"])

with tab1:
    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("Nombre:")
        telefono = st.text_input("Teléfono:")
        precio = st.number_input("Precio ($):", value=435)
        cantidad = st.number_input("Frascos:", value=1)
        if st.form_submit_button("Guardar"):
            if registrar_cliente_script(nombre, telefono, precio, cantidad):
                st.success("¡Guardado!")

with tab2:
    lista_clientes = cargar_clientes_nube()
    
    if lista_clientes:
        # --- NUEVA LÓGICA DE REPORTE ---
        hoy = datetime.now()
        ventas_mes = [c for c in lista_clientes if c.Fecha_Compra.month == hoy.month and c.Fecha_Compra.year == hoy.year]
        total_frascos = sum(c.Cantidad_Frasco for c in ventas_mes)
        total_dinero = sum(c.Precio_Especial * c.Cantidad_Frasco for c in ventas_mes)
        
        st.subheader(f"📈 Ventas de {hoy.strftime('%B %Y')}")
        c1, c2 = st.columns(2)
        c1.metric("Frascos", total_frascos)
        c2.metric("Ingresos", f"${total_dinero:,}")
        st.divider()
        # -------------------------------

        for cliente in lista_clientes:
            dias_pasados = (datetime.now() - cliente.Fecha_Compra).days
            st.write(f"### 👤 {cliente.Nombre_Cliente}")
            st.write(f"Hace {dias_pasados} días | **{cliente.Cantidad_Frasco} frascos**")
            link = f"https://wa.me/{cliente.Tel_Correo}?text=Hola+{cliente.Nombre_Cliente}%2C+¿cómo+va+tu+tratamiento+con+Andalucía+Beauty%3F"
            st.link_button("💬 WhatsApp", link)
            st.divider()
