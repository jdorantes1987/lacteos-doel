from scripts.sql_read import get_read_sql

class FacturaVentasConsultas:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def data_factura_venta_con_detalle(self, **kwargs):
        fecha_d, fecha_h = kwargs.get('fecha_d', 'all'), kwargs.get('fecha_h', 'all')
        tip_cli = kwargs.get('tip_cli', 'all')
        condicion_tipo_cliente = "c.tip_cli=c.tip_cli" if tip_cli == 'all' else f"c.tip_cli = '{tip_cli}'"
        all_records = True if fecha_d == 'all' or fecha_h == 'all' else False
        # La funcion integrada CAST permite convertir fechas sin minutos y segundos
        where = f"WHERE fact.anulado=0 AND {condicion_tipo_cliente}" if all_records else f"WHERE fact.anulado=0 AND CAST(fact.fec_emis AS DATE) >= '{fecha_d}' and CAST(fact.fec_emis AS DATE) <='{fecha_h}' AND {condicion_tipo_cliente}"
        sql_mov = f"""
            SELECT reng_num, RTRIM(fact.doc_num) as doc_num, 
                    RTRIM(dfact.co_art) as co_art, art.art_des,
                    fact.fec_emis, fact.fec_reg, fact.descrip,
                    year(fact.fec_reg) AS anio, 
                    month(fact.fec_reg) AS mes, 
                    RTRIM(fact.co_ven) as co_ven, 
                    RTRIM(fact.co_cli) as co_cli, 
                    RTRIM(fact.co_tran) AS co_tran, c.cli_des, 
                    RTRIM(c.tip_cli) as tip_cli, v.ven_des, t.des_tran, 
                    RTRIM(dfact.co_alma) as co_alma, 
                    RTRIM(dfact.co_precio) as co_precio, 
                    RTRIM(dfact.co_uni) as co_uni,
                    au.equivalencia, au.relacion as es_unidad, dfact.total_art, 
                    ap.monto as art_monto, 
                    ROUND(ap.monto/au.equivalencia, 4) art_monto_uni, dfact.prec_vta, 
                    iif(reng_num=1, ROUND(fact.total_neto - fact.saldo, 4), 0) as monto_abonado, 
                    (dfact.reng_neto) AS monto_base_item,
                    (dfact.monto_imp) as iva,
                    (dfact.reng_neto + dfact.monto_imp) as total_item,
                    iif(reng_num=1, fact.otros1, 0) as igtf, 
                    iif(reng_num=1, fact.saldo, 0) as saldo_total_doc, 
                    iif(fact.campo8 <> '', fact.campo8, 'DEV') as campo8, RTRIM(num_doc) as num_doc, 
                    RTRIM(tipo_doc) as tipo_doc_origen, 0 as es_saldo_ant 
            FROM    (saFacturaVenta AS fact INNER JOIN saFacturaVentaReng AS dfact ON
                    fact.doc_num = dfact.doc_num) 
                    LEFT JOIN saArtPrecio as ap ON dfact.co_art = ap.co_art AND dfact.co_precio = ap.co_precio
                    LEFT JOIN saArtUnidad as au ON dfact.co_art = au.co_art AND dfact.co_uni = au.co_uni 
                    LEFT JOIN saArticulo AS art ON dfact.co_art = art.co_art 
                    LEFT JOIN saCliente AS c ON fact.co_cli = c.co_cli 
                    LEFT JOIN saVendedor as v ON fact.co_ven = v.co_ven
                    LEFT JOIN saTransporte as t ON fact.co_tran = t.co_tran 

            {where} 
            ORDER BY fact.fec_reg, fact.doc_num
            """
        fact_det = get_read_sql(sql_mov, self.conexion)
        fact_det['co_tipo_doc'] = 'FACT'
        return fact_det
        
    def data_factura_venta_sin_ruta(self, **kwargs):
        fecha_d, fecha_h = kwargs.get('fecha_d', 'all'), kwargs.get('fecha_h', 'all')
        if fecha_d == 'all':
           fecha_d = 'NULL'
           fecha_h = 'NULL'
        sql = f"""
            EXEC RepFacturaVentaxFecha
            @dCo_fecha_d = '{fecha_d}',
            @dCo_fecha_h = '{fecha_h}', 
            @cCo_Transporte_d = N'NA',
            @cCo_Transporte_h = N'NA',
            @cAnulado = N'NOT'
        """
        sql = sql.replace("'NULL'", 'NULL')
        ventas = get_read_sql(sql, self.conexion)
        return ventas