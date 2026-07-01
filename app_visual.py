import streamlit as st
import pandas as pd
from datetime import datetime

# Clase Cliente
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco, Fecha_Compra):
        self.Nombre_Cliente = str(Nombre_Cliente)
        self.Tel_Correo = str(Tel_Correo)
        # Manejo de seguridad para datos vacíos o formatos incorrectos
        self.Precio_Especial = float(Precio_Especial) if str(Precio_Especial).replace('.','',1).isdigit() else 0.0
        self.Cantidad_Frasco = int(float(Cantidad_Frasco)) if str(Cantidad_Frasco).replace('.','',1).isdigit() else 0
        try:
            self.Fecha_Compra = pd.to_datetime(Fecha_Compra)
        except:
            self.Fecha_Compra = datetime.now()

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
    except: 
        return []

# INTERFAZ
st.set_page_config(page_title="Andalucía Beauty", layout="centered")
st.title("ANDALUCÍA BEAUTY")

tab1, tab2 = st.tabs(["📝 Registrar Cliente", "📊 Reportes y Seguimiento"])

with tab1:
    with st.form("registro_form", clear_on_submit=True):
        st.text_input("Nombre:")
        st.text_input("Teléfono:")
        st.number_input("Precio ($):", value=435)
        st.number_input("Frascos:", value=1)
        if st.form_submit_button("Guardar"):
            st.success("Guardado")

with tab2:
    lista = cargar_clientes_nube()
    if lista:
        hoy = datetime.now()
        
        # CÁLCULOS HISTÓRICOS TOTALES
        frascos_totales = sum(x.Cantidad_Frasco for x in lista)
        dinero_total = sum(x.Cantidad_Frasco * x.Precio_Especial for x in lista)
        
        # CÁLCULOS ANUALES (Filtro por año actual)
        ventas_año = [x for x in lista if x.Fecha_Compra.year == hoy.year]
        frascos_anio = sum(x.Cantidad_Frasco for x in ventas_año)
        dinero_anio = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_año)
        
        # Mostrar métricas
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Frascos (Total)", frascos_totales)
            st.metric("Ingresos (Total)", f"${dinero_total:,.2f}")
        with col2:
            st.metric(f"Frascos {hoy.year}", frascos_anio)
            st.metric(f"Ingresos {hoy.year}", f"${dinero_anio:,.2f}")
        
        st.divider()
        st.subheader("Historial de Clientes")
        for cli in lista:
            dias = (hoy - cli.Fecha_Compra).days
            with st.expander(f"{cli.Nombre_Cliente} - Hace {dias} días ({cli.Fecha_Compra.strftime('%d/%m/%Y')})"):
                st.write(f"Cantidad: {cli.Cantidad_Frasco} frasco(s) | Precio: ${cli.Precio_Especial:,.2f}")
                if dias >= 15:
                    st.warning("¡Seguimiento necesario!")
                    st.link_button("💬 WhatsApp", f"https://wa.me/{cli.Tel_Correo}?text=Hola+{cli.Nombre_Cliente},+cómo+te+ha+ido+con+la+crema?")
    else:
        st.info("No se encontraron registros en la base de datos.")
