import locale
from pandas import pivot_table, merge
from numpy import nan
from scripts.sql_read import get_read_sql
from scripts.datos_profit import DatosProfit

class CXC:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def view_cxc(self):
        sql = f"""
                EXEC RepDocumentoCXCxCliente
                @sCo_Condic = '12'
            """
        cxc = get_read_sql(sql, self.conexion)
        
        cxc['co_tipo_doc'] = cxc['co_tipo_doc'].str.strip()
        cxc['co_cli'] = cxc['co_cli'].str.strip()
        cxc['saldo'] = cxc.apply(lambda x: x['saldo'] if (x['co_tipo_doc'] != 'AJNM' and x['co_tipo_doc'] != 'AJNA' and x['co_tipo_doc'] != 'N/CR') else -x['saldo'], axis=1)
        clientes = DatosProfit(self.conexion).clientes()[['co_cli', 'tip_cli']]
        merge_cxc_clientes = merge(cxc, clientes,how='left', left_on=['co_cli'], right_on=['co_cli'])
        return merge_cxc_clientes.sort_values(by=['nro_doc'], ascending=[False]).reset_index(drop=True)
        
    
    #  Facturas de ventas parcialmente cobradas o sin cobro        
    def cxc_clientes_resum_pivot(self, tipo_cliente):
        df_cxc = self.view_cxc()
        if tipo_cliente == 'T':
            df_cxc = df_cxc[df_cxc['tip_cli'] != '']
        else:
            df_cxc = df_cxc[df_cxc['tip_cli'] == tipo_cliente]
        df_cxc = df_cxc.sort_values(by=['fec_emis'], ascending=[True])
        df_cxc['anio'] =  df_cxc['fec_emis'].dt.year  # Obtiene el año
        locale.setlocale(locale.LC_ALL, 'es_ES')
        df_cxc['mes'] = df_cxc['fec_emis'].dt.month_name(locale='es_ES').str[:3]
        locale.setlocale(locale.LC_ALL, '')
        return pivot_table(
            df_cxc,
            values='saldo',
            index=['co_cli', 'cli_des'],
            columns=['anio', 'mes'],
            aggfunc='sum',
            margins=True,
            sort=False,
        ).replace(nan, 0)