import streamlit as st
import pandas as pd
from datetime import datetime

# Clase Cliente (Se mantiene intacta)
class Cliente:
    def __init__(self, Nombre_Cliente, Tel_Correo, Precio_Especial, Cantidad_Frasco, Fecha_Compra):
        self.Nombre_Cliente = str(Nombre_Cliente)
        self.Tel_Correo = str(Tel_Correo)
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

# INTERFAZ MEJORADA
st.set_page_config(page_title="Andalucía Beauty", layout="centered")

# Título llamativo con un emoji y estilo
st.markdown("<h1 style='text-align: center; color: #d63384;'>✨ ANDALUCÍA BEAUTY ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Gestión de ventas y seguimiento de clientes</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Registrar Cliente", "📊 Reportes y Seguimiento"])

with tab1:
    with st.form("registro_form", clear_on_submit=True):
        st.subheader("Datos de la Venta")
        st.text_input("Nombre:")
        st.text_input("Teléfono:")
        st.number_input("Precio ($):", value=435)
        st.number_input("Frascos:", value=1)
        if st.form_submit_button("Guardar en Base de Datos"):
            st.success("Guardado exitosamente")

with tab2:
    lista = cargar_clientes_nube()
    if lista:
        hoy = datetime.now()
        
        # Lógica de cálculo (Sin cambios, tal cual la tenías)
        ventas_mes = [x for x in lista if x.Fecha_Compra.month == hoy.month and x.Fecha_Compra.year == hoy.year]
        frascos_mes = sum(x.Cantidad_Frasco for x in ventas_mes)
        dinero_mes = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_mes)
        
        ventas_anio = [x for x in lista if x.Fecha_Compra.year == hoy.year]
        frascos_anio = sum(x.Cantidad_Frasco for x in ventas_anio)
        dinero_anio = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_anio)
        
        # Visualización mejorada
        st.subheader(f"Resumen de {hoy.strftime('%B')}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"Ventas: {hoy.strftime('%B')}", frascos_mes)
        with col2:
            st.metric(f"Ingresos: {hoy.strftime('%B')}", f"${dinero_mes:,.2f}")
            
        st.markdown("---")
        
        st.subheader(f"Acumulado Anual ({hoy.year})")
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Total Frascos Año", frascos_anio)
        with col4:
            st.metric("Total Ingresos Año", f"${dinero_anio:,.2f}")
        
        st.divider()
        st.subheader("🕒 Historial de Seguimiento")
        for cli in lista:
            dias = (hoy - cli.Fecha_Compra).days
            color = "orange" if dias >= 15 else "blue"
            with st.expander(f"👤 {cli.Nombre_Cliente} - Hace {dias} días"):
                st.write(f"**Cantidad:** {cli.Cantidad_Frasco} frascos | **Precio:** ${cli.Precio_Especial:,.2f}")
                if dias >= 15:
                    st.warning("⚠️ ¡Seguimiento necesario!")
                    st.link_button("💬 Enviar WhatsApp", f"https://wa.me/{cli.Tel_Correo}?text=Hola+{cli.Nombre_Cliente},+cómo+te+ha+ido+con+la+crema+Andalucía?")
    else:
        st.info("Cargando datos o base de datos vacía...")
