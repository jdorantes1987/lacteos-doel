import os
import streamlit as st
from io import BytesIO
from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.empresa import ClsEmpresa
from scripts.compras import ComprasConsultas 

st.set_page_config(page_title='Compras', 
                   layout='centered', 
                   page_icon=':vs:')
make_sidebar()
base_de_datos = os.getenv('DB_NAME_PROFIT_DOEL') if ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=base_de_datos)

st.subheader("Listado de productos en compras")

with st.expander("mostrar"):
    datos_vencimiento = ComprasConsultas(conexion).datos_vencimientos_productos()
    st.dataframe(datos_vencimiento,
                use_container_width=True,
                hide_index=True,
                column_config={
                                "doc_num": st.column_config.TextColumn(
                                "doc. compra",
                                ),
                                "nro_fact": st.column_config.TextColumn(
                                "nro fact.",
                                ),
                                "fec_emis":st.column_config.DateColumn(
                                "fecha fact.",
                                format="DD-MM-YYYY"
                                ),
                                "co_prov": st.column_config.TextColumn(
                                "cod. proveedor",
                                ),
                                "prov_des": st.column_config.TextColumn(
                                "razón social",
                                ),
                                "co_art": st.column_config.TextColumn(
                                "cod. artículo",
                                ),    
                                "art_des": st.column_config.TextColumn(
                                "descripción artículo",
                                ),
                                "total_art": st.column_config.NumberColumn(
                                "cantidad",
                                default=0,
                                help="cantidad de artículos comprados",
                                ),
                                "cost_unit": st.column_config.NumberColumn(
                                "costo unid.",
                                default=0,
                                format="$ %.2f",
                                ),    
                                "comentario": st.column_config.TextColumn(
                                "fecha venc.",
                                ),})
    datos_vencimiento.to_excel(buf := BytesIO())
    st.download_button(
        'Descargar',
        buf.getvalue(),
        f'Vencimientos de productos en compras {ClsEmpresa.modulo_seleccionado()}.xlsx',
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
    