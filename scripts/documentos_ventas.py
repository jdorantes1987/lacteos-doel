from scripts.sql_read import get_read_sql

class DocumentosVentasConsultas:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def saldo_anterior_facturas_ventas(self, **kwargs):
        """_Retorna la data de los saldos anteriores de las facturas de ventas según el rango de fechas indicado._

          Args:
              fecha_d (_fecha desde_): _corresponde a la fecha a partir del cual se acumulan los movimientos._
              tip_cli (_tipo de documento_): _corresponde al tipo de cliente 'C' comercios 'R' ruteros 'all' todos._
              tip_doc (_tipo de documento_): _corresponde al tipo de documento 'FACT' factura 'AJPM' ajuste positivo manual 'AJNM' ajuste negativo manual 'N/CR' nota de crédito._

          Returns:
              _DataFrame_: _Retorna un DataFrame con los saldos anteriores según la fecha indicada._
          """       
        fecha_d, tip_doc = kwargs.get('fecha_d') , kwargs.get('tip_doc', 'FACT')
        tip_cli = kwargs.get('tip_cli', 'all')
        condicion_tipo_cliente = "c.tip_cli=c.tip_cli" if tip_cli == 'all' else f"c.tip_cli = '{tip_cli}'"
        sql = f"""
            SELECT CAST('{fecha_d}' AS datetime) AS fecha_anterior_a, RTRIM(doc.co_cli) as co_cli, sum(doc.total_neto) as sa_facturas 
            FROM saDocumentoVenta as doc LEFT JOIN saCliente as c ON doc.co_cli = c.co_cli 
            WHERE RTRIM(doc.co_tipo_doc) = '{tip_doc}'  AND  CAST(doc.fec_emis AS DATE) < '{fecha_d}' AND doc.anulado = 0  AND {condicion_tipo_cliente} 
            GROUP BY doc.co_cli
            """
        return get_read_sql(sql, self.conexion)
    