import streamlit as st
from datetime import datetime
import pandas as pd
import requests

# ==========================================
# 1. CLASE CLIENTE
# ==========================================
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco, Fecha_Compra=None):
        self.Nombre_Cliente = Nombre_Cliente
        self.Tel_Correo = Tel_Correo
        self.Precio_Especial = Precio_Especial
        self.Cantidad_Frasco = Cantidad_Frasco
        
        # Validación de fecha robusta
        if Fecha_Compra and str(Fecha_Compra).strip():
            try:
                self.Fecha_Compra = pd.to_datetime(Fecha_Compra)
            except:
                self.Fecha_Compra = datetime.now()
        else:
            self.Fecha_Compra = datetime.now()

# ==========================================
# 2. FUNCIONES DE CONEXIÓN
# ==========================================
# Usamos un cache más simple para evitar problemas de serialización
@st.cache_data(ttl=60)
def cargar_clientes_nube():
    try:
        url_csv = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqDrMcAlzp02km9pBIMls0I8OxKgRMySxN5GhbWgd08nj6sj5hn8BstFTti5go4g7T6x1NsHUUU_BE/pub?output=csv"
        df = pd.read_csv(url_csv, keep_default_na=False)
        if df.empty: return []
        
        # Convertir a lista de diccionarios primero para evitar errores de serialización de objetos
        data = df.to_dict('records')
        clientes = []
        for row in data:
            nombre = str(row.get('NOMBRE', '')).strip()
            if not nombre or nombre.upper() == "NOMBRE": continue
            
            clientes.append(Cliente(
                Nombre_Cliente=nombre,
                Tel_Correo=str(row.get('TELEFONO', '')).strip(),
                Precio_Especial=float(row.get('PRECIO', 0) or 0),
                Cantidad_Frasco=float(row.get('CANTIDAD', 1) or 1),
                Fecha_Compra=row.get('FECHA', '')
            ))
        return clientes
    except:
        return []

def registrar_cliente_script(nombre, telefono, precio, cantidad):
    try:
        url_script = st.secrets["connections"]["gsheets"]["spreadsheet"]
        response = requests.post(url_script, json={"nombre": nombre, "telefono": telefono, "precio": precio, "cantidad": cantidad}, timeout=10)
        return response.status_code == 200
    except: return False

# ==========================================
# 3. INTERFAZ
# ==========================================
st.set_page_config(page_title="Andalucía Beauty", layout="centered")

# Encabezado corregido para evitar errores de renderizado
st.markdown("""<div style="background-color: #798670; padding: 20px; border-radius: 10px; text-align: center; color: white;">
<h1>ANDALUCÍA BEAUTY</h1></div>""", unsafe_html=True)

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
        hoy = datetime.now()
        
        # Filtros con manejo de seguridad
        ventas_mes = [c for c in lista_clientes if c.Fecha_Compra.month == hoy.month and c.Fecha_Compra.year == hoy.year]
        total_frascos = sum(c.Cantidad_Frasco for c in ventas_mes)
        total_dinero = sum(c.Precio_Especial * c.Cantidad_Frasco for c in ventas_mes)
        
        st.subheader(f"📈 Ventas Mensuales")
        c1, c2 = st.columns(2)
        c1.metric("Frascos", int(total_frascos))
        c2.metric("Ingresos", f"${total_dinero:,.2f}")
        
        st.divider()

        for cliente in lista_clientes:
            dias = (datetime.now() - cliente.Fecha_Compra).days
            st.write(f"### 👤 {cliente.Nombre_Cliente}")
            st.write(f"Hace {max(0, dias)} días | **{int(cliente.Cantidad_Frasco)} frascos**")
            link = f"https://wa.me/{cliente.Tel_Correo}?text=Hola+{cliente.Nombre_Cliente}%2C+¿cómo+va+tu+tratamiento+con+Andalucía+Beauty%3F"
            st.link_button("💬 WhatsApp", link)
            st.divider()
    else:
        st.info("No se pudieron cargar los datos o la lista está vacía.")
