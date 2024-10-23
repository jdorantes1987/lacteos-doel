import os
from numpy import where
import streamlit as st
from io import BytesIO
from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.inventario import Inventario
from scripts.empresa import ClsEmpresa
from scripts.cxc import CXC

st.set_page_config(page_title='Inventario', 
                   layout='wide', 
                   page_icon='⚡')

make_sidebar()
st.subheader("Resumen de inventario")
base_de_datos = os.getenv('DB_NAME_PROFIT_DOEL') if ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=base_de_datos)

@st.cache_data
def resumen_inventario():
    return Inventario(conexion).resumen_mov_inventario_filtrado_almacen_preincipal()

@st.cache_data
def movimientos_inventario_filtrado():
    return Inventario(conexion).movimientos_inventario_filtrado()

if st.button("🔄 Refrescar"):
    st.cache_data.clear()

tab1, tab2 = st.tabs(["Resumen", "Movimientos"])
with tab1:
    st.markdown('''
    :blue[Resumen de inventario principal sin incluir facturas, devoluciones e inventario provisional de 1.000 unidades por cada artículo].''')
    resumen_inventario = resumen_inventario()
    # Inserta columna llamada 'Select'
    resumen_inventario.insert(0, "Select", False) 
    edited_df = st.data_editor(resumen_inventario,
                            column_config={
                                            "co_art": st.column_config.TextColumn(
                                            "cod. articulo",
                                            ),
                                            "art_des": st.column_config.TextColumn(
                                            "descripcion",
                                            ),
                                            "co_uni": st.column_config.TextColumn(
                                            "cod. unidad",
                                            ),
                                            "co_alma": st.column_config.TextColumn(
                                            "cod. almacen",
                                            ),
                                            "total_entrada": st.column_config.NumberColumn(
                                            "total entradas",
                                            format="%.2f",
                                            ),
                                            "total_salida": st.column_config.NumberColumn(
                                            "total salidas",
                                            format="%.2f",
                                            ),
                                            "saldo": st.column_config.NumberColumn(
                                            "saldo final",
                                            format="%.2f",
                                            )},
                            use_container_width=False,
                            hide_index=True)

    selected_articulos = list(where(edited_df.Select)[0])
    selected_rows = resumen_inventario[edited_df.Select].copy()
    resumen_inventario[['co_art', 'art_des', 'co_uni', 'co_alma', 'total_entrada', 'total_salida', 'saldo']].to_excel(buf := BytesIO())
    st.download_button(
        'Descargar',
        buf.getvalue(),
        f'Resumen de inventario {ClsEmpresa.modulo_seleccionado()}.xlsx',
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
    
with tab2:
    st.markdown('''
    :orange[Movimientos de inventario principal sin incluir facturas, devoluciones e inventario provisional de 1.000 unidades por cada artículo].''')
    movimientos = movimientos_inventario_filtrado()[['co_art', 'art_des', 'co_uni', 'co_cliprov', 'co_alma', 'tipo', 'costo_pro', 'doc_num', 'fecha', 'total_entrada', 'total_salida']]
    movimientos_almacen_principal = movimientos[movimientos['co_alma'] == '01'] 
    articulos_filtrados = movimientos_almacen_principal[movimientos_almacen_principal['co_art'].isin(selected_rows['co_art'])].copy() 
    st.subheader("Movimientos de inventario")
    st.dataframe(articulos_filtrados,
                column_config={
                                "co_art": st.column_config.TextColumn(
                                "cod. articulo",
                                ),
                                "art_des": st.column_config.TextColumn(
                                "descripcion",
                                ),
                                "co_uni": st.column_config.TextColumn(
                                "cod. unidad",
                                ),
                                "co_alma": st.column_config.TextColumn(
                                "cod. almacen",
                                ),
                                "co_cliprov":st.column_config.TextColumn(
                                "cod. cli_prov"
                                ),
                                "fecha":st.column_config.DateColumn(
                                "fecha doc.",
                                format="DD-MM-YYYY"
                                ),
                                "doc_num": st.column_config.TextColumn(
                                "número doc.",
                                ),
                                "costo_pro": st.column_config.NumberColumn(
                                "costo art.",
                                format="%.2f",
                                ),
                                "total_entrada": st.column_config.NumberColumn(
                                "total entradas",
                                format="%.2f",
                                ),
                                "total_salida": st.column_config.NumberColumn(
                                "total salidas",
                                format="%.2f",
                                ),
                                "saldo": st.column_config.NumberColumn(
                                "saldo final",
                                format="%.2f",
                                )},
                use_container_width=True,
                hide_index=True)
    articulos_filtrados.to_excel(buf := BytesIO())
    st.download_button(
        'Descargar movimientos de inventario',
        buf.getvalue(),
        f'Movimientos de inventario {ClsEmpresa.modulo_seleccionado()}.xlsx',
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
