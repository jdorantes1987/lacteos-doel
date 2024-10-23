import locale
from pandas import merge
from numpy import nan
from scripts.sql_read import get_read_sql
from scripts.datos_profit import DatosProfit

class Cobros:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def view_cobros_x_cliente(self):
        sql = f"""
                EXEC RepCobrosxCliente
            """
        cobros = get_read_sql(sql, self.conexion)
        clientes = DatosProfit(self.conexion).clientes()[['co_cli', 'tip_cli']]
        cobros['cob_num'] = cobros['cob_num'].str.strip()
        cobros['nro_doc'] = cobros['nro_doc'].str.strip()
        cobros['co_cli'] = cobros['co_cli'].str.strip()
        cobros['co_tipo_doc'] = cobros['co_tipo_doc'].str.strip()
        cobros_doc = cobros[(cobros['co_tipo_doc'].isin(['FACT', 'AJPM', 'AJNM']) & (cobros['anulado'] == 0))]
        cobros_doc_cli = merge(cobros_doc, clientes, how='left', left_on='co_cli', right_on='co_cli')
        cobros_doc_cli['cargo'] = cobros_doc_cli['cargo'] - cobros_doc_cli['abono']
        return cobros_doc_cli[['cob_num', 'fecha', 'co_cli', 'cli_des', 'tip_cli', 'co_tipo_doc', 'nro_doc', 'cargo']]