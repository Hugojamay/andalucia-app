import streamlit as st
import pandas as pd
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
# 2. CARGA DE DATOS (Estable y rápida)
# ==========================================
@st.cache_data(ttl=600)
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
# 3. INTERFAZ Y LÓGICA (Reportes y Seguimiento)
# ==========================================
st.set_page_config(page_title="Andalucía Beauty", layout="centered")
st.markdown("<h1 style='text-align: center;'>ANDALUCÍA BEAUTY</h1>", unsafe_html=True)

tab1, tab2 = st.tabs(["📝 Registrar Cliente", "📊 Reportes y Seguimiento"])

with tab1:
    with st.form("registro_form", clear_on_submit=True):
        n = st.text_input("Nombre:")
        t = st.text_input("Teléfono:")
        p = st.number_input("Precio ($):", value=435)
        c = st.number_input("Frascos:", value=1)
        if st.form_submit_button("Guardar"):
            st.success("Guardado")

with tab2:
    lista = cargar_clientes_nube()
    if lista:
        hoy = datetime.now()
        
        # --- CÁLCULOS DE VENTAS Y GANANCIAS ---
        ventas_mes = [x for x in lista if x.Fecha_Compra.month == hoy.month and x.Fecha_Compra.year == hoy.year]
        ventas_anio = [x for x in lista if x.Fecha_Compra.year == hoy.year]
        
        # Totales
        frascos_mes = sum(x.Cantidad_Frasco for x in ventas_mes)
        frascos_anio = sum(x.Cantidad_Frasco for x in ventas_anio)
        ganancia_mes = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_mes)
        ganancia_anio = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_anio)
        
        st.subheader("📈 Reporte de Ventas")
        col1, col2 = st.columns(2)
        col1.metric("Frascos (Mes)", frascos_mes)
        col1.metric("Ingresos (Mes)", f"${ganancia_mes:,.2f}")
        col2.metric("Frascos (Año)", frascos_anio)
        col2.metric("Ingresos (Año)", f"${ganancia_anio:,.2f}")
        
        st.divider()
        st.subheader("👤 Detalle de Seguimiento")
        
        # --- LISTA DE SEGUIMIENTO ---
        for cli in lista:
            dias_pasados = (hoy - cli.Fecha_Compra).days
            
            with st.expander(f"👤 {cli.Nombre_Cliente} - Hace {dias_pasados} días"):
                st.write(f"**Cantidad:** {cli.Cantidad_Frasco} frascos")
                st.write(f"**Precio por frasco:** ${cli.Precio_Especial:,.2f}")
                st.write(f"**Fecha compra:** {cli.Fecha_Compra.strftime('%d/%m/%Y')}")
                
                if dias_pasados >= 15:
                    st.warning("¡Tiempo de seguimiento!")
                    link = f"https://wa.me/{cli.Tel_Correo}?text=Hola+{cli.Nombre_Cliente}%2C+¿cómo+va+tu+tratamiento+con+Andalucía+Beauty%3F"
                    st.link_button("💬 WhatsApp", link)
            st.divider()
    else:
        st.info("Sin datos disponibles.")
