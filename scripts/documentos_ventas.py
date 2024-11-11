from scripts.sql_read import get_read_sql

class DocumentosVentasConsultas:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def saldo_anterior(self, **kwargs):
            fecha_d, tip_doc = kwargs.get('fecha_d') , kwargs.get('tip_doc', 'FACT')
            tip_cli = kwargs.get('tip_cli', 'all')
            condicion_tipo_cliente = "c.tip_cli=c.tip_cli" if tip_cli == 'all' else f"c.tip_cli = '{tip_cli}'"
            sql = f"""
                SELECT '{tip_doc}' as tipo_doc, CAST ('{fecha_d}' AS DATE) AS fecha_anterior_a, RTRIM(doc.co_cli) as co_cli, sum(doc.total_neto) as total_neto 
                FROM saDocumentoVenta as doc LEFT JOIN saCliente as c ON doc.co_cli = c.co_cli 
                WHERE RTRIM(doc.co_tipo_doc) = '{tip_doc}'  AND  doc.fec_emis < '{fecha_d}' AND doc.anulado = 0  AND {condicion_tipo_cliente} 
                GROUP BY doc.co_cli
                """
            return get_read_sql(sql, self.conexion)
    