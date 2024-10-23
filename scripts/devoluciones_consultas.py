from scripts.sql_read import get_read_sql

class DevolucionesConsultas:
      def __init__(self, conexion):
          self.conexion = conexion    
            
      def data_devolucion_con_detalle(self, **kwargs):
            anio, mes = kwargs.get('anio'), kwargs.get('mes')
            where_anio = f"" if anio == 'all' else f" AND year(dev.fec_reg)='{anio}'"
            where_all = "WHERE dev.anulado=0 " + where_anio
            where_mes = f"WHERE dev.anulado=0 AND year(dev.fec_reg)='{anio}' and month(dev.fec_reg)='{mes}'"
            where = where_all if mes == 'all' else where_mes
            sql = f"""
                SELECT reng_num, RTRIM(dev.doc_num) as doc_num, RTRIM(ddev.co_art) as co_art, art.art_des,
                        dev.fec_emis, dev.fec_reg, dev.descrip,
                        year(dev.fec_reg) AS anio, month(dev.fec_reg) AS mes, RTRIM(dev.co_ven) as co_ven, RTRIM(dev.co_cli) as co_cli, 
                        RTRIM(dev.co_tran) AS co_tran, c.cli_des, RTRIM(c.tip_cli) as tip_cli, v.ven_des, t.des_tran, RTRIM(ddev.co_alma) as co_alma, RTRIM(ddev.co_precio) as co_precio, RTRIM(ddev.co_uni) as co_uni,
						au.equivalencia, au.relacion as es_unidad, ddev.total_art, ap.monto as art_monto, ROUND(ap.monto/au.equivalencia, 4) art_monto_uni, ddev.prec_vta, 
                        iif(reng_num=1, ROUND(dev.total_neto - dev.saldo, 4), 0) as monto_abonado, 
						(ddev.reng_neto) AS monto_base_item,
                        (ddev.monto_imp) as iva,
                        (ddev.reng_neto + ddev.monto_imp) as total_item,
                        iif(reng_num=1, dev.otros1, 0) as igtf, 
                        iif(reng_num=1, dev.saldo, 0) as saldo_total_doc 
                FROM    (saDevolucionCliente AS dev INNER JOIN saDevolucionClienteReng AS ddev ON
                        dev.doc_num = ddev.doc_num) LEFT JOIN saArtPrecio as ap ON ddev.co_art = ap.co_art AND ddev.co_precio = ap.co_precio
						LEFT JOIN saArtUnidad as au ON ddev.co_art = au.co_art AND ddev.co_uni = au.co_uni 
						LEFT JOIN saArticulo AS art ON ddev.co_art = art.co_art LEFT JOIN saCliente AS c ON dev.co_cli = c.co_cli 
						LEFT JOIN saVendedor as v ON dev.co_ven = v.co_ven
                        LEFT JOIN saTransporte as t ON dev.co_tran = t.co_tran 
    
                {where} 
                ORDER BY dev.fec_reg, dev.doc_num
                """
            dev_det = get_read_sql(sql, self.conexion)
            dev_det['co_tipo_doc'] = 'FACT'
            return dev_det