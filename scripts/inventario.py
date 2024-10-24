from pandas import merge
from scripts.sql_read import get_read_sql
from scripts.datos_profit import DatosProfit
from scripts.facturas_ventas import FacturaVentasConsultas

class Inventario:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def movimiento_inventario_x_articulo(self):
        clientes = DatosProfit(self.conexion).clientes()[['co_cli', 'tip_cli']]
        ventas = FacturaVentasConsultas(self.conexion).data_factura_venta_sin_ruta(anio='all', mes='all')[['doc_num', 'co_tran']]
        ventas['doc_num'] = ventas['doc_num'].str.strip()
        ventas['co_tran'] = ventas['co_tran'].str.strip()
        sql = f"""
                EXEC RepMovimientoInventarioxArticulo 
            """
        mov_invent = get_read_sql(sql, self.conexion)
        mov_invent[['co_art', 'co_alma', 'tipo', 'doc_num', 'co_cliprov']] = mov_invent[['co_art', 'co_alma', 'tipo', 'doc_num', 'co_cliprov']].apply(
                                                                lambda x: x[['co_art', 'co_alma', 'tipo', 'doc_num', 'co_cliprov']].str.strip(), axis=1)
        mov_invent = merge(mov_invent, clientes,how='left', left_on=['co_cliprov'], right_on=['co_cli'])
        mov_invent = merge(mov_invent, ventas,how='left', left_on=['doc_num'], right_on=['doc_num'])
        mov_invent['exclude'] = (mov_invent['tipo'] == 'FACT') &  (mov_invent['co_tran'] != 'NA')
        return mov_invent
    
    def movimientos_inventario_filtrado(self):
        df = self.movimiento_inventario_x_articulo()
        df2 = df[((df['doc_num'] != 'AI-P000000') & (df['tipo'] != 'DCLI') & (df['co_alma'] == '01') & (~ df['exclude']))]
        return df2
    
    def resumen_mov_nventario_filtrado(self):
        df = self.movimientos_inventario_filtrado()
        return df.groupby(['co_art', 'art_des', 'co_uni', 'co_alma']).agg({'total_entrada':'sum', 'total_salida':'sum'}).reset_index()
    
         
    def resumen_mov_inventario_filtrado_almacen_preincipal(self):
        df = self.resumen_mov_nventario_filtrado()
        df2 = df[df['co_alma'] == '01'].copy()
        df2['saldo'] = round(df2['total_entrada'] - df2['total_salida'], ndigits=2)
        df2['total_entrada'] = round(df2['total_entrada'], ndigits=2)
        df2['total_salida'] = round(df2['total_salida'], ndigits=2)
        return df2