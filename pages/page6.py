import os
import time
from datetime import datetime
from io import BytesIO
import streamlit as st
from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.libro_compra_venta import LibroCompraVenta
from scripts.empresa import ClsEmpresa
from scripts.cxc import CXC

st.set_page_config(page_title='Tributario', 
                   layout='wide', 
                   page_icon='⚡')

make_sidebar()
base_de_datos = os.getenv('DB_NAME_PROFIT_DOEL') if ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=base_de_datos)

if st.button("🔄 Refrescar"):
    st.cache_data.clear()

@st.cache_data
def libro_ventas(fecha_d, fecha_h):
    return LibroCompraVenta(conexion).libro_ventas(fecha_d=fecha_d, fecha_h=fecha_h)

@st.cache_data
def libro_compras(fecha_d, fecha_h):
    return LibroCompraVenta(conexion).libro_compras(fecha_d=fecha_d, fecha_h=fecha_h)

st.subheader("Libro de Ventas")
with st.expander("mostrar"):
    col1, col2 = st.columns(2, 
                            gap="small")
    with col1:
        #Fecha actual
        now = datetime.now()
        mes, year = now.month, now.year
        current_fecha_ini = datetime(year, mes, 1, 0, 00, 00, 00000)
        fecha_ini = st.date_input("fecha inicial", value=current_fecha_ini).strftime('%Y%m%d %H:%M:%S') # Convierte la fecha a YYYYMMDD
    with col2:
        fecha_fin = st.date_input("fecha final").strftime('%Y%m%d 23:59:59') # Convierte la fecha a YYYYMMDD

    libro_ventas = libro_ventas(fecha_d=fecha_ini, fecha_h=fecha_fin)
    if libro_ventas is not None:
        libro_ventas.style.format("{:,.2f}")
        st.dataframe(libro_ventas,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                                    "co_cli": st.column_config.TextColumn(
                                    "cod. cliente",
                                    ),
                                    "r": st.column_config.TextColumn(
                                    "RIF",
                                    ),
                                    "tipo_doc": st.column_config.TextColumn(
                                    "tipo doc",
                                    ),
                                    "r": st.column_config.TextColumn(
                                    "RIF",
                                    ),
                                    "num_comprobante": st.column_config.TextColumn(
                                    "número de comprobante",
                                    ),
                                    "nro_orig": st.column_config.TextColumn(
                                    "numero doc",
                                    ),    
                                    "tipo_imp": st.column_config.TextColumn(
                                    "tipo impuesto",
                                    ),
                                    "cli_des": st.column_config.TextColumn(
                                    "nombre o razón Social",
                                    ),
                                    "tasa": st.column_config.NumberColumn(
                                    "% alic.",
                                    default=0,
                                    format='%.1f %%',
                                    help="Monto objeto de impuesto",
                                    ),
                                    "base_imp_bs": st.column_config.NumberColumn(
                                    "base imponible",
                                    default=0,
                                    help="Monto objeto de impuesto",
                                    ),
                                    "ventas_exentas_bs": st.column_config.NumberColumn(
                                    "ventas exentas",
                                    default=0,
                                    ),
                                    "total_neto_bs": st.column_config.NumberColumn(
                                    "total ventas",
                                    default=0,
                                    ),
                                    "monto_imp_bs": st.column_config.NumberColumn(
                                    "impuesto I.V.A.",
                                    default=0,
                                    ),
                                    "monto_ret_imp_bs": st.column_config.NumberColumn(
                                    "total ret. I.V.A.",
                                    default=0,
                                    )})
        libro_ventas.to_excel(buf := BytesIO())
        st.download_button(
            'Descargar',
            buf.getvalue(),
            f'Libro de Ventas {ClsEmpresa.modulo_seleccionado()}.xlsx',
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
    

st.subheader("Libro de Compras")
with st.expander("mostrar"):
    col1, col2 = st.columns(2, 
                            gap="small")
    with col1:
        #Fecha actual
        now = datetime.now()
        mes, year = now.month, now.year
        current_fecha_ini = datetime(year, mes, 1, 0, 00, 00, 00000)
        fecha_ini = st.date_input("fecha inicial2", value=current_fecha_ini).strftime('%Y%m%d %H:%M:%S') # Convierte la fecha a YYYYMMDD
    with col2:
        fecha_fin = st.date_input("fecha final2").strftime('%Y%m%d 23:59:59') # Convierte la fecha a YYYYMMDD

    libro_compras = libro_compras(fecha_d=fecha_ini, fecha_h=fecha_fin)
    if libro_compras is not None:
        libro_compras.style.format("{:,.2f}")
        st.dataframe(libro_compras,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                                    "co_cli": st.column_config.TextColumn(
                                    "cod. cliente",
                                    ),
                                    "r": st.column_config.TextColumn(
                                    "RIF",
                                    ),
                                    "tipo_doc": st.column_config.TextColumn(
                                    "tipo doc",
                                    ),
                                    "r": st.column_config.TextColumn(
                                    "RIF",
                                    ),
                                    "num_comprobante": st.column_config.TextColumn(
                                    "número de comprobante",
                                    ),
                                    "nro_fact": st.column_config.TextColumn(
                                    "numero doc",
                                    ),
                                    "tipo_imp": st.column_config.TextColumn(
                                    "tipo impuesto",
                                    ),
                                    "cli_des": st.column_config.TextColumn(
                                    "nombre o razón Social",
                                    ),
                                    "tasa": st.column_config.NumberColumn(
                                    "% alic.",
                                    default=0,
                                    format='%.1f %%',
                                    help="Monto objeto de impuesto",
                                    ),
                                    "base_imp_bs": st.column_config.NumberColumn(
                                    "base imponible",
                                    default=0,
                                    help="Monto objeto de impuesto",
                                    ),
                                    "compras_exentas_bs": st.column_config.NumberColumn(
                                    "compras exentas",
                                    default=0,
                                    ),
                                    "total_neto_bs": st.column_config.NumberColumn(
                                    "total compras",
                                    default=0,
                                    ),
                                    "monto_imp_bs": st.column_config.NumberColumn(
                                    "impuesto I.V.A.",
                                    default=0,
                                    ),
                                    "monto_ret_imp_bs": st.column_config.NumberColumn(
                                    "total ret. I.V.A.",
                                    default=0,
                                    )})
        libro_compras.to_excel(buf := BytesIO())
        st.download_button(
            'Descargar',
            buf.getvalue(),
            f'Libro de Compras {ClsEmpresa.modulo_seleccionado()}.xlsx',
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)

    