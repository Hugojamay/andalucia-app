import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import requests

# ==========================================
# 1. CLASE CLIENTE (Mantiene tu lógica)
# ==========================================
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco, Fecha_Compra):
        self.Nombre_Cliente = Nombre_Cliente
        self.Tel_Correo = Tel_Correo
        self.Precio_Especial = float(Precio_Especial)
        self.Cantidad_Frasco = int(Cantidad_Frasco)
        try:
            self.Fecha_Compra = pd.to_datetime(Fecha_Compra)
        except:
            self.Fecha_Compra = datetime.now()

# ==========================================
# 2. FUNCIONES DE CONEXIÓN
# ==========================================
def cargar_clientes_nube():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqDrMcAlzp02km9pBIMls0I8OxKgRMySxN5GhbWgd08nj6sj5hn8BstFTti5go4g7T6x1NsHUUU_BE/pub?output=csv"
        df = pd.read_csv(url, keep_default_na=False)
        clientes = []
        for _, row in df.iterrows():
            if str(row.get('NOMBRE', '')).strip():
                clientes.append(Cliente(
                    row.get('NOMBRE'), row.get('TELEFONO'), 
                    row.get('PRECIO', 0), row.get('CANTIDAD', 1), 
                    row.get('FECHA', datetime.now())
                ))
        return clientes
    except: return []

# ==========================================
# 3. INTERFAZ Y LÓGICA DE NEGOCIO
# ==========================================
st.set_page_config(page_title="Andalucía Beauty", layout="centered")
st.header("ANDALUCÍA BEAUTY")

tab1, tab2 = st.tabs(["📝 Registrar", "📊 Reportes y Seguimiento"])

with tab1:
    with st.form("registro_form", clear_on_submit=True):
        n = st.text_input("Nombre:")
        t = st.text_input("Teléfono:")
        p = st.number_input("Precio:", value=435)
        c = st.number_input("Frascos:", value=1)
        if st.form_submit_button("Guardar"):
            st.success("Guardado")

with tab2:
    lista = cargar_clientes_nube()
    if lista:
        hoy = datetime.now()
        
        # --- CÁLCULOS MENSUALES Y ANUALES ---
        ventas_mes = [c for c in lista if c.Fecha_Compra.month == hoy.month and c.Fecha_Compra.year == hoy.year]
        ventas_anio = [c for c in lista if c.Fecha_Compra.year == hoy.year]
        
        st.subheader("📈 Reportes")
        col1, col2 = st.columns(2)
        col1.metric("Frascos (Mes)", sum(c.Cantidad_Frasco for c in ventas_mes))
        col2.metric("Frascos (Año)", sum(c.Cantidad_Frasco for c in ventas_anio))
        
        st.divider()
        st.subheader("🔔 Seguimiento (Aviso a los 15 días)")
        
        # --- LÓGICA DE SEGUIMIENTO ---
        for cli in lista:
            dias_pasados = (hoy - cli.Fecha_Compra).days
            # Si pasaron 15 días o más, mostramos aviso
            if dias_pasados >= 15:
                st.warning(f"¡Aviso! {cli.Nombre_Cliente} compró hace {dias_pasados} días.")
                link = f"https://wa.me/{cli.Tel_Correo}?text=Hola+{cli.Nombre_Cliente}%2C+¿cómo+va+tu+tratamiento+con+Andalucía+Beauty%3F"
                st.link_button("💬 WhatsApp", link)
            else:
                st.write(f"✅ {cli.Nombre_Cliente} (hace {dias_pasados} días)")
    else:
        st.info("Sin datos.")
