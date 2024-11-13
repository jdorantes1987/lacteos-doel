from scripts.sql_read import get_read_sql

class Ajustes:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def documentos_ajustes(self, **kwargs):
        fecha_d, fecha_h = kwargs.get('fecha_d', 'all'), kwargs.get('fecha_h', 'all')
        tip_cli = kwargs.get('tip_cli', 'all')
        all_records = True if fecha_d == 'all' or fecha_h == 'all' else False
        condicion_tipo_cliente = "c.tip_cli=c.tip_cli" if tip_cli == 'all' else f"c.tip_cli = '{tip_cli}'"
        where = f"WHERE d.anulado=0 AND RTRIM(d.co_tipo_doc) <> 'FACT' AND {condicion_tipo_cliente}" if all_records else f"WHERE d.anulado=0 AND RTRIM(d.co_tipo_doc) <> 'FACT' AND CAST(d.fec_emis AS DATE) >= '{fecha_d}' and CAST(d.fec_emis AS DATE) <='{fecha_h}' AND {condicion_tipo_cliente}"
        sql = f"""
            SELECT RTRIM(d.co_tipo_doc) as co_tipo_doc, RTRIM(d.co_cli) as co_cli, 
                   c.cli_des, RTRIM(c.tip_cli) as tip_cli, 
                   RTRIM(d.nro_doc) as doc_num, d.fec_emis, 
                   IIF(RTRIM(d.co_tipo_doc) = 'AJNM' OR  RTRIM(d.co_tipo_doc) = 'AJNA' OR RTRIM(d.co_tipo_doc) = 'IVAN', -d.total_bruto, d.total_bruto) AS total_bruto, 
                   IIF(RTRIM(d.co_tipo_doc) = 'AJNM' OR  RTRIM(d.co_tipo_doc) = 'AJNA' OR RTRIM(d.co_tipo_doc) = 'IVAN', -d.total_neto, d.total_neto) AS total_neto,
                   IIF(RTRIM(d.co_tipo_doc) = 'AJNM' OR  RTRIM(d.co_tipo_doc) = 'AJNA' OR RTRIM(d.co_tipo_doc) = 'IVAN', -d.saldo, d.saldo) AS saldo_doc,
                   RTRIM(d.co_cta_ingr_egr) as co_cta_ingr_egr
            FROM saDocumentoVenta as d  LEFT JOIN saCliente AS c ON d.co_cli = c.co_cli 
            {where}  
            ORDER BY d.fec_emis, d.nro_doc
            """
        df = get_read_sql(sql, self.conexion)
        #if len(df) > 0:
        #    df['fec_emis'] = df['fec_emis'].dt.date
        return df
    
    def ganancias_aplicadas(self):
        sql = f"""
            SELECT RTRIM(d.co_cli) as co_cli, RTRIM(d.nro_doc) as nro_doc, d.fec_emis, total_neto, RTRIM(d.nro_orig) as nro_orig, RTRIM(d.co_tipo_doc) as co_tipo_doc 
            FROM saDocumentoVenta as d  LEFT JOIN saCliente AS c ON d.co_cli = c.co_cli 
            WHERE RTRIM(c.tip_cli) = 'R' AND RTRIM(d.co_tipo_doc) = 'AJNM' AND RTRIM(d.co_cta_ingr_egr) = 'APS'
            """
        df = get_read_sql(sql, self.conexion)
        #if len(df) > 0:
        #    df['fec_emis'] = df['fec_emis'].dt.date
        return df
    
    def saldo_anterior_ajustes(self, **kwargs):
        fecha_d, tip_cli = kwargs.get('fecha_d') , kwargs.get('tip_cli', 'all')
        tip_cli = kwargs.get('tip_cli', 'all')
        condicion_tipo_cliente = "c.tip_cli=c.tip_cli" if tip_cli == 'all' else f"c.tip_cli = '{tip_cli}'"
        where = f"WHERE doc.anulado=0 AND RTRIM(doc.co_tipo_doc) <> 'FACT' AND CAST(doc.fec_emis AS DATE) < '{fecha_d}' AND {condicion_tipo_cliente}"
        sql = f"""
            SELECT RTRIM(doc.co_cli) AS co_cli, CAST('{fecha_d}' AS DATE) AS fecha_anterior_a, 
                    sum(IIF(RTRIM(doc.co_tipo_doc) = 'AJNM' OR  RTRIM(doc.co_tipo_doc) = 'AJNA' OR RTRIM(doc.co_tipo_doc) = 'IVAN', -doc.total_neto, doc.total_neto)) AS total_neto 
            FROM saDocumentoVenta as doc LEFT JOIN saCliente as c ON doc.co_cli = c.co_cli 
            {where}
            GROUP BY doc.co_cli
            """
        return get_read_sql(sql, self.conexion)