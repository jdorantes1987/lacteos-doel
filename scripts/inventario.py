from pandas import merge, concat
from scripts.sql_read import get_read_sql
from scripts.datos_profit import DatosProfit
from scripts.facturas_ventas import FacturaVentasConsultas

class Inventario:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def movimiento_inventario_x_articulo(self):
        clientes = DatosProfit(self.conexion).clientes()[['co_cli', 'tip_cli']]
        ventas = FacturaVentasConsultas(self.conexion).data_factura_venta_sin_ruta()[['doc_num', 'co_tran']]
        ventas['doc_num'] = ventas['doc_num'].str.strip()
        ventas['co_tran'] = ventas['co_tran'].str.strip()
        sql = f"""
                EXEC RepMovimientoInventarioxArticulo 
            """
        mov_invent = get_read_sql(sql, self.conexion)
        mov_invent['fecha'] = mov_invent['fecha'].dt.normalize()
        mov_invent[['co_art', 'co_alma', 'tipo', 'doc_num', 'co_cliprov']] = mov_invent[['co_art', 'co_alma', 'tipo', 'doc_num', 'co_cliprov']].apply(
                                                                lambda x: x[['co_art', 'co_alma', 'tipo', 'doc_num', 'co_cliprov']].str.strip(), axis=1)
        mov_invent = merge(mov_invent, clientes,how='left', left_on=['co_cliprov'], right_on=['co_cli'])
        mov_invent = merge(mov_invent, ventas,how='left', left_on=['doc_num'], right_on=['doc_num'])
        mov_invent['exclude'] = (mov_invent['tipo'] == 'FACT') &  (mov_invent['co_tran'] != 'NA')
        return mov_invent
    
    def movimientos_inventario_filtrado(self, fecha_d, fecha_h):
        df = self.movimiento_inventario_x_articulo()
        movimientos = df[((df['doc_num'] != 'AI-P000000') & (df['tipo'] != 'DCLI') & (df['co_alma'] == '01') & (~ df['exclude']))]
        mov_entre_fechas = movimientos[(movimientos['fecha']>=fecha_d) & (movimientos['fecha']<=fecha_h)] 
        mov_anterior_fechas = movimientos[(movimientos['fecha']<fecha_d)].copy()
        mov_anterior_fechas['co_alma'] = '01'
        mov_anterior_fechas = mov_anterior_fechas.groupby(['co_art', 'art_des', 'co_alma']).agg({'total_entrada':'sum', 'total_salida':'sum'}) .reset_index()
        movimientos_inv = concat([mov_anterior_fechas, mov_entre_fechas], ignore_index=True, axis=0)
        return movimientos_inv
    
    def resumen_mov_inventario_filtrado(self, fecha_d, fecha_h):
        df = self.movimientos_inventario_filtrado(fecha_d=fecha_d, fecha_h=fecha_h)
        df['es_saldo_ant'] = df['fecha'].isnull()
        mov_anterior_fechas = df[df['es_saldo_ant']]
        mov_entre_fechas = df[~df['es_saldo_ant']]
        mov_entre_fechas = mov_entre_fechas.groupby(['co_art', 'art_des', 'co_alma']).agg({'total_entrada':'sum', 'total_salida':'sum'}).reset_index()
        mov_anterior_fechas = mov_anterior_fechas.groupby(['co_art', 'art_des', 'co_alma']).agg({'total_entrada':'sum', 'total_salida':'sum'}).reset_index()
        mov_anterior_fechas.rename(columns={'total_entrada':'total_entrada_sa', 'total_salida':'total_salida_sa'}, inplace=True)
        if len(mov_anterior_fechas) > 0:
            resumen = merge(mov_entre_fechas, mov_anterior_fechas, how='inner')
        else:
            resumen = mov_entre_fechas
            resumen['total_entrada_sa'] = 0.0
            resumen['total_salida_sa'] = 0.0
        return resumen
    
         
    def resumen_mov_inventario_filtrado_almacen_principal(self, fecha_d, fecha_h):
        df = self.resumen_mov_inventario_filtrado(fecha_d=fecha_d, fecha_h=fecha_h)
        df['saldo_anterior'] = round(df['total_entrada_sa'] - df['total_salida_sa'], ndigits=2)
        df['saldo'] = round(df['saldo_anterior'] + df['total_entrada'] - df['total_salida'], ndigits=2)
        df['total_entrada'] = round(df['total_entrada'], ndigits=2)
        df['total_salida'] = round(df['total_salida'], ndigits=2)
        return df[['co_art', 'art_des', 'co_alma', 'saldo_anterior', 'total_entrada', 'total_salida', 'saldo']]