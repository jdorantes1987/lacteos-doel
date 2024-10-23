import locale
from pandas import DataFrame
from pandas import concat
from pandas import merge
from pandas import to_datetime
from pandas import merge_asof
from pandas import pivot_table
from pandas import options
from numpy import nan
from datetime import datetime
from re import findall
from xml.etree import ElementTree as xml_tree
from scripts.utilidades import search_df, ultimo_dia_mes
from scripts.sql_read import get_read_sql
from scripts.bcv.data import historico_tasas_bcv

options.display.float_format = '{:,.2f}'.format  # Configuramos separadores de miles y 2 decimales

class DatosProfit:
    campos_comunes_fact = ['co_tipo_doc', 'doc_num', 'fec_reg', 'co_cli', 'cli_des', 'co_ven', 'ven_des']
    l_campos_facturacion = ['reng_num', 'doc_num', 'co_art', 'cod_art_izq', 'co_tipo_doc', 'fec_emis', 'fec_reg', 'anio', 'mes_x',
                            'co_ven', 'co_cli', 'cli_des', 'ven_des', 'descrip', 'monto_base_item', 'iva', 'igtf', 'total_item', 
                            'saldo_total_doc']
    
    def __init__(self, conexion):
        self.conexion = conexion
# Agrega un identificador unico para la columna pasa por parámetro
    def get_identificador_unicos(self, df, name_field) -> DataFrame:
        df['correl'] = df.groupby([name_field]).cumcount() + 1
        df['correl'] = df['correl'].astype('str')
        df['identificador'] = df.apply(lambda x: str(x[name_field]) + x['correl'], axis=1)
        return df

    def articulos_profit(self):
        sql = """
            Select RTRIM(co_art) as co_art, fecha_reg, art_des, tipo_imp, tipo, anulado, fecha_inac, co_lin, co_subl, co_cat, co_color 
            co_ubicacion, cod_proc, item, modelo, ref, comentario, dis_cen, RTRIM(campo1) as campo1, campo2, campo3, campo4, 
            campo5, campo6, campo7, campo8, co_us_in, co_sucu_in, fe_us_in, co_us_mo, co_sucu_mo, fe_us_mo 
            FROM saArticulo
            """
        return get_read_sql(sql, self.conexion)
    
    def art_unidad(self):
        sql = """
            Select RTRIM(co_art) as co_art, RTRIM(co_uni) as co_uni, equivalencia  
            FROM saArtUnidad
            """
        return get_read_sql(sql, self.conexion)
    
    def unidades(self):
        sql = """
            Select RTRIM(co_uni) as co_art, campo1 
            FROM saUnidad
            """
        return get_read_sql(sql, self.conexion)

    def data_ventas_con_detalle(self, **kwargs):
        anio, mes = kwargs.get('anio'), kwargs.get('mes')
        where_anio = f"" if anio == 'all' else f" AND year(fact.fec_reg)='{anio}'"
        where_all = "WHERE fact.[anulado]=0 " + where_anio
        where_mes = f"WHERE fact.[anulado]=0 AND year(fact.fec_reg)='{anio}' and month(fact.fec_reg)='{mes}'"
        where = where_all if mes == 'all' else where_mes
        sql = f"""
            SELECT reng_num, RTRIM(fact.doc_num) as doc_num, RTRIM(dfact.co_art) as co_art, RTRIM(art.campo1) as cod_art_izq,
                    fact.fec_emis, fact.fec_reg, fact.descrip,
                    year(fact.fec_reg) AS anio, month(fact.fec_reg) AS mes, RTRIM(fact.co_ven) as co_ven, RTRIM(fact.co_cli) as co_cli,
                    c.cli_des, (v.ven_des + iif(v.campo1 <> '', + ' -> ' + v.campo1, '')) as ven_des, (dfact.reng_neto-dfact.monto_desc_glob) AS monto_base_item,
                    (dfact.monto_imp+dfact.monto_imp_afec_glob) as iva,
                    ((dfact.reng_neto-dfact.monto_desc_glob)+(dfact.monto_imp+dfact.monto_imp_afec_glob)) as total_item,
                    iif(reng_num=1, fact.otros1, 0) as igtf, fact.saldo as saldo_total_doc 
            FROM saFacturaVenta AS fact INNER JOIN saFacturaVentaReng AS dfact ON
                    fact.doc_num = dfact.doc_num LEFT JOIN saArticulo AS art ON
                    dfact.co_art = art.co_art LEFT JOIN saCliente AS c ON fact.co_cli = c.co_cli LEFT JOIN saVendedor as v ON fact.co_ven = v.co_ven  
            {where} 
            ORDER BY fact.fec_reg, fact.doc_num
            """
        fact_det = get_read_sql(sql, self.conexion)
        fact_det['co_tipo_doc'] = 'FACT'
        return fact_det
    
    def encabezado_factura_ventas(self, fecha_ini, fecha_fin):
        sql = f"""
                SELECT RTRIM(fv.doc_num) as doc_num,fv.descrip, fv.co_cli, c.cli_des, fv.co_tran, fv.co_mone, fv.co_ven, fv.co_cond, 
                fv.fec_emis, fec_venc, fec_reg, 
                fv.anulado, fv.status, fv.n_control, fv.ven_ter, fv.tasa, fv.porc_desc_glob, fv.monto_desc_glob, fv.monto_reca, 
                fv.total_bruto, fv.monto_imp, fv.total_neto, fv.saldo, fv.co_us_in, fv.co_sucu_in, fv.fe_us_in, fv.co_us_mo, 
                fv.co_sucu_mo, fv.fe_us_mo, fv.campo1, fv.campo3 
                FROM saFacturaVenta as fv LEFT JOIN saCliente AS c ON fv.co_cli = c.co_cli 
                WHERE fv.fec_emis >= '{fecha_ini}' AND fv.fec_emis <= '{fecha_fin}'
            """
        return get_read_sql(sql, self.conexion)

    def data_notas_credito(self, **kwargs):
        l_campos = ['reng_num', 'doc_num', 'co_art', 'cod_art_izq', 'co_tipo_doc', 'fec_emis', 'fec_reg', 'anio', 'mes',
                    'co_ven', 'co_cli', 'cli_des', 'ven_des', 'descrip', 'monto_base_item', 'iva', 'igtf', 'total_item', 'saldo_total_doc']
        anio, mes = kwargs.get('anio'), kwargs.get('mes')
        where_anio = f"" if anio == 'all' else f"AND year(docv.fec_reg)='{anio}'"
        where_all = "WHERE docv.co_tipo_doc='N/CR' AND docv.anulado=0 " + where_anio
        where_mes = f"WHERE docv.co_tipo_doc='N/CR' AND docv.anulado=0 AND year(docv.fec_reg)='{anio}' and month(docv.fec_reg)='{mes}'"
        where = where_all if mes == 'all' else where_mes

        sql = f"""
            SELECT 1 as reng_num, RTRIM(docv.nro_doc) as doc_num, RTRIM(docv.co_tipo_doc) as co_tipo_doc, observa as descrip, docv.dis_cen, docv.fec_emis, 
                    docv.fec_reg, year(docv.fec_reg) AS anio, month(docv.fec_reg) AS mes, RTRIM(docv.co_ven) as co_ven, 
                    RTRIM(docv.co_cli) as co_cli, c.cli_des, (v.ven_des + iif(v.campo1 <> '', + ' -> ' + v.campo1, '')) as ven_des, 
                    -docv.total_bruto as monto_base_item, -docv.monto_imp as iva,
                    -(docv.total_neto-docv.otros1) as total_item, -docv.otros1 as igtf,  -docv.saldo as saldo_total_doc
            FROM saDocumentoVenta AS docv LEFT JOIN saCliente AS c ON docv.co_cli = c.co_cli LEFT JOIN saVendedor as v ON docv.co_ven = v.co_ven
            {where}
            """
        df_notas = get_read_sql(sql, self.conexion)
        #  Desempaqueta la cuenta contable del texto xml en las notas de credito
        df_notas['dis_cen'] = df_notas['dis_cen'].apply(
            lambda x: str(xml_tree.fromstring(x).findtext('Carpeta01/CuentaContable')) if x is not None else None)
        art = self.articulos_profit()
        #  Desempaqueta la cuenta contable del texto xml en los articulos
        art['dis_cen'] = art['dis_cen'].apply(
            lambda x: str(xml_tree.fromstring(x).findtext('Carpeta03/CuentaContable')) if x is not None else None)
        art2 = art[['co_art', 'dis_cen', 'campo1']]
        #  El método drop_duplicates elimina las filas duplicadas en el dataframe de la derecha basándose en la columna dis_cen
        df_notas_art = merge(df_notas, art2.drop_duplicates('dis_cen'), on='dis_cen', how='left', suffixes=('_t1', '_t2'))
        df_notas_art['co_art'] = df_notas_art['co_art'].str.strip()  # suprimir espacios en las cadenas de texto
        df_notas_art.rename(columns={'campo1': 'cod_art_izq'}, inplace=True)
        df_notas_art = df_notas_art[l_campos]
        return df_notas_art

    def data_documentos(self, **kwargs):
        l_campos = ['reng_num', 'doc_num', 'co_art', 'cod_art_izq', 'co_tipo_doc', 'fec_emis', 'fec_reg', 'anio', 'mes',
                    'co_ven', 'co_cli', 'cli_des', 'ven_des', 'descrip', 'monto_base_item', 'iva', 'igtf', 'total_item', 'saldo_total_doc']
        anio, mes, tipo_doc = kwargs.get('anio'), kwargs.get('mes'), kwargs.get('tipo_doc')
        where_anio = f"" if anio == 'all' else f"AND year(docv.fec_reg)='{anio}'"
        where_all = f"WHERE docv.co_tipo_doc='{tipo_doc}' AND docv.anulado=0 " + where_anio
        where_mes = f"WHERE docv.co_tipo_doc='{tipo_doc}' AND docv.anulado=0 AND year(docv.fec_reg)='{anio}' and month(docv.fec_reg)='{mes}'"
        where = where_all if mes == 'all' else where_mes

        sql = f"""
            SELECT 1 as reng_num, RTRIM(docv.nro_doc) as doc_num, RTRIM(docv.co_tipo_doc) as co_tipo_doc, observa as descrip, docv.dis_cen, docv.fec_emis, 
                    docv.fec_reg, year(docv.fec_reg) AS anio, month(docv.fec_reg) AS mes, RTRIM(docv.co_ven) as co_ven, 
                    RTRIM(docv.co_cli) as co_cli, c.cli_des, (v.ven_des + iif(v.campo1 <> '', + ' -> ' + v.campo1, '')) as ven_des, 
                    docv.total_bruto as monto_base_item, docv.monto_imp as iva,
                    (docv.total_neto-docv.otros1) as total_item, docv.otros1 as igtf, docv.saldo as saldo_total_doc 
            FROM saDocumentoVenta AS docv LEFT JOIN saCliente AS c ON docv.co_cli = c.co_cli LEFT JOIN saVendedor as v ON docv.co_ven = v.co_ven
            {where}
            """
        df_doc = get_read_sql(sql, self.conexion)
        #  Desempaqueta la cuenta contable del texto xml en las notas de credito
        df_doc['dis_cen'] = df_doc['dis_cen'].apply(
            lambda x: str(xml_tree.fromstring(x).findtext('Carpeta01/CuentaContable')) if x is not None else None)
        art = self.articulos_profit()
        #  Desempaqueta la cuenta contable del texto xml en los articulos
        art['dis_cen'] = art['dis_cen'].apply(
            lambda x: str(xml_tree.fromstring(x).findtext('Carpeta03/CuentaContable')) if x is not None else None)
        art2 = art[['co_art', 'dis_cen', 'campo1']]
        #  El método drop_duplicates elimina las filas duplicadas en el dataframe de la derecha basándose en la columna dis_cen
        df_doc_art = merge(df_doc, art2.drop_duplicates('dis_cen'), on='dis_cen', how='left', suffixes=('_t1', '_t2'))
        df_doc_art['co_art'] = df_doc_art['co_art'].str.strip()  # suprimir espacios en las cadenas de texto
        df_doc_art.rename(columns={'campo1': 'cod_art_izq'}, inplace=True)
        df_doc_art = df_doc_art[l_campos]
        return df_doc_art
    
    def encabezado_notas_entrega(self):
        sql = """
                SELECT RTRIM(ne.doc_num) as doc_num,ne.descrip, ne.co_cli, c.cli_des, ne.co_tran, ne.co_mone, ne.co_ven, ne.co_cond, 
                ne.fec_emis, fec_venc, fec_reg, 
                ne.anulado, ne.status, ne.n_control, ne.ven_ter, ne.tasa, ne.porc_desc_glob, ne.monto_desc_glob, ne.monto_reca, 
                ne.total_bruto, ne.monto_imp, ne.total_neto, ne.saldo, ne.co_us_in, ne.co_sucu_in, ne.fe_us_in, ne.co_us_mo, 
                ne.co_sucu_mo, ne.fe_us_mo 
                FROM saNotaEntregaVenta as ne LEFT JOIN saCliente AS c ON ne.co_cli = c.co_cli
            """
        return get_read_sql(sql, self.conexion)
    
    def ventas_con_detalle(self, **kwargs):
        anio, mes, conv_usd = kwargs.get('anio', 'all'), kwargs.get('mes', 'all'), kwargs.get('usd', True)
        l_campos = self.l_campos_facturacion.copy()
        fact_detalle = self.data_ventas_con_detalle(anio=anio, mes=mes)
        notas_de_cre = self.data_notas_credito(anio=anio, mes=mes)
            # verifica que existan notas de crédito antes de hacer la concatenación
        if notas_de_cre.empty != True:
            fact_detalle_total = concat([fact_detalle, notas_de_cre], axis=0, ignore_index=True)
        else:
            fact_detalle_total = fact_detalle

        df_data_bcv = historico_tasas_bcv()  # archivo BCV
        fact_detalle_total['descrip'] = fact_detalle_total['descrip'].replace(nan, " ") # Permite corregir error al agrupar los datos
        fact_detalle_total['fec_reg'] = to_datetime(fact_detalle_total['fec_reg']).dt.normalize()  # fecha sin hora, minutos y segundos
        fact_detalle_sort = fact_detalle_total.sort_values(by=['fec_reg'], ascending=[True])  # se debe ordenar el df para poder conbinar
        data_bcv_sort = df_data_bcv.sort_values(by=['fecha'], ascending=[True])  # se debe ordenar el df para poder conbinar
        merge_data = merge_asof(fact_detalle_sort, data_bcv_sort, left_on='fec_reg', right_on='fecha', direction="nearest")  # Combinar por aproximación
        merge_data['monto_base_item'] = merge_data.apply(lambda x: x['monto_base_item'] / x['venta_ask2'] if conv_usd else x['monto_base_item'], axis=1)
        merge_data['iva'] = merge_data.apply(lambda x: x['iva'] / x['venta_ask2'] if conv_usd else x['iva'], axis=1)
        # modifica la columna total_item, si es el primer reglón del detalle de la factura, se usan dos condicionales.
        # 1 evalua si se debe convertir a usd y si es el primer renglon, convertir a USD y agregar saldo.
        # 2 evalua si es el primer renglon, agregar total_item + igtf.
        # el igtf será asignado al artículo del primer renglón. 
        merge_data['total_item'] = merge_data.apply(lambda x: (x['total_item'] + x['igtf']) / x['venta_ask2'] if conv_usd  else x['total_item'] + x['igtf'], axis=1)
        merge_data['igtf'] = merge_data.apply(lambda x: x['igtf'] / x['venta_ask2'] if conv_usd else x['igtf'], axis=1)
        # modifica la columna saldo_total_doc a cero, si no es el primer reglón del detalle de la factura, se usan dos condicionales.
        # 1 evalua si debe convertir a usd y si es el primer renglon, convertir a USD y agregar saldo.
        # 2 evalua si es el primer renglon, agregar saldo.
        merge_data['saldo_total_doc'] = merge_data.apply(lambda x: (x['saldo_total_doc'] / x['venta_ask2']) if conv_usd and (x['reng_num'] == 1)  else x['saldo_total_doc'] if x['reng_num'] == 1 else 0, axis=1)
        # merge_data.to_excel('ventas_con_detalle.xlsx')
        return merge_data[l_campos]


    def ventas_sin_detalle(self, **kwargs):
        anio, mes, conv_usd = kwargs.get('anio', 'all'), kwargs.get('mes', 'all'), kwargs.get('usd', True)
        l_campos = self.l_campos_facturacion.copy()
        df_fact = self.ventas_con_detalle(anio=anio, mes=mes, usd=conv_usd).copy()
        # Se eliminan los renglones y articulos para agrupar por los demás campos
        l_campos.remove('reng_num')
        l_campos.remove('co_art')
        l_campos.remove('cod_art_izq')
        lista_cifras= ['monto_base_item',
                    'iva', 
                    'total_item', 
                    'saldo_total_doc']
        """
            elimina los campos correspondientes a las CIFRAS para que no los agrupe,
            no se incluye los campos 'igtf' y 'igtf$' ya que en este caso si queremos
            que los agrupe por ser montos totales.
        """

        for elem_a_eliminar in lista_cifras:
            l_campos.remove(elem_a_eliminar)
        #  Cuidado con este GroupBy ya que si existen valores vacios en cualquier campo imite esos registros 
        return df_fact.groupby(l_campos, sort=False)[lista_cifras].sum().reset_index()


    def variacion_tasa_en_cobros(self, **kwargs):
        anio, mes = kwargs.get('anio', 2023), kwargs.get('mes', 'all')
        l_campos = ['nro_doc', 'co_cli', 'cli_des', 'f_reg_doc', 'f_cobro', 'dias_transc', 'cob_num', 'forma_pag',
                    'cod_cta', 'cod_caja', 'mont_cob_dc', 'm_base$', 'm_base_cob$', 'variacion$', 'porc_cobrado']
        where_all = f"WHERE fp.forma_pag IS NOT NULL AND RTrim(d.co_tipo_doc) In ('FACT','N/CR') AND YEAR(d.fec_reg)={anio}"
        where_mes = f"WHERE fp.forma_pag IS NOT NULL AND RTrim(d.co_tipo_doc) In ('FACT','N/CR') AND YEAR(d.fec_reg)={anio} AND MONTH(d.fec_reg)={mes}"
        where = where_all if mes == 'all' else where_mes
        sql = (
            """
                SELECT RTRIM(d.nro_doc) AS nro_doc, RTRIM(d.co_cli) AS co_cli, cl.cli_des, d.fec_reg as f_reg_doc, 
                    cb.fecha AS f_cobro, RTRIM(dcb.cob_num) AS cob_num, fp.forma_pag, RTRIM(fp.cod_cta) as cod_cta, RTRIM(fp.cod_caja) as cod_caja, 
                    (d.total_bruto-d.monto_desc_glob) as m_base, dcb.mont_cob as mont_cob_dc, d.total_neto AS total_doc,
                    Round(dcb.mont_cob/d.total_neto,6) AS porc_cobrado
                FROM (((saDocumentoVenta AS d LEFT JOIN saCobroDocReng AS dcb ON d.nro_doc = dcb.nro_doc)
                    LEFT JOIN saCobroTPReng AS fp ON dcb.cob_num = fp.cob_num)
                    LEFT JOIN saCobro AS cb ON dcb.cob_num = cb.cob_num)
                    INNER JOIN saCliente AS cl ON d.co_cli = cl.co_cli 
            """
            + where
        )
        df = get_read_sql(sql, self.conexion)
        df['f_reg_doc'] = to_datetime(df['f_reg_doc']).dt.normalize()  # fecha sin hora, minutos y segundos
        df_bcv = historico_tasas_bcv()[['venta_ask2', 'fecha']]  # archivo BCV
        bcv_tasas = df_bcv.sort_values(by=['fecha'], ascending=[True])  # se debe ordenar el df para poder conbinar
        dc = df.sort_values(by=['f_reg_doc'], ascending=[True])  # se debe ordenar el df para poder conbinar
        merge_data1 = merge_asof(dc, bcv_tasas, left_on='f_reg_doc', right_on='fecha', direction="nearest")  # Combinar por aproximación
        merge_data1.rename(columns={'venta_ask2': 'venta_ask2_doc'}, inplace=True)
        merge_data1.rename(columns={'fecha': 'fecha_bcv_doc'}, inplace=True)
        merge_data1['mont_cob_doc$'] = merge_data1.apply(lambda x: x['mont_cob_dc'] / x['venta_ask2_doc'], axis=1)
        merge_data1['total_doc$'] = merge_data1.apply(lambda x: x['total_doc'] / x['venta_ask2_doc'], axis=1)
        merge_data1['m_base$'] = merge_data1.apply(lambda x: (x['m_base'] * x['porc_cobrado']) / x['venta_ask2_doc'], axis=1)
        merge_data_sort = merge_data1.sort_values(by=['f_cobro'], ascending=[True])  # se debe ordenar el df para poder conbinar
        data = merge_asof(merge_data_sort, bcv_tasas, left_on='f_cobro', right_on='fecha',
                        direction="nearest")  # Combinar por aproximación
        data.rename(columns={'venta_ask2': 'venta_ask2_cob'}, inplace=True)
        data.rename(columns={'fecha': 'fecha_bcv_cob'}, inplace=True)
        data['mont_cob$'] = data.apply(lambda x: x['mont_cob_dc'] / x['venta_ask2_cob'], axis=1)
        data['m_base_cob$'] = data.apply(lambda x: (x['m_base'] * x['porc_cobrado']) / x['venta_ask2_cob'], axis=1)
        data_sort = data.sort_values(by=['nro_doc'], ascending=[False])  # se debe ordenar el df para poder conbinar
        data_sort['variacion$'] = data_sort.apply(lambda x: round(x['m_base$'] - x['m_base_cob$'], ndigits=2), axis=1)
        data_sort["dias_transc"] = (data_sort["f_cobro"] - data_sort["f_reg_doc"]).dt.days  # Dias transcurridos entre la ultima fecha al dia de hoy
        print('\n' * 1, 'Diferencia total$= ', round(data_sort['variacion$'].sum(), ndigits=2))
        return data_sort[l_campos]

    def variacion_tasa_en_cobros_por_mes(self, **kwargs):
        anio = kwargs.get('anio', 2023)
        df = self.variacion_tasa_en_cobros(anio=anio)
        df['anio'] = df['f_reg_doc'].dt.year
        df['mes'] = df['f_reg_doc'].dt.month
        group = df.groupby(['anio', 'mes'])['variacion$'].sum().reset_index()
        print('\n' * 1, 'Variacion de tasa promedio mensual$= ', round(group['variacion$'].mean(), ndigits=2))
        return group

    def facturacion_por_cod_art(self, **kwargs) -> DataFrame:
        """
        --> Obtiene la facturación resumida de los campos
            'cod_art_izq' y 'monto_base_item$'
        """
        anio, mes, conv_usd = kwargs.get('anio', 'all'), kwargs.get('mes', 'all'), kwargs.get('usd', True)
        det_fact = self.ventas_con_detalle(anio=anio, mes=mes, usd=conv_usd).copy()
        return (
            det_fact.groupby('cod_art_izq')[['monto_base_item$']]
            .sum()
            .reset_index()
        )

    def facturacion_x_cliente(self, anio=2023):
        doc = self.ventas_con_detalle(anio=anio, mes='all', usd=True).copy()
        # Listado de tipos de Documentos que deben ser tomados en cuenta para el calculo del impuesto CONATEL
        docs_tipos = ['FACT', 'N/CR', 'N/DB']
        # Varifica si los elementos o valores de la columna "co_tipo_doc" existen dentro de la lista "docs_tipos"
        doc_leg = doc[doc['co_tipo_doc'].isin(docs_tipos)]
        doc_leg['anio'] =  doc_leg['fec_reg'].dt.year  # Obtiene el año
        doc_g2 = doc_leg.groupby(['anio', 'co_cli'])[['monto_base_item', 'monto_base_item$']].sum().reset_index()
        return doc_g2.sort_values(
            by=['monto_base_item', 'co_cli'], ascending=[False, False]
        ).reset_index(drop=True)

    def facturacion_x_anio(self, **kwargs):
        anio, mes, conv_usd = kwargs.get('anio', 'all'), kwargs.get('mes', 'all'), kwargs.get('usd', True)
        doc = self.ventas_con_detalle(anio=anio, mes=mes, usd=conv_usd).copy()
        # Listado de tipos de Documentos que deben ser tomados en cuenta para el calculo del impuesto CONATEL
        docs_tipos = ['FACT', 'N/CR', 'N/DB']
        # Varifica si los elementos o valores de la columna "co_tipo_doc" existen dentro de la lista "docs_tipos"
        doc_leg = doc[doc['co_tipo_doc'].isin(docs_tipos)]
        doc_leg['anio'] = doc_leg['fec_reg'].dt.year  # Obtiene el año
        doc_leg['mes'] = doc_leg['fec_reg'].dt.month  # Obtiene el mes
        doc_g2 = doc_leg.groupby(['anio', 'mes'])[['monto_base_item', 'total_item']].sum().reset_index()
        return doc_g2.sort_values(
            by=['anio', 'mes', 'monto_base_item'], ascending=[False, False, False]
        ).reset_index()
    
    def facturacion_x_anio_vend(self, **kwargs):
        anio, mes, vend, conv_usd = kwargs.get('anio', 'all'), kwargs.get('mes', 'all'), kwargs.get('vendedor', 'all'), kwargs.get('usd', True)
        doc = self.ventas_con_detalle(anio=anio, mes=mes, usd=conv_usd).copy()
        # Listado de tipos de Documentos que deben ser tomados en cuenta para el calculo del impuesto CONATEL
        docs_tipos = ['FACT', 'N/CR', 'N/DB']
        # Varifica si los elementos o valores de la columna "co_tipo_doc" existen dentro de la lista "docs_tipos"
        if vend == 'all':
            doc_leg = doc[doc['co_tipo_doc'].isin(docs_tipos)]
        else:
            doc_leg = doc[doc['co_tipo_doc'].isin(docs_tipos) & (doc['co_tipo_doc'] == vend)]

        doc_leg['anio'] = doc_leg['fec_reg'].dt.year  # Obtiene el año
        doc_leg['mes'] = doc_leg['fec_reg'].dt.month  # Obtiene el mes
        doc_g2 = doc_leg.groupby(['anio', 'mes', 'co_ven'])[['monto_base_item', 'total_item']].sum().reset_index()
        return doc_g2.sort_values(
            by=['anio', 'mes', 'co_ven', 'monto_base_item'],
            ascending=[False, False, False, False],
        ).reset_index()

    def articulos_profit(self):
        sql = """
                Select RTRIM(co_art) as co_art, art_des, campo1, anulado, dis_cen, tipo_imp 
                from saArticulo
            """
        df = get_read_sql(sql, self.conexion)
        return DataFrame(df)

    def articulos_profit_con_su_cuenta_contable(self):
        df = self.articulos_profit()
        art_profit = DataFrame(df)
        art_con_cta_asignada = art_profit[art_profit['dis_cen'].notnull()].copy()
        #  Desempaqueta la cuenta contable del texto xml
        art_con_cta_asignada['co_cta_cont'] = art_con_cta_asignada['dis_cen'].apply(
            lambda x: str(xml_tree.fromstring(x).findtext('Carpeta03/CuentaContable')))
        return art_con_cta_asignada

    def plan_cta(self):
        return get_read_sql("Select * from sccuenta", **self.dict_con_contab)


    def detalle_comprob(self):
        return get_read_sql("Select * from scren_co", **self.dict_con_contab)

    def _extrae_numero(self, string_num):
        # Extrae los números dentro de la cadena de texto
        num = findall('[0-9.]+', string_num)
        return str(int(num[0]) + 1)

    def get_id_movbanco(self):
        df = get_read_sql("Select mov_num from saMovimientoBanco "
                        "where origen='BAN'")
        mb = df['mov_num'].max()
        return 'MB' + self._extrae_numero(mb)

    def get_movbanco(self, fecha_inicio_mes):
        fecha_ini = fecha_inicio_mes
        fecha_final = ultimo_dia_mes(to_datetime(fecha_inicio_mes))
        sql = f"""SELECT mov_num, descrip, cod_cta, co_cta_ingr_egr, fecha, doc_num, monto_d, monto_h, idb, cob_pag, 
                        anulado, co_us_in, fe_us_in, co_us_mo, fe_us_mo 
                FROM saMovimientoBanco 
                WHERE fecha>='{fecha_ini}' AND fecha<='{fecha_final}'
            """
        return get_read_sql(sql, self.conexion)

    def search_in_movbanco(self, **kwargs):
        str_search, anio, mes = kwargs.get('texto_a_buscar'), kwargs.get('anio', 'all'), kwargs.get('mes', 'all')  

        fields_mov_bco = ['mov_num', 'fecha', 'cod_cta', 'descrip', 'co_cta_ingr_egr',
                        'doc_num', 'monto_d', 'monto_h', 'idb', 'USD']

        where_anio = f"" if anio == 'all' else f"WHERE year(fecha)='{anio}'"
        where_all = f"" + where_anio
        where_mes = f"WHERE year(fecha)='{anio}' and month(fecha)='{mes}'"
        where = where_all if mes == 'all' else where_mes

        sql = f"""
            SELECT RTRIM(mov_num) as mov_num, descrip, cod_cta, RTRIM(co_cta_ingr_egr) as co_cta_ingr_egr, fecha, doc_num, monto_d, monto_h, idb, cob_pag, anulado, 
                    campo1, campo2, campo3, campo4, campo5, campo6, campo7, co_us_in, fe_us_in, co_us_mo, fe_us_mo       
            FROM saMovimientoBanco
            {where}
            """
        df = get_read_sql(sql, self.conexion)
        df['descrip'] = df['descrip'].str[:80]  # Extrae los primeros 80 caracteres de la izquierda
        file_bcv = historico_tasas_bcv()  # archivo BCV
        file_bcv.rename(columns={'fecha': 'fecha2'}, inplace=True)
        resul_sor = df.sort_values(by=['fecha'], ascending=[True])  # se debe ordenar el df para poder conbinar
        tasas_cambio_s = file_bcv.sort_values(by=['fecha2'], ascending=[True])  # se debe ordenar el df para poder conbinar
        merge_data = merge_asof(resul_sor, tasas_cambio_s, left_on='fecha', right_on='fecha2', direction="nearest")  # Combinar por aproximación
        # es necesario colocar axis=1 para que solo evalue las columnas indicadas en la funcion lambda
        merge_data['USD'] = merge_data.apply(lambda x: (x['monto_d']+x['monto_h']) / x['venta_ask2'], axis=1)
        merge_data['USD'] = merge_data['USD'].apply('${:,.2f}'.format)  # Se aplica formato de $ float
        return search_df(str_search, merge_data)[fields_mov_bco]

    def search_clients(self, str_search, **kwargs):
        df = self.clientes()
        df['co_cli'] = df['co_cli'].str.strip()
        df['fe_us_in'] = to_datetime(df['fe_us_in']).dt.normalize()
        resul = search_df(str_search, df)[['co_cli', 
                                           'cli_des', 
                                           'rif', 
                                           'dir_ent2', 
                                           'telefonos', 
                                           'respons', 
                                           'direc1', 
                                           'fe_us_in', 
                                           'campo3',
                                           'matriz']]
        if kwargs.get('resumir_datos', False):
            resul['cli_des'] = resul['cli_des'].str[:30]  # Extrae los primeros 40 caracteres de la izquierda
            resul['direc1'] = resul['direc1'].str[:20]  # Extrae los primeros 40 caracteres de la izquierda
        return resul

    def clientes(self):
        sql = """
                SELECT  RTRIM([co_cli]) as co_cli
                    ,RTRIM([tip_cli]) as tip_cli
                    ,[cli_des]
                    ,[direc1]
                    ,[dir_ent2]
                    ,[direc2]
                    ,[telefonos]
                    ,[fax]
                    ,[inactivo]
                    ,[comentario]
                    ,[respons]
                    ,[fecha_reg]
                    ,[puntaje]
                    ,[mont_cre]
                    ,[co_mone]
                    ,[cond_pag]
                    ,[plaz_pag]
                    ,[desc_ppago]
                    ,[co_zon]
                    ,[co_seg]
                    ,[co_ven]
                    ,[desc_glob]
                    ,[horar_caja]
                    ,[frecu_vist]
                    ,[lunes]
                    ,[martes]
                    ,[miercoles]
                    ,[jueves]
                    ,[viernes]
                    ,[sabado]
                    ,[domingo]
                    ,[rif]
                    ,[nit]
                    ,[contrib]
                    ,[numcom]
                    ,[feccom]
                    ,[dis_cen]
                    ,[email]
                    ,[co_cta_ingr_egr]
                    ,[juridico]
                    ,[tipo_adi]
                    ,[matriz]
                    ,[co_tab]
                    ,[tipo_per]
                    ,[valido]
                    ,[ciudad]
                    ,[zip]
                    ,[login]
                    ,[password]
                    ,[website]
                    ,[sincredito]
                    ,[contribu_e]
                    ,[rete_regis_doc]
                    ,[porc_esp]
                    ,[co_pais]
                    ,[serialp]
                    ,[Id]
                    ,[salestax]
                    ,[estado]
                    ,[campo1]
                    ,[campo2]
                    ,[campo3]
                    ,[campo4]
                    ,[campo5]
                    ,[campo6]
                    ,[campo7]
                    ,[campo8]
                    ,[co_us_in]
                    ,[fe_us_in]
                    ,[co_sucu_in]
                    ,[co_us_mo]
                    ,[fe_us_mo]
                    ,[co_sucu_mo] 
                FROM [dbo].[saCliente]  
            """
        return get_read_sql(sql, self.conexion)
    
    def vendedores(self):
        sql = """
            SELECT co_ven, RTRIM(ven_des) as ven_des, campo1  
            FROM saVendedor 
            """
        return get_read_sql(sql, self.conexion)
    
    def proveedores(self):
        sql = """
            SELECT  RTRIM(co_prov) as co_prov, RTRIM(prov_des) as prov_des, direc1, direc2, telefonos, fax,
                    respons, fecha_reg, plaz_pag, rif, email, tipo_per, ciudad, zip, website, contribu_e, porc_esp, 
                    co_us_in, fe_us_in, co_us_mo, fe_us_mo 
            FROM saProveedor
            """
        return get_read_sql(sql, self.conexion)

    def search_in_compras(self, **kwargs) -> DataFrame:
        # sourcery skip: class-extract-method
        anio, mes = kwargs.get('anio', 'all'), kwargs.get('mes', 'all')
        text_to_search = kwargs.get('str_search', '')
        fields_fact = ['doc_num', 'nro_fact', 'fec_emis', 'co_prov', 'prov_des',
                    'descrip', 'monto_base_item', 'iva', 'igtf', 'total_item',
                    'USD_BASE', 'USD_IVA', 'USD_TOTAL', 'USD_IGTF']

        df = self.factura_compra_con_su_detalle(anio=anio, mes=mes)
        # Permite convertir la fecha o el tiempo a 00:00:00, debes usar dt.normalizeodt.floor
        df['fec_emis'] = to_datetime(df['fec_emis']).dt.normalize()
        resul = search_df(text_to_search, df)  # df con el resultado de la busqueda
        resul_sor = resul.sort_values(by=['fec_emis'],
                                    ascending=[True])  # se debe ordenar el df para poder conbinar
        file_bcv = historico_tasas_bcv()  # archivo BCV
        tasas_cambio_s = file_bcv.sort_values(by=['fecha'],
                                            ascending=[True])  # se debe ordenar el df para poder conbinar
        merge_data = merge_asof(resul_sor, tasas_cambio_s, left_on='fec_emis', right_on='fecha',
                                direction="nearest")  # Combinar por aproximación
        # es necesario colocar axis=1 para que solo evalue las columnas indicadas en la funcion lambda
        merge_data['USD_BASE'] = merge_data.apply(lambda x: x['monto_base_item'] / x['venta_ask2'], axis=1)
        merge_data['USD_IVA'] = merge_data.apply(lambda x: x['iva'] / x['venta_ask2'], axis=1)
        merge_data['USD_TOTAL'] = merge_data.apply(lambda x: x['total_item'] / x['venta_ask2'], axis=1)
        merge_data['USD_IGTF'] = merge_data.apply(lambda x: x['igtf'] / x['venta_ask2'], axis=1)
        print(round(merge_data['USD_BASE'].sum(), ndigits=2))
        return merge_data[fields_fact]


    def search_in_ventas(self, **kwargs):
        anio, mes = kwargs.get('anio', 'all'), kwargs.get('mes', 'all')
        text_to_search = kwargs.get('str_search', '')
        print(f"\n Los resultados de '{text_to_search}' en la facturación son los siguientes: ")
        campos_fact = ['doc_num', 'fec_emis', 'co_cli', 'cli_des',
                        'descrip', 'monto_base_item', 'iva', 'igtf', 'total_item',
                        'USD_BASE', 'USD_IVA', 'USD_IGTF', 'USD_TOTAL', 'saldo_total_doc', 'saldo_total_doc$']
        facturas = self.ventas_con_detalle(anio=anio, mes=mes, usd=True).copy()
        facturas['fec_emis'] = to_datetime(facturas['fec_emis']).dt.normalize()  # fecha sin hora, minutos y segundos
        resul = search_df(text_to_search, facturas) #  buscar texto dentro de la facturacion
        resul_sor = resul.sort_values(by=['fec_emis'], ascending=[True])  # se debe ordenar el df para poder conbinar
        file_bcv = historico_tasas_bcv()  # archivo BCV
        tasas_cambio_s = file_bcv.sort_values(by=['fecha'], ascending=[True])  # se debe ordenar el df para poder conbinar
        merge_data = merge_asof(resul_sor, tasas_cambio_s, left_on='fec_emis', right_on='fecha', direction="nearest")  # Combinar por aproximación    
        # es necesario colocar axis=1 para que solo evalue las columnas indicadas en la funcion lambda
        merge_data['USD_BASE'] = merge_data.apply(lambda x: x['monto_base_item'] / x['venta_ask2'], axis=1)
        merge_data['USD_IVA'] = merge_data.apply(lambda x: x['iva'] / x['venta_ask2'], axis=1)
        merge_data['USD_TOTAL'] = merge_data.apply(lambda x: x['total_item'] / x['venta_ask2'], axis=1)
        merge_data['USD_IGTF'] = merge_data.apply(lambda x: x['igtf'] / x['venta_ask2'], axis=1)
        print('monto_base_item:', round(merge_data['monto_base_item'].sum(), 2))
        print('total_item:', round(merge_data['total_item'].sum(), 2))
        merge_data['saldo_total_doc'] = merge_data.apply(lambda x: x['total_item'] if x['saldo_total_doc'] != 0.0 else 0.0, axis=1)
        print('saldo_total_doc:', round(merge_data['saldo_total_doc'].sum(), 2))
        print('USD_BASE:', round(merge_data['USD_BASE'].sum(), 2))
        print('USD_TOTAL:', round(merge_data['USD_TOTAL'].sum(), 2))
        merge_data['saldo_total_doc$'] = merge_data.apply(lambda x: x['USD_TOTAL'] if x['saldo_total_doc$'] != 0.0 else 0.0, axis=1)
        print('saldo_total_doc$:', round(merge_data['saldo_total_doc$'].sum(), 2))
        merge_data['cli_des'] = merge_data['cli_des'].str[:50]  # Extrae los primeros 50 caracteres de la izquierda
        return merge_data[campos_fact]


    def conjunto_ref_mov_bcrios(self, fecha_inicio_mes):
        df = self.get_movbanco(fecha_inicio_mes)
        return set(df['doc_num'])


    def get_monto_tasa_bcv_del_dia(self):
        df_data_bcv = historico_tasas_bcv()  # archivo BCV
        fila_tasa_dia = df_data_bcv[df_data_bcv['fecha'] == df_data_bcv['fecha'].max()]
        return float(fila_tasa_dia['venta_ask2'].iloc[0])

    def get_fecha_tasa_bcv_del_dia(self):
        df_data_bcv = historico_tasas_bcv()  # archivo BCV
        return df_data_bcv['fecha'].iloc[0]

    def get_monto_tasa_bcv_fecha(self, fecha_oper):
        fecha_operacion = to_datetime(fecha_oper)
        df_data_bcv = historico_tasas_bcv()  # archivo BCV
        fila_tasa_dia = df_data_bcv[df_data_bcv['fecha'] == fecha_operacion]
        print('Tasa BCV al:', fila_tasa_dia['fecha'].iloc[0])
        return float(fila_tasa_dia['venta_ask2'].iloc[0])

    def factura_compra_con_su_detalle(self, **kwargs):
        anio, mes = kwargs.get('anio', '2023'), kwargs.get('mes', 'all')
        where_anio = f"" if anio == 'all' else f" AND year(fact.fec_reg)='{anio}'"
        where_all = "WHERE fact.[anulado]=0 " + where_anio
        where_mes = f"WHERE fact.[anulado]=0 AND year(fact.fec_reg)='{anio}' and month(fact.fec_reg)='{mes}'"
        where = where_all if mes == 'all' else where_mes
        sql = f"""
            SELECT RTRIM(fact.doc_num) as doc_num, RTRIM(fact.nro_fact) as nro_fact, RTRIM(dfact.co_art) as co_art, RTRIM(art.campo1) as cod_art_izq,
                    fact.fec_emis, fact.fec_reg, fact.fec_venc, fact.descrip,
                    year(fact.fec_reg) AS anio, month(fact.fec_reg) AS mes, RTRIM(fact.co_prov) as co_prov,
                    RTRIM(c.prov_des) as prov_des, (dfact.reng_neto-dfact.monto_desc_glob) AS monto_base_item,
                    (dfact.monto_imp+dfact.monto_imp_afec_glob) as iva,
                    ((dfact.reng_neto-dfact.monto_desc_glob)+(dfact.monto_imp+dfact.monto_imp_afec_glob)) as total_item,
                    fact.otros1 as igtf, fact.saldo as saldo_total_doc
            FROM saFacturaCompra AS fact INNER JOIN saFacturaCompraReng AS dfact ON
                    fact.doc_num = dfact.doc_num LEFT JOIN saArticulo AS art ON
                    dfact.co_art = art.co_art LEFT JOIN saProveedor AS c ON fact.co_prov = c.co_prov 
            {where} 
            ORDER BY fact.fec_reg, fact.doc_num
            """
        fact_det = get_read_sql(sql, self.conexion)
        fact_det['co_tipo_doc'] = 'FACT'
        return fact_det

    def get_last__nro_fact_venta(self):
        sql = """
                SELECT RTRIM(doc_num) as doc_num, RTRIM(n_control) as n_control
                FROM saFacturaVenta 
                WHERE doc_num in (SELECT MAX(RTRIM(doc_num)) 
                                FROM saFacturaVenta)
            """
        return get_read_sql(sql, self.conexion)        
    
    #  Facturas de ventas parcialmente cobradas o sin cobro
    def facturacion_saldo_x_clientes_detallado(self, **kwargs):
        l_campos= self.campos_comunes_fact.copy()
        l_campos.extend(['saldo_total_doc'])
        l_campos.extend(['total_item'])
        anio, mes, dato_cliente, conv_usd = kwargs.get('anio', 'all'), kwargs.get('mes', 'all'), kwargs.get('dato_cliente', 'all'), kwargs.get('usd', True)
        vendedor = kwargs.get('vendedor', 'all')
        df_fact = self.ventas_sin_detalle(anio=anio, mes=mes, usd=conv_usd)
        df_fact_con_saldo = df_fact[df_fact['saldo_total_doc'] != 0][l_campos]
        df_fact_con_saldo_f= df_fact_con_saldo
        #  Permite filtrar por codigo de cliente o nombre del cliente
        if dato_cliente != 'all':
            df_fact_con_saldo_f= df_fact_con_saldo[(df_fact_con_saldo['co_cli'].str.contains(dato_cliente)) | (df_fact_con_saldo['cli_des'].str.contains(dato_cliente))].copy()

        today = datetime.now()
        df_fact_con_saldo_f["dias_transc"] = (today - df_fact_con_saldo_f['fec_reg']).dt.days  # Dias transcurridos entre la ultima fecha al dia de hoy

        return (
            df_fact_con_saldo_f
            if vendedor == 'all'
            else df_fact_con_saldo_f[df_fact_con_saldo_f['ven_des'] == vendedor]
        )
            
    #  Facturas de ventas parcialmente cobradas o sin cobro        
    def cxc_clientes_resum_pivot(self, **kwargs):
        anio, mes, conv_usd = kwargs.get('anio', 'all'), kwargs.get('mes', 'all'), kwargs.get('usd', True)
        vendedor = kwargs.get('vendedor', 'all')
        df_fact = self.facturacion_saldo_x_clientes_detallado(anio=anio, mes=mes, usd=conv_usd, vendedor=vendedor)
        df_fact['anio'] =  df_fact['fec_reg'].dt.year  # Obtiene el año
        locale.setlocale(locale.LC_ALL, 'es_ES')
        df_fact['mes'] = df_fact['fec_reg'].dt.month_name(locale='es_ES').str[:3]
        locale.setlocale(locale.LC_ALL, '')
        return pivot_table(
            df_fact,
            values='saldo_total_doc',
            index=['cli_des'],
            columns=['anio', 'mes'],
            aggfunc='sum',
            margins=True,
            sort=False,
        ).replace(nan, 0)

    #  Facturas de ventas parcialmente cobradas o sin cobro
    def cxc_clientes_resum_grouped(self, **kwargs):
        anio, mes, conv_usd, vendedor = kwargs.get('anio', 'all'), kwargs.get('mes', 'all'), kwargs.get('usd', True), kwargs.get('vendedor', 'all')
        df_fact = self.facturacion_saldo_x_clientes_detallado(anio=anio, mes=mes, usd=conv_usd, vendedor=vendedor)
        df_fact['anio'] =  df_fact['fec_reg'].dt.year  # Obtiene el año
        locale.setlocale(locale.LC_ALL, 'es_ES')
        df_fact['mes'] = df_fact['fec_reg'].dt.month_name(locale='es_ES').str[:3]
        locale.setlocale(locale.LC_ALL, '')
        df_x_vendedor = df_fact if vendedor == 'all' else df_fact[df_fact['ven_des']]
        return (
            df_x_vendedor.groupby(
                ['cli_des', 'anio', 'mes', 'co_ven', 'ven_des'], sort=False
            )[['total_item', 'saldo_total_doc']]
            .sum()
            .reset_index()
        )

    #  Facturas de ventas parcialmente cobradas o sin cobro    
    def dicc_ventas_total_por_anio(self, **kwargs):
        anio, conv_usd = kwargs.get('anio', 2023), kwargs.get('usd', False)
        df_fact = self.facturacion_x_anio(usd=conv_usd).groupby('anio')[['monto_base_item']].sum().reset_index()
        df_fact.set_index(['anio'], inplace=True)
        return round(df_fact.loc[anio, 'monto_base_item'], ndigits=2)
    
    #  Facturas de ventas parcialmente cobradas o sin cobro    
    def dicc_ventas_total_por_anio_vendedor(self, **kwargs):
        anio, vend, conv_usd = kwargs.get('anio', 2023), kwargs.get('vendedor', '0001'), kwargs.get('usd', False)
        df_fact = self.facturacion_x_anio_vend(usd=conv_usd).groupby(['anio', 'co_ven'])[['monto_base_item']].sum().reset_index()
        df_fact.set_index(['anio', 'co_ven'], inplace=True)
        
        if vend == 'Todos':
            ventas_anio_vend = round(df_fact.loc[(anio), 'monto_base_item'], ndigits=2)
        else:
            try:
                ventas_anio_vend = round(df_fact.loc[(anio, vend), 'monto_base_item'], ndigits=2)
            except KeyError:
                ventas_anio_vend = 0.0
                
        return ventas_anio_vend
    

    def new_cod_client(self):
        clients = self.clientes()[['co_cli']]
        patron = r"[A-Za-z]{2}\d{1,3}$"  # Patron para ubicar los clientes NO AGRUPADOS ejemplo: CL95 sin el guion
        clientes_filtro = clients[clients['co_cli'].str.contains(patron, regex=True)].copy() # Se debe especificar que se está trabajando con expresiones regulares
        clientes_filtro['num_cod_client'] = clientes_filtro.apply(lambda x: findall('[0-9.]+', x['co_cli'])[0], axis=1) # Extrae los números contenidos en la cadena o string
        clientes_filtro['num_cod_client']=clientes_filtro['num_cod_client'].astype("int64") 
        id_new_client= clientes_filtro['num_cod_client'].max() + 1
        return f"CL{id_new_client}"
    
    def data_nota_entrega_con_detalle(self, **kwargs):
            anio, mes = kwargs.get('anio'), kwargs.get('mes')
            where_anio = f"" if anio == 'all' else f" AND year(fact.fec_reg)='{anio}'"
            where_all = "WHERE fact.[anulado]=0 " + where_anio
            where_mes = f"WHERE fact.[anulado]=0 AND year(fact.fec_reg)='{anio}' and month(fact.fec_reg)='{mes}'"
            where = where_all if mes == 'all' else where_mes
            sql = f"""
                SELECT reng_num, RTRIM(fact.doc_num) as doc_num, RTRIM(dfact.co_art) as co_art, RTRIM(art.campo1) as cod_art_izq,
                        fact.fec_emis, fact.fec_reg, fact.descrip,
                        year(fact.fec_reg) AS anio, month(fact.fec_reg) AS mes, RTRIM(fact.co_ven) as co_ven, RTRIM(fact.co_cli) as co_cli,
                        c.cli_des, (v.ven_des + iif(v.campo1 <> '', + ' -> ' + v.campo1, '')) as ven_des, (dfact.reng_neto-dfact.monto_desc_glob) AS monto_base_item,
                        (dfact.monto_imp+dfact.monto_imp_afec_glob) as iva,
                        ((dfact.reng_neto-dfact.monto_desc_glob)+(dfact.monto_imp+dfact.monto_imp_afec_glob)) as total_item,
                        iif(reng_num=1, fact.otros1, 0) as igtf, fact.saldo as saldo_total_doc 
                FROM saFacturaVenta AS fact INNER JOIN saFacturaVentaReng AS dfact ON
                        fact.doc_num = dfact.doc_num LEFT JOIN saArticulo AS art ON
                        dfact.co_art = art.co_art LEFT JOIN saCliente AS c ON fact.co_cli = c.co_cli LEFT JOIN saVendedor as v ON fact.co_ven = v.co_ven  
                {where} 
                ORDER BY fact.fec_reg, fact.doc_num
                """
            fact_det = get_read_sql(sql, self.conexion)
            fact_det['co_tipo_doc'] = 'FACT'
            return fact_det