from datetime import datetime, timedelta
from pandas import merge
from scripts.sql_read import get_read_sql
from scripts.datos_profit import DatosProfit

class Cobros:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def view_cobros_x_cliente(self, **kwargs):
        fecha_d, fecha_h = kwargs.get('fecha_d', 'all'), kwargs.get('fecha_h', 'all')
        all_records = True if fecha_d == 'all' or fecha_h == 'all' else False
        parametros = "" if all_records else f"@dFecha_d = '{fecha_d}', @dFecha_h = '{fecha_h}'"
        sql = f"""
                EXEC RepCobrosxCliente
                {parametros}
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
    
    def view_cobros_x_cliente_saldo_anterior(self, **kwargs):
        fecha_d = kwargs.get('fecha_d') 
        # converte el formato de fecha pasado por parametro a date, luego resta un día,
        # finalmente devuelve la fecha obtenida en formato fecha requerido
        fecha_h = (datetime.strptime(fecha_d, '%Y%m%d').date() + timedelta(days=-1)).strftime('%Y%m%d')
        cobros = self.view_cobros_x_cliente(fecha_d='20010101', fecha_h=fecha_h)
        cobros = cobros.groupby(['co_cli']).agg({'cargo':'sum'}).reset_index()
        cobros['fecha_anterior_a'] = datetime.strptime(fecha_d, '%Y%m%d').date()
        return cobros[['fecha_anterior_a', 'co_cli', 'cargo']]