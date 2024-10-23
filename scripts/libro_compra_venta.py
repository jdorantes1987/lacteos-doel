from pandas import to_datetime, merge_asof
from scripts.sql_read import get_read_sql
from scripts.bcv.data import historico_tasas_bcv

class LibroCompraVenta:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def view_rep_libro_ventas(self, fecha_d, fecha_h):
            sql = f"""
                    EXEC RepLibroVenta 
                    @sCo_fecha_d = '{fecha_d}',
                    @sCo_fecha_h = '{fecha_h}'
                """
            libro_ventas = get_read_sql(sql, self.conexion)
            return libro_ventas
        
    def view_rep_libro_compras(self, fecha_d, fecha_h):
            sql = f"""
                    EXEC RepLibroCompra  
                    @sCo_fecha_d = '{fecha_d}',
                    @sCo_fecha_h = '{fecha_h}'
                """
            libro_compras = get_read_sql(sql, self.conexion)
            return libro_compras
        
        
    def libro_ventas(self, fecha_d, fecha_h):
        df_data_bcv = historico_tasas_bcv()[['fecha', 'venta_ask2']]  # archivo BCV
        df_data_bcv['venta_ask2'] = round(df_data_bcv['venta_ask2'], ndigits=2)
        data_bcv_sort = df_data_bcv.sort_values(by=['fecha'], ascending=[True])  # se debe ordenar el df para poder conbinar    
        libro = self.view_rep_libro_ventas(fecha_d=fecha_d, fecha_h=fecha_h)
        if libro['nro_doc'].loc[0] != None:
            libro['tipo_doc'] = libro.apply(lambda x: 'FACTURA' if x['nro_doc'][0]!='i' else 'RET', axis=1)
            libro['num_comprobante'] = libro.apply(lambda x: '' if x['nro_doc'][0]!='i' else x['num_comprobante'], axis=1)
            libro['fec_comprobante'] = libro.apply(lambda x: '' if x['nro_doc'][0]!='i' else x['fec_comprobante'], axis=1)
            libro['fecha_emis'] = to_datetime(libro['fecha_emis']).dt.normalize()
            libro['fec_comprobante'] = to_datetime(libro['fec_comprobante']).dt.normalize()
            merge_libro_tasas = merge_asof(libro, data_bcv_sort, left_on='fecha_emis', right_on='fecha', direction="nearest")  # Combinar por aproximación
            merge_libro_tasas['fecha_emis'] = merge_libro_tasas['fecha_emis'].dt.strftime('%d-%m-%Y')
            merge_libro_tasas['fec_comprobante'] = merge_libro_tasas['fec_comprobante'].dt.strftime('%d-%m-%Y')
            merge_libro_tasas[['base_imp_bs', 
                            'monto_imp_bs', 
                            'ventas_exentas_bs', 
                            'monto_igtf_bs', 
                            'monto_ret_imp_bs',
                            'total_neto_bs']] = merge_libro_tasas.apply(lambda x: x[['base_imp', 
                                                                                        'monto_imp', 
                                                                                        'ventas_exentas', 
                                                                                        'monto_igtf', 
                                                                                        'monto_ret_imp',
                                                                                        'total_neto']] * x['venta_ask2'],
                                                                        axis=1)
            merge_libro_tasas['base_imp_bs'] = round(merge_libro_tasas['base_imp_bs'], ndigits=2)
            merge_libro_tasas['monto_imp_bs'] = round(merge_libro_tasas['monto_imp_bs'], ndigits=2)
            merge_libro_tasas['ventas_exentas_bs'] = round(merge_libro_tasas['ventas_exentas_bs'], ndigits=2)
            merge_libro_tasas['monto_igtf_bs'] = round(merge_libro_tasas['monto_igtf_bs'], ndigits=2)
            merge_libro_tasas['monto_ret_imp_bs'] = round(merge_libro_tasas['monto_ret_imp_bs'], ndigits=2)
            merge_libro_tasas['total_neto_bs'] = round(merge_libro_tasas['total_neto_bs'], ndigits=2)
            return merge_libro_tasas[['tipo_doc',
                                    'co_cli',
                                    'fecha_emis',
                                    'r', 
                                    'cli_des',
                                    'num_comprobante',
                                    'nro_orig',
                                    'n_control', 
                                    'doc_afec',
                                    'total_neto_bs',
                                    'ventas_exentas_bs',
                                    'base_imp_bs',
                                    'tasa', 
                                    'monto_imp_bs',
                                    'monto_igtf_bs',
                                    'monto_ret_imp_bs', 
                                    'anulado', 
                                    'tipo_imp', 
                                    'fec_comprobante', 
                                    'contrib',  
                                    ]]
        
    def libro_compras(self, fecha_d, fecha_h):
        df_data_bcv = historico_tasas_bcv()[['fecha', 'venta_ask2']]  # archivo BCV
        df_data_bcv['venta_ask2'] = round(df_data_bcv['venta_ask2'], ndigits=2)
        data_bcv_sort = df_data_bcv.sort_values(by=['fecha'], ascending=[True])  # se debe ordenar el df para poder conbinar    
        libro = self.view_rep_libro_compras(fecha_d=fecha_d, fecha_h=fecha_h)
        if libro['nro_doc'].loc[0] != None:
            libro['tipo_doc'] = libro.apply(lambda x: 'FACTURA' if x['nro_doc'][0]!='i' else 'RET', axis=1)
            libro['num_comprobante'] = libro.apply(lambda x: '' if x['nro_doc'][0]!='i' else x['num_comprobante'], axis=1)
            libro['fec_comprobante'] = libro.apply(lambda x: '' if x['nro_doc'][0]!='i' else x['fec_comprobante'], axis=1)
            libro['fecha_emis'] = to_datetime(libro['fecha_emis']).dt.normalize()
            merge_libro_tasas = merge_asof(libro, data_bcv_sort, left_on='fecha_emis', right_on='fecha', direction="nearest")  # Combinar por aproximación
            merge_libro_tasas['fecha_emis'] = merge_libro_tasas['fecha_emis'].dt.strftime('%d-%m-%Y')
            merge_libro_tasas[['base_imp_bs', 
                            'monto_imp_bs', 
                            'compras_exentas_bs', 
                            'monto_igtf_bs', 
                            'monto_ret_imp_bs',
                            'total_neto_bs']] = merge_libro_tasas.apply(lambda x: x[['base_imp', 
                                                                                        'monto_imp', 
                                                                                        'compras_exentas', 
                                                                                        'monto_igtf', 
                                                                                        'monto_ret_imp',
                                                                                        'total_neto']] * x['venta_ask2'],
                                                                        axis=1)
            merge_libro_tasas['base_imp_bs'] = round(merge_libro_tasas['base_imp_bs'], ndigits=2)
            merge_libro_tasas['monto_imp_bs'] = round(merge_libro_tasas['monto_imp_bs'], ndigits=2)
            merge_libro_tasas['compras_exentas_bs'] = round(merge_libro_tasas['compras_exentas_bs'], ndigits=2)
            merge_libro_tasas['monto_igtf_bs'] = round(merge_libro_tasas['monto_igtf_bs'], ndigits=2)
            merge_libro_tasas['monto_ret_imp_bs'] = round(merge_libro_tasas['monto_ret_imp_bs'], ndigits=2)
            merge_libro_tasas['total_neto_bs'] = round(merge_libro_tasas['total_neto_bs'], ndigits=2)
            return merge_libro_tasas[['tipo_doc',
                                    'co_prov',
                                    'fecha_emis',
                                    'r', 
                                    'prov_des',
                                    'num_comprobante',
                                    'nro_fact',
                                    'n_control', 
                                    'doc_afec',
                                    'total_neto_bs',
                                    'compras_exentas_bs',
                                    'base_imp_bs',
                                    'tasa', 
                                    'monto_imp_bs',
                                    'monto_igtf_bs',
                                    'monto_ret_imp_bs', 
                                    'anulado', 
                                    'tipo_imp', 
                                    'fec_comprobante', 
                                    'contrib',  
                                    ]]