import streamlit as st
import pandas as pd
from datetime import datetime

# Clase Cliente
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

st.markdown("<h1 style='text-align: center; color: #555555;'>✨ ANDALUCÍA BEAUTY ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777777;'>Gestión de ventas y seguimiento de clientes</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Registrar Cliente", "📊 Reportes y Seguimiento"])

with tab1:
    lista_db = cargar_clientes_nube()
    mapa_clientes = {cli.Nombre_Cliente: cli for cli in lista_db}
    nombres_ordenados = sorted(list(mapa_clientes.keys()))

    st.subheader("Datos de la Venta")
    
    seleccion = st.selectbox("¿Cliente frecuente? (Selecciona para autocompletar)", [""] + nombres_ordenados)
    
    if seleccion:
        cli = mapa_clientes[seleccion]
        st.session_state.nombre_val = cli.Nombre_Cliente
        st.session_state.tel_val = cli.Tel_Correo
        st.session_state.precio_val = cli.Precio_Especial
    else:
        # Valores por defecto si no hay selección
        if "nombre_val" not in st.session_state: st.session_state.nombre_val = ""
        if "tel_val" not in st.session_state: st.session_state.tel_val = ""
        if "precio_val" not in st.session_state: st.session_state.precio_val = 435.0
        if "cant_val" not in st.session_state: st.session_state.cant_val = 1

    with st.form("registro_form", clear_on_submit=False):
        st.text_input("Nombre:", key="nombre_val")
        st.text_input("Teléfono:", key="tel_val")
        st.number_input("Precio ($):", key="precio_val")
        st.number_input("Frascos:", value=1, key="cant_val")
        
        if st.form_submit_button("Guardar en Base de Datos"):
            # URL generada con tus IDs reales
            url_base = "https://docs.google.com/forms/d/e/1FAIpQLSeNrfgmi0FDk1Y9IeuhOnwP-pzDXjX7SMieZeZr6ajjlQLLow/viewform?usp=pp_url"
            link = (f"{url_base}"
                    f"&entry.295001426={st.session_state.nombre_val}"
                    f"&entry.1284683403={st.session_state.tel_val}"
                    f"&entry.1564218932={st.session_state.precio_val}"
                    f"&entry.962058671={st.session_state.cant_val}")
            
            st.markdown(f'<a href="{link}" target="_blank" style="padding: 10px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">✅ Clic aquí para confirmar registro</a>', unsafe_allow_html=True)

with tab2:
    lista = lista_db
    if lista:
        hoy = datetime.now()
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
        
        ventas_mes = [x for x in lista if x.Fecha_Compra.month == mes_num and x.Fecha_Compra.year == anio_sel]
        frascos_mes = sum(x.Cantidad_Frasco for x in ventas_mes)
        dinero_mes = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_mes)
        
        ventas_anio = [x for x in lista if x.Fecha_Compra.year == anio_sel]
        frascos_anio = sum(x.Cantidad_Frasco for x in ventas_anio)
        dinero_anio = sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_anio)
        
        st.markdown(f"<h3 style='color: #555555;'>📊 Resumen de {mes_nombre} {anio_sel}</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Frascos vendidos", frascos_mes)
        col2.metric("Ingresos", f"${dinero_mes:,.2f}")
            
        st.markdown("---")
        st.markdown(f"<h3 style='color: #555555;'>📈 Acumulado Anual ({anio_sel})</h3>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)
        col3.metric("Total Frascos Año", frascos_anio)
        col4.metric("Total Ingresos Año", f"${dinero_anio:,.2f}")
        
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
