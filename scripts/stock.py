from scripts.consultas_generales import ConsultasGenerales
from scripts.transacciones import GestorTransacciones



class Stock:
    def __init__(self, conexion):
        self.conexion = conexion
        
    def update_stock(self):
        gestor_trasacc = GestorTransacciones(self.conexion)
        cursor = gestor_trasacc.get_cursor()
        gestor_trasacc.iniciar_transaccion()
        resumen_inventario = ConsultasGenerales(self.conexion).resumen_inventario_x_articulo()
        for index, row in resumen_inventario.iterrows():  
            index += 1      
            sql = f"""
                UPDATE saStockAlmacen SET stock={row['StockFinal']}
                WHERE RTRIM(co_alma) = '01' AND co_art LIKE '%{row['co_art']}%' AND TIPO LIKE '%ACT%'
                """
            cursor.execute(sql)
            
            # sql2 = f"""
            #        DELETE FROM saStockAlmacen 
            #        WHERE tipo LIKE '%COM%'
            #        """
            # cursor.execute(sql2)
            
        gestor_trasacc.confirmar_transaccion()