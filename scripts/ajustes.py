from scripts.sql_read import get_read_sql

class Ajustes:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def documentos_ajustes(self, anio, mes):
        where_anio, mes = anio, mes
        where_anio = f"" if where_anio == 'all' else f" AND year(d.fec_emis)='{where_anio}' AND RTRIM(d.co_tipo_doc) <> 'FACT'"
        where_all = f"WHERE d.anulado = 0 {where_anio}"
        where_mes = f"WHERE d.anulado = 0 AND year(d.fec_emis)='{where_anio}' and month(d.fec_emis)='{mes}' AND RTRIM(d.co_tipo_doc) <> 'FACT')"
        where = where_all if mes == 'all' else where_mes
        sql = f"""
            SELECT RTRIM(d.co_tipo_doc) as co_tipo_doc, RTRIM(d.co_cli) as co_cli, 
                   c.cli_des, RTRIM(c.tip_cli) as tip_cli, 
                   RTRIM(d.nro_doc) as doc_num, d.fec_emis, 
                   IIF(RTRIM(d.co_tipo_doc) = 'AJNM' OR  RTRIM(d.co_tipo_doc) = 'AJNA' OR RTRIM(d.co_tipo_doc) = 'IVAN', -d.total_bruto, d.total_bruto) AS total_bruto, 
                   IIF(RTRIM(d.co_tipo_doc) = 'AJNM' OR  RTRIM(d.co_tipo_doc) = 'AJNA' OR RTRIM(d.co_tipo_doc) = 'IVAN', -d.total_neto, d.total_neto) AS total_neto,
                   IIF(RTRIM(d.co_tipo_doc) = 'AJNM' OR  RTRIM(d.co_tipo_doc) = 'AJNA' OR RTRIM(d.co_tipo_doc) = 'IVAN', -d.saldo, d.saldo) AS saldo_doc,
                   RTRIM(d.co_cta_ingr_egr) as co_cta_ingr_egr
            FROM saDocumentoVenta as d  LEFT JOIN saCliente AS c ON d.co_cli = c.co_cli 
            {where} AND RTRIM(d.co_tipo_doc) <> 'FACT' 
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