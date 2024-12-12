import os
from io import BytesIO
from numpy import where, nan
from datetime import datetime, timedelta

from pandas import DataFrame, concat
import matplotlib.pyplot as plt
import streamlit as st

from helpers.navigation import make_sidebar
from scripts.conexion import ConexionBD
from scripts.estado_cuenta_rutero import EstadoCuentaRutero
from scripts.ajustes import Ajustes
from scripts.empresa import ClsEmpresa
from scripts.cobros import Cobros
from scripts.rpt_edo_cta import ReporteEstadoCuenta


st.set_page_config(page_title='Edo. Cta. Rutero', 
                   layout='wide', 
                   page_icon='⚡')

make_sidebar()
empresa = os.getenv('DB_NAME_PROFIT_DOEL') if  ClsEmpresa.modulo_seleccionado() =='DOEL' else os.getenv('DB_NAME_PROFIT_PANA')
conexion = ConexionBD(base_de_datos=empresa)
estado_cuenta_rutero = EstadoCuentaRutero(conexion=conexion)
ajustes = Ajustes(conexion=conexion)
cobros = Cobros(conexion=conexion)

@st.cache_data
def resumen_movimientos_cuenta_ruteros(**kwargs):
    return estado_cuenta_rutero.resumen_movimiento_cuenta(**kwargs)

@st.cache_data
def movimiento_cuenta_rutero_x_dia(**kwargs):
    return estado_cuenta_rutero.movimiento_cuenta_rutero_x_dia(**kwargs)

@st.cache_data
def mov_facturas_directas(**kwargs):
    mov_fact = estado_cuenta_rutero.resumen_facturas_rutero(**kwargs)
    if len(mov_fact) > 0 :
        mov_fact = mov_fact.sort_values(by=['fec_emis'], ascending=[False])
        mov_fact['fec_emis'] = mov_fact['fec_emis'].dt.strftime('%d-%m-%Y')
    return mov_fact

@st.cache_data
def mov_facturas_comercios(**kwargs):
    mov_fact_comercio = estado_cuenta_rutero.calculo_ganacia_por_factura_comercio(**kwargs)
    if len(mov_fact_comercio) > 0 :
        mov_fact_comercio = mov_fact_comercio.sort_values(by=['fec_emis'], ascending=[False])
        mov_fact_comercio['fec_emis'] = mov_fact_comercio['fec_emis'].dt.strftime('%d-%m-%Y')
    return mov_fact_comercio

@st.cache_data
def movimientos_nota_entrega_rutero(**kwargs):
    notas_entrega = estado_cuenta_rutero.resumen_nota_entrega_rutero(**kwargs)
    if len(notas_entrega) > 0 :
        notas_entrega = notas_entrega.sort_values(by=['fec_emis'], ascending=[False])
        notas_entrega['fec_emis'] = notas_entrega['fec_emis'].dt.strftime('%d-%m-%Y')
        notas_entrega.rename(columns={'total_item':'total_ne'}, inplace=True)
    return notas_entrega

@st.cache_data
def movimientos_ajustes(**kwargs):
    ajustes_rutero = ajustes.documentos_ajustes(**kwargs)
    if len(ajustes_rutero) > 0 :
        ajustes_rutero = ajustes_rutero.sort_values(by=['fec_emis'], ascending=[False])
        ajustes_rutero['fec_emis'] = ajustes_rutero['fec_emis'].dt.strftime('%d-%m-%Y')
    return ajustes_rutero

@st.cache_data
def movimientos_ganancias_aplicadas(**kwargs):
    ganancias_aplicadas = ajustes.ganancias_aplicadas(**kwargs)
    if len(ganancias_aplicadas) > 0 :
        ganancias_aplicadas = ganancias_aplicadas.sort_values(by=['fec_emis'], ascending=[False])
        ganancias_aplicadas['fec_emis'] = ganancias_aplicadas['fec_emis'].dt.strftime('%d-%m-%Y')
    return ganancias_aplicadas

@st.cache_data
def movimientos_cobros(**kwargs):
    cobros_ruta = cobros.view_cobros_x_cliente(**kwargs)
    if len(cobros_ruta) > 0 :
        cobros_ruta = cobros_ruta[cobros_ruta['tip_cli'] == 'R']
        cobros_ruta = cobros_ruta.sort_values(by=['fecha'], ascending=[False])
        cobros_ruta['fecha'] = cobros_ruta['fecha'].dt.strftime('%d-%m-%Y')
    return cobros_ruta

if 'rutero_selected' not in st.session_state:
    st.session_state.rutero_selected = ""
    st.session_state.rutero_selected_name = ""
    st.session_state.rutero_selected_saldo = 0.0

st.header("Cuenta de Facturación")

col1, col2 = st.columns(2, gap="small")
with col1:
    #Fecha actual
    now = datetime.now()
    mes, year = now.month, now.year
    current_fecha_ini = datetime(year, mes, 1, 0, 00, 00, 00000)
    fecha_ini = st.date_input("fecha inicial", value=current_fecha_ini).strftime('%Y%m%d') # Convierte la fecha a YYYYMMDD
with col2:
    fecha_fin = st.date_input("fecha final").strftime('%Y%m%d') # Convierte la fecha a YYYYMMDD

mov_ruta = resumen_movimientos_cuenta_ruteros(tip_cli='R', fecha_d=fecha_ini, fecha_h=fecha_fin)[['co_cli', 'cli_des', 'sa_total', 'total_ne', 'total_fd', 'total_fcp2', 'total_ajust', 'total_cobro', 'total_ganancia', 'total_fondo', 'saldo']]
col, col02 = st.columns(2) 
with col:
    st.metric(
                label ='Total saldos a la fecha', 
                value='{:,.2f}'.format(mov_ruta['saldo'].sum())
            )


tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Resumen", "Movimientos", "Notas de entrega", "Facturas directas", "Factura comercios", "Gcias. aplicadas", "Ajustes", "Cobros"])
with tab1:
    st.markdown('''
    :blue[Resumen del saldo general por rutero].''')
    resumen_movimientos = mov_ruta.sort_values(by='saldo', ascending=False)
    # Inserta columna llamada 'Select'
    resumen_movimientos.insert(0, "sel", False)
    cmap = plt.colormaps['summer']
    #resumen_movimientos.style.format({"saldo": "${:,.2f}"})
    df_style = resumen_movimientos.style.format({'saldo': '{:,.2f}', 'sa_total': '{:,.2f}'},precision=2).background_gradient(cmap=cmap, subset=['saldo', 'sa_total'], axis=None)
    editor_resumen_mov = st.data_editor(df_style,
                                        column_config={ 
                                                        "co_cli": st.column_config.TextColumn(
                                                        "cod. rutero",
                                                        width='small',
                                                        ),
                                                        "cli_des": st.column_config.TextColumn(
                                                        "nombre",
                                                        width='medium',
                                                        ),
                                                        "sa_total": st.column_config.NumberColumn(
                                                        "s. anterior",
                                                        width='small',
                                                        ),
                                                        "total_ne": st.column_config.NumberColumn(
                                                        "notas e.",
                                                        width='small',
                                                        help='Despachos realizados a la ruta.'
                                                        ),
                                                        "total_fd": st.column_config.NumberColumn(
                                                        "f. directa",
                                                        width='small',
                                                        help='Facturación directa de la ruta.'
                                                        ),
                                                        "total_fcp2": st.column_config.NumberColumn(
                                                        "f. comercios",
                                                        width='small',
                                                        help='Facturación aplicada a la ruta.'
                                                        ),
                                                        "total_ajust": st.column_config.NumberColumn(
                                                        "ajustes",
                                                        width='small',
                                                        help='Documentos de ajustes positivos manuales aplicados al saldo de la ruta.'
                                                        ),
                                                        "total_cobro": st.column_config.NumberColumn(
                                                        "cobros",
                                                        width='small',
                                                        ),
                                                        "total_ganancia": st.column_config.NumberColumn(
                                                        "ganacia a.",
                                                        width='small',
                                                        help='Ganacia aplicada sobre la facturación a comercios (precio 2)'
                                                        ),
                                                        "total_fondo": st.column_config.NumberColumn(
                                                        "fondo g.",
                                                        width='small',
                                                        help='Fondo de garantía de la ruta.'
                                                        )},
                                        use_container_width=False,
                                        disabled=['co_cli', 'cli_des', 'sa_total', 'total_ne', 'total_fd', 'total_fcp2', 'total_ajust', 'total_cobro', 'total_ganancia', 'total_fondo', 'saldo'],
                                        hide_index=True)
    #selected_ruteros = list(where(editor_resumen_mov.sel)[0])
    selected_rows = resumen_movimientos[editor_resumen_mov.sel]
    if len(selected_rows) > 0 :
         st.session_state.rutero_selected = selected_rows.iloc[0,1] # Codigo ruta
         st.session_state.rutero_selected_name = selected_rows.iloc[0,2] # Nombre
         st.session_state.rutero_selected_saldo_anterior = selected_rows.iloc[0,3] # Saldo anterior
         st.session_state.rutero_selected_ne = selected_rows.iloc[0,4] # Notas de entregar
         st.session_state.rutero_selected_fd = selected_rows.iloc[0,5] # Facturas directas
         st.session_state.rutero_selected_fcp2 = selected_rows.iloc[0,6] # Facturas Comercios
         st.session_state.rutero_selected_cobros = selected_rows.iloc[0,8] # Cobros
         st.session_state.rutero_selected_saldo = selected_rows.iloc[0,11] # Saldo 
    else:
        st.session_state.rutero_selected = ""
    
    editor_resumen_mov.to_excel(buf := BytesIO())
    st.download_button(
        'Descargar',
        buf.getvalue(),
        f'Resumen estado de cuenta Rutero {ClsEmpresa.modulo_seleccionado()}.xlsx',
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
    
    
    if st.button("🔄 Refrescar"):
        st.cache_data.clear()
        st.rerun()

if len(selected_rows) > 0 :
    with tab2:
        st.markdown('''
        :blue[Detalle del movimiento de la cuenta de facturación].''')
        movimiento_x_dia = movimiento_cuenta_rutero_x_dia(tip_cli='R', fecha_d=fecha_ini, fecha_h=fecha_fin)
        tb2_col1, tb2_col2, tb2_col3 = st.columns(3)
        with tb2_col1:
            st.subheader(st.session_state.rutero_selected)
        with tb2_col2:
            st.subheader(st.session_state.rutero_selected_name) 
        with tb2_col3:   
            st.metric(
                    label ='Saldo', 
                    value='{:,.2f}'.format(float(st.session_state.rutero_selected_saldo))
            )
            
        if len(movimiento_x_dia) > 0:
            mov_filtrados_x_rutero = movimiento_x_dia[movimiento_x_dia['co_cli'].isin(selected_rows['co_cli'])].copy() 
            mov_filtrados_x_rutero['saldo'] = mov_filtrados_x_rutero['total_ne'] + mov_filtrados_x_rutero['total_fd'] - mov_filtrados_x_rutero['total_fcp2'] + mov_filtrados_x_rutero['total_ajust'] - mov_filtrados_x_rutero['total_cobro'] - mov_filtrados_x_rutero['total_ganancia'] - mov_filtrados_x_rutero['total_fondo']
            mov_filtrados_x_rutero['fec_emis'] = mov_filtrados_x_rutero['fec_emis'].dt.strftime('%d-%m-%Y')
            valores_anterior = []
            valores_anterior.append(st.session_state.rutero_selected)
            valores_anterior.append(st.session_state.rutero_selected_name + ' (S. Anterior)')
            fecha_anterior = (datetime.strptime(fecha_ini, '%Y%m%d') + timedelta(days=-1)).strftime('%d-%m-%Y')
            valores_anterior.append(fecha_anterior)
            valores_anterior.append(' ')
            valores_anterior.append(st.session_state.rutero_selected_saldo_anterior)
            columns_saldo_anterior = ['co_cli', 'cli_des', 'fec_emis', 'fec_mid', 'saldo']
            df_saldo_anterior = DataFrame([valores_anterior], columns=columns_saldo_anterior)
            mov_filtrados_x_rutero = concat([df_saldo_anterior, mov_filtrados_x_rutero], axis=0, ignore_index=True)
            mov_filtrados_x_rutero['saldo final'] = mov_filtrados_x_rutero['saldo'].cumsum()
            mov_filtrados_x_rutero.drop(columns=['saldo'], inplace=True)
            mov_filtrados_x_rutero.replace(nan, 0.0, inplace=True)
            resumen_movimientos_style = mov_filtrados_x_rutero.style.format({
                                                                            'total_ne': '{:,.2f}', 
                                                                            'saldo final': '{:,.2f}',
                                                                            'total_fd': '{:,.2f}',
                                                                            'total_fcp2': '{:,.2f}',
                                                                            'total_ajust': '{:,.2f}',
                                                                            'total_cobro':'{:,.2f}',
                                                                            'total_ganancia':'{:,.2f}',
                                                                            'total_fondo':'{:,.2f}',
                                                                            'saldo final': '{:,.2f}'},
                                                                            precision=2)
            mov_rut = st.dataframe(resumen_movimientos_style,
                                                column_config={
                                                    "fec_emis":st.column_config.TextColumn(
                                                    "fecha",
                                                    width='small',
                                                    ),
                                                    "fec_mid": st.column_config.TextColumn(
                                                    "día",
                                                    width='small',
                                                    ),
                                                    "co_cli": st.column_config.TextColumn(
                                                    "ruta",
                                                    ),
                                                    "cli_des": st.column_config.TextColumn(
                                                    "razón social",
                                                    width='medium',
                                                    ),
                                                    "total_ne": st.column_config.NumberColumn(
                                                    "n. entrega",
                                                    width='small',
                                                    ),
                                                    "total_fd": st.column_config.NumberColumn(
                                                    "f. directa",
                                                    width='small',
                                                    ),
                                                    "total_fcp2": st.column_config.NumberColumn(
                                                    "f. comerc.",
                                                    width='small',
                                                    ),
                                                    "total_ajust": st.column_config.NumberColumn(
                                                    "ajustes",
                                                    width='small',
                                                    ),
                                                    "total_cobro": st.column_config.NumberColumn(
                                                    "cobros",
                                                    width='small',
                                                    ),
                                                    "total_ganancia": st.column_config.NumberColumn(
                                                    "gncia/apl",
                                                    width='small',
                                                    ),
                                                    "total_fondo": st.column_config.NumberColumn(
                                                    "fdo. garant.",
                                                    width='small',
                                                    ),
                                                    "saldo final": st.column_config.NumberColumn(
                                                    "saldo final",
                                                    width='small',
                                                    )},
                                                use_container_width=True,
                                                hide_index=True)
            
            
            tb2_col4, tb2_col5 = st.columns(2)
            with tb2_col4:
                mov_filtrados_x_rutero.to_excel(buf := BytesIO())
                st.download_button(
                'Descargar',
                buf.getvalue(),
                f'Movimientos estado de cuenta Rutero {ClsEmpresa.modulo_seleccionado()}.xlsx',
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",)
                
            with tb2_col5:
                if st.button("reporte"):
                    rpt = ReporteEstadoCuenta()
                    nombre = st.session_state.rutero_selected_name
                    codigo = st.session_state.rutero_selected
                    saldo_a = st.session_state.rutero_selected_saldo_anterior
                    saldo = st.session_state.rutero_selected_saldo
                    data = dict(nombre=nombre,
                                cod_ruta=codigo,
                                saldo_a='{:,.2f}'.format(saldo_a),
                                saldo='{:,.2f}'.format(saldo),
                                fecha_rpt=datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                                fecha_i=datetime.strptime(fecha_ini,'%Y%m%d').strftime("%d-%m-%Y"),
                                fecha_f=datetime.strptime(fecha_fin,'%Y%m%d').strftime("%d-%m-%Y"),
                                total_ne='{:,.2f}'.format(mov_filtrados_x_rutero['total_ne'].sum()),
                                total_fd='{:,.2f}'.format(mov_filtrados_x_rutero['total_fd'].sum()),
                                total_fcp2='{:,.2f}'.format(mov_filtrados_x_rutero['total_fcp2'].sum()),
                                total_ajust='{:,.2f}'.format(mov_filtrados_x_rutero['total_ajust'].sum()),
                                total_cobro='{:,.2f}'.format(mov_filtrados_x_rutero['total_cobro'].sum()),
                                total_ganancia='{:,.2f}'.format(mov_filtrados_x_rutero['total_ganancia'].sum()),
                                total_fondo='{:,.2f}'.format(mov_filtrados_x_rutero['total_fondo'].sum()),)
                    columnas_a_formatear = ['total_ne', 'total_fd', 'total_fcp2', 'total_ajust','total_cobro', 'total_ganancia','total_fondo', 'saldo final']
                    # Aplicar el formato a las columnas seleccionadas 
                    mov_filtrados_x_rutero[columnas_a_formatear] = mov_filtrados_x_rutero[columnas_a_formatear].map(lambda x: '{:,.2f}'.format(x))
                    movimientos = mov_filtrados_x_rutero.to_dict('records')
                    
                    rpt.reder_and_open_data(encabezados=data, 
                                            movimientos=movimientos,
                                            nombre_file=nombre)
            
    with tab3:
        st.markdown('''
        :blue[Movimientos notas de entrega por rutero].''')
        movimientos_ne = movimientos_nota_entrega_rutero(tip_cli='R', fecha_d=fecha_ini, fecha_h=fecha_fin)
        if len(movimientos_ne) > 0:
            movimientos_ne = movimientos_ne[movimientos_ne['co_cli'] == st.session_state.rutero_selected]
            tb3_col1, tb3_col2 = st.columns(2) 
            with tb3_col1:
                st.metric(
                        label ='Total notas de entrega', 
                        value='{:,.2f}'.format(movimientos_ne['total_ne'].sum()))
            with tb3_col2:    
                st.metric(
                        label ='Número de documentos', 
                        value=movimientos_ne['total_ne'].count())
            movimientos_ne = movimientos_ne.style.format({'total_ne': '{:,.2f}'}, precision=2)
            st.dataframe(movimientos_ne,
                        column_config={
                                        "co_cli": st.column_config.TextColumn(
                                        "rutero",
                                            width='small',
                                        ),
                                        "cli_des": st.column_config.TextColumn(
                                        "razón social",
                                        width='large',
                                        ),
                                        "doc_num": st.column_config.TextColumn(
                                        "número doc.",
                                        width='medium',
                                        ),
                                        "fec_emis": st.column_config.TextColumn(
                                        "fecha",
                                        width='small')},
                        use_container_width=False,
                        hide_index=True)
        
    with tab4:
        st.markdown('''
        :blue[Facturas emitidas a ruteros].''')
        tb4_col1, tb4_col2 = st.columns(2)
        mov_facturas = mov_facturas_directas(tip_cli='R', fecha_d=fecha_ini, fecha_h=fecha_fin)[['co_cli', 'cli_des', 'doc_num', 'fec_emis', 'total_item']]
        if len(mov_facturas) > 0:
            mov_facturas = mov_facturas[mov_facturas['co_cli'] == st.session_state.rutero_selected]
            with tb4_col1:
                st.metric(
                        label ='Total facturación directa.', 
                        value='{:,.2f}'.format(mov_facturas['total_item'].sum()))
            with tb4_col2:
                st.metric(
                        label ='Número de documentos.', 
                        value=mov_facturas['total_item'].count())
            mov_facturas = mov_facturas.style.format({'total_item': '{:,.2f}'}, precision=2)
            st.dataframe(mov_facturas,
                        column_config={
                                        "co_cli": st.column_config.TextColumn(
                                        "rutero",
                                            width='small',
                                        ),
                                        "cli_des": st.column_config.TextColumn(
                                        "razón social",
                                        width='large',
                                        ),
                                        "doc_num": st.column_config.TextColumn(
                                        "número fact.",
                                        width='small',
                                        ),
                                        "fec_emis": st.column_config.TextColumn(
                                        "fecha",
                                        width='small')},
                        use_container_width=False,
                        hide_index=True)

    with tab5:
        st.markdown('''
        :blue[Facturas comercios aplicadas a rutero].''')
        tb5_col1, tb5_col2 = st.columns(2)
        facturas_comercios_ruteros = mov_facturas_comercios(tip_cli='R', fecha_d=fecha_ini, fecha_h=fecha_fin)
        if len(facturas_comercios_ruteros) > 0:
            facturas_comercios_ruteros = facturas_comercios_ruteros.groupby(['co_cli_t1', 'co_tran', 'fec_emis', 'cli_des', 'doc_num_t1'], sort=False).agg({'total_item_precio_2':'sum'}).reset_index()
            facturas_comercios_ruteros.rename(columns={'co_tran':'ruta', 'co_cli_t1':'co_cli', 'total_item_precio_2':'total_fact.'}, inplace=True)
            facturas_comercios_ruteros = facturas_comercios_ruteros[facturas_comercios_ruteros['ruta'] == st.session_state.rutero_selected]
            with tb5_col1:
                st.metric(
                        label ='Total facturación comercios.', 
                        value='{:,.2f}'.format(facturas_comercios_ruteros['total_fact.'].sum()))
            with tb5_col2:
                st.metric(
                        label ='Número de documentos.', 
                        value=facturas_comercios_ruteros['total_fact.'].count())   
            facturas_comercios_ruteros = facturas_comercios_ruteros.style.format({'total_fact.': '{:,.2f}'}, precision=2)
            st.dataframe(facturas_comercios_ruteros,
                        column_config={
                                        "co_cli": st.column_config.TextColumn(
                                        "cod. cliente",
                                            width='small',
                                        ),
                                        "cli_des": st.column_config.TextColumn(
                                        "razón social",
                                        width='large',
                                        ),
                                        "doc_num_t1": st.column_config.TextColumn(
                                        "número fact.",
                                        width='small',
                                        ),
                                        "fec_emis": st.column_config.TextColumn(
                                        "fecha",
                                        width='small')},
                        use_container_width=False,
                        hide_index=True)
        
    with tab6:
        st.markdown('''
        :blue[Ganancias aplicadas sobre facturas de comercios precio dos].''')
        ganancias_aplicadas = movimientos_ganancias_aplicadas(tip_cli='R', fecha_d=fecha_ini, fecha_h=fecha_fin)[['co_cli', 'co_tipo_doc', 'fec_emis', 'nro_doc', 'nro_orig', 'total_neto']]
        if len(ganancias_aplicadas) > 0:
            ganancias_aplicadas = ganancias_aplicadas[ganancias_aplicadas['co_cli'] == st.session_state.rutero_selected]
            st.metric(
                    label ='Total ganancias aplicadas', 
                    value='{:,.2f}'.format(ganancias_aplicadas['total_neto'].sum())
                )
            ganancias_aplicadas = ganancias_aplicadas.style.format({'total_neto.': '{:,.2f}'}, precision=2)
            st.dataframe(ganancias_aplicadas,
                        column_config={
                                        "co_cli": st.column_config.TextColumn(
                                        "cod. cliente",
                                            width='small',
                                        ),
                                        "nro_doc": st.column_config.TextColumn(
                                        "doc. ajuste",
                                        width='small',
                                        ),
                                        "nro_orig": st.column_config.TextColumn(
                                        "número fact.",
                                        width='small',
                                        ),
                                        "co_tipo_doc": st.column_config.TextColumn(
                                        "tipo doc.",
                                        width='small',
                                        ),
                                        "fec_emis": st.column_config.TextColumn(
                                        "fecha",
                                        width='small')},
                        use_container_width=False,
                        hide_index=True)  
        
    with tab7:
        st.markdown('''
        :blue[Ajustes aplicados al rutero].''')
        ajustes_rutero = movimientos_ajustes(tip_cli='R', fecha_d=fecha_ini, fecha_h=fecha_fin)
        if len(ajustes_rutero) > 0:
            ajustes_rutero = ajustes_rutero[(ajustes_rutero['tip_cli'] == 'R') & (~ajustes_rutero['co_tipo_doc'].isin(['IVAN', 'AJPA', 'AJNA'])) & (ajustes_rutero['co_cta_ingr_egr'] != 'APS')].copy()
            ajustes_rutero = ajustes_rutero.groupby(['co_tipo_doc', 'co_cli', 'cli_des', 'doc_num', 'fec_emis']).agg({'total_neto':'sum'}).reset_index()
            ajustes_rutero.rename(columns={'total_neto':'total_ajust'}, inplace=True)
            ajustes_rutero = ajustes_rutero[ajustes_rutero['co_cli'] == st.session_state.rutero_selected]
            st.metric(
                    label ='Total ajustes', 
                    value='{:,.2f}'.format(ajustes_rutero['total_ajust'].sum())
                )
            ajustes_rutero = ajustes_rutero.style.format({'total_ajust': '{:,.2f}'}, precision=2)
            st.dataframe(ajustes_rutero,
                        column_config={
                                        "co_cli": st.column_config.TextColumn(
                                        "ruta",
                                            width='small',
                                        ),
                                        "cli_des": st.column_config.TextColumn(
                                        "razón social",
                                        width='large',
                                        ),
                                        "doc_num": st.column_config.TextColumn(
                                        "número ajuste",
                                        width='medium',
                                        ),
                                        "co_tipo_doc": st.column_config.TextColumn(
                                        "tipo ajuste.",
                                        width='small',
                                        ),
                                        "fec_emis": st.column_config.TextColumn(
                                        "fecha",
                                        width='small')},
                        use_container_width=False,
                        hide_index=True)
        
    with tab8:
        st.markdown('''
        :blue[Cobros realizados a rutero].''')
        tb8_col1, tb8_col2 = st.columns(2)
        cobros_rutero = movimientos_cobros(tip_cli='R', fecha_d=fecha_ini, fecha_h=fecha_fin)
        if len(cobros_rutero) > 0:
            cobros_rutero = cobros_rutero[cobros_rutero['tip_cli'] == 'R']
            cobros_rutero = cobros_rutero.groupby(['co_cli', 'cli_des', 'co_tipo_doc', 'cob_num', 'fecha', 'nro_doc'], sort=False).agg({'cargo':'sum'}).reset_index()
            cobros_rutero.rename(columns={'fecha':'fec_emis', 'cargo':'total_cobro'}, inplace=True)
            cobros_rutero = cobros_rutero[cobros_rutero['co_cli'] == st.session_state.rutero_selected]
            with tb8_col1:
                st.metric(
                        label ='Total cobros', 
                        value='{:,.2f}'.format(cobros_rutero['total_cobro'].sum())
                    )
            with tb8_col2:
                st.metric(
                        label ='Número de documentos.', 
                        value=cobros_rutero['total_cobro'].count()
                    ) 
            cobros_rutero = cobros_rutero.style.format({'total_cobro': '{:,.2f}'}, precision=2)
            st.dataframe(cobros_rutero,
                        column_config={
                                        "co_cli": st.column_config.TextColumn(
                                        "ruta",
                                            width='small',
                                        ),
                                        "cli_des": st.column_config.TextColumn(
                                        "razón social",
                                        width='large',
                                        ),
                                        "co_tipo_doc": st.column_config.TextColumn(
                                        "tipo doc.",
                                        width='small',
                                        ),
                                        "cob_num": st.column_config.TextColumn(
                                        "núm. cobro",
                                        width='medium',
                                        ),
                                        "nro_doc": st.column_config.TextColumn(
                                        "núm. doc",
                                        width='medium',
                                        ),
                                        "fec_emis": st.column_config.TextColumn(
                                        "fecha",
                                        width='small')},
                        use_container_width=False,
                        hide_index=True)    