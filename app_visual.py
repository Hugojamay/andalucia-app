import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

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
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        # Cargamos desde tu pestaña exacta
        df = conn.read(worksheet="Respuestas de formulario 1")
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
    
    def_nombre, def_tel, def_precio, def_cant = "", "", 435.0, 1
    if seleccion:
        cli = mapa_clientes[seleccion]
        def_nombre, def_tel, def_precio = cli.Nombre_Cliente, cli.Tel_Correo, cli.Precio_Especial

    with st.form("registro_form", clear_on_submit=True):
        nombre = st.text_input("Nombre:", value=def_nombre)
        telefono = st.text_input("Teléfono:", value=def_tel)
        precio = st.number_input("Precio ($):", value=float(def_precio))
        cantidad = st.number_input("Frascos:", value=def_cant)
        
        if st.form_submit_button("Guardar en Base de Datos"):
            conn = st.connection("gsheets", type=GSheetsConnection)
            # Leer actual para anexar
            df_actual = conn.read(worksheet="Respuestas de formulario 1")
            nuevo_dato = pd.DataFrame([{
                "NOMBRE": nombre, 
                "TELEFONO": telefono, 
                "PRECIO": precio, 
                "CANTIDAD": cantidad, 
                "FECHA": datetime.now().strftime("%Y-%m-%d")
            }])
            df_actual = pd.concat([df_actual, nuevo_dato], ignore_index=True)
            conn.update(worksheet="Respuestas de formulario 1", data=df_actual)
            st.success("✅ Registro guardado con éxito")
            st.rerun()

with tab2:
    lista = lista_db
    if lista:
        hoy = datetime.now()
        meses_espanol = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            mes_nombre = st.selectbox("Selecciona el mes:", list(meses_espanol.values()), index=hoy.month-1)
        with col_sel2:
            anio_sel = st.number_input("Año:", value=hoy.year, step=1)
            
        mes_num = [k for k, v in meses_espanol.items() if v == mes_nombre][0]
        ventas_mes = [x for x in lista if x.Fecha_Compra.month == mes_num and x.Fecha_Compra.year == anio_sel]
        
        st.markdown(f"<h3 style='color: #555555;'>📊 Resumen de {mes_nombre} {anio_sel}</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Frascos", sum(x.Cantidad_Frasco for x in ventas_mes))
        col2.metric("Ingresos", f"${sum(x.Cantidad_Frasco * x.Precio_Especial for x in ventas_mes):,.2f}")
        
        st.divider()
        st.subheader("🔍 Buscar historial por cliente")
        nombres_unicos = sorted(list(set(x.Nombre_Cliente for x in lista)))
        cliente_buscado = st.selectbox("Selecciona un cliente para ver su historial específico:", [""] + nombres_unicos)
        if cliente_buscado:
            for cli in [x for x in lista if x.Nombre_Cliente == cliente_buscado]:
                st.write(f"📅 {cli.Fecha_Compra.strftime('%d/%m/%Y')} | 📦 {cli.Cantidad_Frasco} frascos | ${cli.Precio_Especial:,.2f}")
    else:
        st.info("Base de datos vacía o cargando...")
