from pandas import read_excel
from scripts.sql_read import get_read_sql
from scripts.datos_profit import DatosProfit 

class ConsultasGenerales:
    def __init__(self, conexion):
        self.conexion = conexion
        self.consultas_profit = DatosProfit(conexion)
    
    def get_last_number_devol(self):
        sql = """
                SELECT RTRIM(doc_num) as doc_num
                FROM saDevolucionCliente 
                WHERE doc_num in (SELECT MAX(RTRIM(doc_num)) 
                                FROM saDevolucionCliente)
            """
        number = get_read_sql(sql,  self.conexion)['doc_num']
        return number[0] if len(number) >0 else 'DV0000000'
    
    def articulos_profit(self):
        sql = """
                Select RTRIM(co_art) as co_art, art_des, campo1, anulado, dis_cen, tipo_imp 
                from saArticulo
            """
        return get_read_sql(sql, self.conexion)
    
    def resumen_inventario_x_articulo(self):
        sql = """
                EXEC RepResumenInventarioxArticulo
                @sCo_Almacen = N'01'
            """
        df = get_read_sql(sql, self.conexion)
        df['co_art'] = df['co_art'].str.strip()
        df['art_des'] = df['art_des'].str.strip()
        df_group = df.groupby(['co_art']).agg({'StockFinal': 'mean'}).reset_index()
        return df_group
    
    def clientes(self):
        return self.consultas_profit.clientes() 
    
    def art_precio(self):
        sql = """
                Select RTRIM(co_art) as co_art, RTRIM(co_precio) as co_precio, RTRIM(co_alma) as co_alma, monto  
                from saArtPrecio
            """
        return get_read_sql(sql, self.conexion)
    
    def get_last__nro_ajuste_negativo(self):
        sql = """
                    SELECT  MAX(RTRIM(nro_doc)) nro_doc
                    FROM saDocumentoVenta 
                    WHERE nro_doc in (SELECT MAX(RTRIM(nro_doc)) 
                            FROM saDocumentoVenta 
                            WHERE RTRIM(co_tipo_doc) = 'AJNM')
            """
        return get_read_sql(sql, self.conexion).iloc[0,0]