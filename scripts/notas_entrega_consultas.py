from scripts.sql_read import get_read_sql
from pandas import merge

class NotasEntregaConsultas:
    
    def __init__(self, conexion):
        self.conexion = conexion
        
    def data_notas_entrega_con_detalle(self, **kwargs):
        fecha_d, fecha_h = kwargs.get('fecha_d', 'all'), kwargs.get('fecha_h', 'all')
        tip_cli = kwargs.get('tip_cli', 'all')
        condicion_tipo_cliente = "c.tip_cli=c.tip_cli" if tip_cli == 'all' else f"c.tip_cli = '{tip_cli}'"
        all_records = True if fecha_d == 'all' or fecha_h == 'all' else False
        where = f"WHERE nota.anulado=0 AND {condicion_tipo_cliente}" if all_records else f"WHERE nota.anulado=0 AND {condicion_tipo_cliente} AND CAST(nota.fec_emis AS DATE) >= '{fecha_d}' and CAST(nota.fec_emis AS DATE) <='{fecha_h}'"
        sql = f"""
            SELECT reng_num, RTRIM(nota.doc_num) as doc_num, RTRIM(dnota.co_art) as co_art, art.art_des,
                    nota.fec_emis, nota.fec_reg, nota.descrip,
                    year(nota.fec_emis) AS anio, month(nota.fec_emis) AS mes, RTRIM(nota.co_ven) as co_ven, RTRIM(nota.co_cli) as co_cli,
                    RTRIM(nota.co_tran) AS co_tran, c.cli_des, v.ven_des, t.des_tran, dnota.co_precio, RTRIM(dnota.co_uni) as co_uni, RTRIM(dnota.co_alma) as co_alma, 
                    au.equivalencia, au.relacion as es_unidad, dnota.total_art, ap.monto as art_monto, ROUND(dnota.prec_vta/au.equivalencia, 6) art_monto_uni, dnota.prec_vta, 
                    ROUND(iif(RTRIM(dnota.co_uni) <> 'UND' AND RTRIM(dnota.co_uni) <> 'KG', dnota.prec_vta/au.equivalencia, dnota.prec_vta), 6) as prec_vta_uni,
                    (dnota.reng_neto) AS monto_base_item,
                    (dnota.monto_imp) as iva,
                    (dnota.reng_neto + dnota.monto_imp) as total_item,
                    iif(reng_num=1, nota.otros1, 0) as igtf, nota.saldo as saldo_total_doc 
            FROM    (saNotaEntregaVenta AS nota INNER JOIN saNotaEntregaVentaReng AS dnota ON
                    nota.doc_num = dnota.doc_num) LEFT JOIN saArtPrecio as ap ON dnota.co_art = ap.co_art AND dnota.co_precio = ap.co_precio
                    LEFT JOIN saArtUnidad as au ON dnota.co_art = au.co_art AND dnota.co_uni = au.co_uni 
                    LEFT JOIN saArticulo AS art ON dnota.co_art = art.co_art LEFT JOIN saCliente AS c ON nota.co_cli = c.co_cli 
                    LEFT JOIN saVendedor as v ON nota.co_ven = v.co_ven
                    LEFT JOIN saTransporte as t ON nota.co_tran = t.co_tran  
            {where} 
            ORDER BY nota.fec_reg, nota.doc_num
            """
        fact_det = get_read_sql(sql, self.conexion)
        fact_det['co_tipo_doc'] = 'NENT'
        return fact_det
        
    def ultimos_precios_notas(self, **kwargs):
        notas = self.data_notas_entrega_con_detalle(**kwargs)
        notas['fec_emis'] = notas['fec_emis'].dt.normalize()
        # Busca el ultimo numero de nota de entrega donde se uso cada cod. articulo
        ultimos_precios = notas.groupby(['co_cli', 'co_art', 'equivalencia'], sort=False, as_index=False)[['doc_num']].max()
        ultimos_precios = merge(ultimos_precios, notas, how='left')[['co_cli', 'co_art', 'equivalencia', 'prec_vta_uni', 'doc_num', 'fec_emis']]
        # Prevee el caso de que existan codigos de articulos duplicados en la misma nota de entrega
        ultimos_precios = ultimos_precios.groupby(['co_cli', 'co_art', 'equivalencia', 'doc_num', 'fec_emis'], sort=False, as_index=False)[['prec_vta_uni']].max()
        # Prevee el caso cuando se utilicen unidades en las notas de entrega
        ultimos_precios['prec_vta_uni'] = ultimos_precios['prec_vta_uni'] * ultimos_precios['equivalencia']
        #  filtrar artículos cuya equivalencia sea diferente de unidad
        ultimos_precios = ultimos_precios[ultimos_precios['equivalencia'] == 1]
        return ultimos_precios
    
    def saldo_anterior_notas(self, **kwargs):
        fecha_d, tip_cli = kwargs.get('fecha_d') , kwargs.get('tip_cli', 'all')
        condicion_tipo_cliente = "c.tip_cli=c.tip_cli" if tip_cli == 'all' else f"c.tip_cli = '{tip_cli}'"
        sql = f"""
            SELECT CAST ('{fecha_d}' AS datetime) AS fecha_anterior_a, RTRIM(doc.co_cli) as co_cli, sum(doc.total_neto) as sa_nota_e
            FROM saNotaEntregaVenta as doc LEFT JOIN saCliente as c ON doc.co_cli = c.co_cli 
            WHERE CAST(doc.fec_emis AS DATE) < '{fecha_d}' AND doc.anulado = 0  AND {condicion_tipo_cliente} 
            GROUP BY doc.co_cli
            """
        return get_read_sql(sql, self.conexion)

