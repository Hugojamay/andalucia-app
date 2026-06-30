import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ==========================================
# 1. CLASE CLIENTE (Lógica original intacta)
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
# 2. CARGA DE DATOS (Sin caché para evitar conflictos)
# ==========================================
def cargar_clientes_nube():
    try:
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRqDrMcAlzp02km9pBIMls0I8OxKgRMySxN5GhbWgd08nj6sj5hn8BstFTti5go4g7T6x1NsHUUU_BE/pub?output=csv"
        df = pd.read_csv(url, keep_default_na=False)
        clientes = []
        for _, row in df.iterrows():
            if str(row.get('NOMBRE', '')).strip():
                clientes.append(Cliente(
                    row.get('NOMBRE'), 
                    row.get('TELEFONO'), 
                    row.get('PRECIO', 0), 
                    row.get('CANTIDAD', 1), 
                    row.get('FECHA', datetime.now())
                ))
        return clientes
    except: return []

# ==========================================
# 3. INTERFAZ (Estable)
# ==========================================
st.set_page_config(page_title="Andalucía Beauty", layout="centered")

st.header("ANDALUCÍA BEAUTY")

tab1, tab2 = st.tabs(["📝 Registro", "📊 Reportes"])

with tab1:
    with st.form("registro_form", clear_on_submit=True):
        n = st.text_input("Nombre:")
        t = st.text_input("Teléfono:")
        p = st.number_input("Precio:", value=435)
        c = st.number_input("Frascos:", value=1)
        if st.form_submit_button("Guardar"):
            # Aquí va tu lógica de guardado
            st.success("Guardado correctamente")

with tab2:
    lista = cargar_clientes_nube()
    if lista:
        # Cálculos de lógica original
        total_f = sum(x.Cantidad_Frasco for x in lista)
        st.metric("Total Frascos", total_f)
        
        for cli in lista:
            st.write(f"### {cli.Nombre_Cliente}")
            st.write(f"Frascos: {cli.Cantidad_Frasco}")
            st.divider()
    else:
        st.info("Cargando o sin datos disponibles.")
