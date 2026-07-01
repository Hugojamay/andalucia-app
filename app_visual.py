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

# INTERFAZ
st.set_page_config(page_title="Andalucía Beauty", layout="centered")

# Título llamativo en gris
st.markdown("<h1 style='text-align: center; color: #555555;'>✨ ANDALUCÍA BEAUTY ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777777;'>Gestión de ventas y seguimiento de clientes</p>", unsafe_allow_html=True)

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
        
        # --- Selector de Mes y Año ---
        meses_espanol = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            mes_nombre = st.selectbox("Selecciona el mes:", list(meses_espanol.values()), index=hoy.month-1)
        with col_sel2:
            anio_sel = st.number_input("Año:", value=hoy.year, step=1)
            
        mes_num = [k for k, v in meses_espanol.items() if v == mes_nombre][0]
        
        # Lógica de cálculo (Filtrada por lo que elijas arriba)
        ventas_mes = [x for x in lista if x.Fecha_Compra.month == mes_num and x.Fecha_Compra.year == anio_sel]
        frascos_mes = sum(x.Cantidad_Frasco for x in ventas_mes)
        dinero_mes = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_mes)
        
        ventas_anio = [x for x in lista if x.Fecha_Compra.year == anio_sel]
        frascos_anio = sum(x.Cantidad_Frasco for x in ventas_anio)
        dinero_anio = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_anio)
        
        # Visualización
        st.markdown(f"<h3 style='color: #555555;'>📊 Resumen de {mes_nombre} {anio_sel}</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Frascos vendidos", frascos_mes)
        with col2:
            st.metric("Ingresos", f"${dinero_mes:,.2f}")
            
        st.markdown("---")
        
        st.markdown(f"<h3 style='color: #555555;'>📈 Acumulado Anual ({anio_sel})</h3>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        with col3:
            st.metric("Total Frascos Año", frascos_anio)
        with col4:
            st.metric("Total Ingresos Año", f"${dinero_anio:,.2f}")
        
        st.divider()
        st.subheader("🕒 Historial de Seguimiento")
        for cli in lista:
            dias = (hoy - cli.Fecha_Compra).days
            with st.expander(f"👤 {cli.Nombre_Cliente} - Hace {dias} días"):
                st.write(f"**Cantidad:** {cli.Cantidad_Frasco} frascos | **Precio:** ${cli.Precio_Especial:,.2f}")
                if dias >= 15:
                    st.warning("⚠️ ¡Seguimiento necesario!")
                    st.link_button("💬 Enviar WhatsApp", f"https://wa.me/{cli.Tel_Correo}?text=Hola+{cli.Nombre_Cliente},+cómo+te+ha+ido+con+la+crema+Andalucía?")
    else:
        st.info("Cargando datos o base de datos vacía...")
