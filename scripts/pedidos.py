from scripts.sql_read import get_read_sql

class PedidosVentasConsultas:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def data_pedido_con_detalle(self, **kwargs):
            anio, mes = kwargs.get('anio'), kwargs.get('mes')
            where_anio = f"" if anio == 'all' else f" AND year(ped.fec_reg)='{anio}'"
            where_all = "WHERE ped.anulado=0 " + where_anio
            where_mes = f"WHERE ped.anulado=0 AND year(ped.fec_reg)='{anio}' and month(ped.fec_reg)='{mes}'"
            where = where_all if mes == 'all' else where_mes
            sql = f"""
                SELECT reng_num, RTRIM(ped.doc_num) as doc_num, RTRIM(dped.co_art) as co_art, art.art_des,
                        ped.fec_emis, ped.fec_reg, ped.descrip,
                        year(ped.fec_reg) AS anio, month(ped.fec_reg) AS mes, RTRIM(ped.co_ven) as co_ven, RTRIM(ped.co_cli) as co_cli, 
                        RTRIM(ped.co_tran) AS co_tran, c.cli_des, v.ven_des, t.des_tran, RTRIM(dped.co_alma) as co_alma, RTRIM(dped.co_precio) as co_precio, RTRIM(dped.co_uni) as co_uni, 
						au.equivalencia, au.relacion as es_unidad, dped.total_art, ap.monto as art_monto, ROUND(ap.monto/au.equivalencia, 4) art_monto_uni, dped.prec_vta, 
						(dped.reng_neto-dped.monto_desc_glob) AS monto_base_item,
                        (dped.monto_imp+dped.monto_imp_afec_glob) as iva,
                        ((dped.reng_neto-dped.monto_desc_glob)+(dped.monto_imp+dped.monto_imp_afec_glob)) as total_item,
                        iif(reng_num=1, ped.otros1, 0) as igtf, ped.saldo as saldo_total_doc, iif(ped.campo8 <> '', ped.campo8, 'DEV') as campo8 
                FROM    (saPedidoVenta AS ped INNER JOIN saPedidoVentaReng AS dped ON
                        ped.doc_num = dped.doc_num) LEFT JOIN saArtPrecio as ap ON dped.co_art = ap.co_art AND dped.co_precio = ap.co_precio
						LEFT JOIN saArtUnidad as au ON dped.co_art = au.co_art AND dped.co_uni = au.co_uni 
						LEFT JOIN saArticulo AS art ON dped.co_art = art.co_art LEFT JOIN saCliente AS c ON ped.co_cli = c.co_cli 
						LEFT JOIN saVendedor as v ON ped.co_ven = v.co_ven
                        LEFT JOIN saTransporte as t ON ped.co_tran = t.co_tran
    
                {where} 
                ORDER BY ped.fec_reg, ped.doc_num
                """
            fact_det = get_read_sql(sql, self.conexion)
            fact_det['co_tipo_doc'] = 'PCLI'
            return fact_det

    def asociar_devolucion_pedido(self, cursor, numero_devolucion, numeros_pedidos):
        for factura in numeros_pedidos:        
            sql = f"""
                UPDATE saPedidoVenta SET campo8='{numero_devolucion}'
                WHERE doc_num LIKE '%{factura}%'
                """
            cursor.execute(sql)