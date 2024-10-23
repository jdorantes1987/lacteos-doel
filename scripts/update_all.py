from pandas import merge_asof, to_datetime
from scripts.transacciones import GestorTransacciones
from scripts.datos_profit import DatosProfit
from scripts.bcv.data import historico_tasas_bcv

class UpdateAll:
      def __init__(self, conexion):
          self.conexion = conexion    
          self.gestor_trasacc = GestorTransacciones(conexion)
          self.cursor = self.gestor_trasacc.get_cursor()
   
      def agregar_info_tasa_facturas(self, fecha_ini, fecha_fin):
          facturas = DatosProfit(self.conexion).encabezado_factura_ventas(fecha_ini=fecha_ini, fecha_fin=fecha_fin)[['fec_emis', 'doc_num', 'campo1', 'campo3']]
          facturas['fec_emis'] = to_datetime(facturas['fec_emis']).dt.normalize()
          facturas_sin_tasa = facturas[facturas['campo1'].isnull() | facturas['campo3'].isnull()]
          if len(facturas_sin_tasa) > 0:
            facturas_sort = facturas_sin_tasa.sort_values(by=['fec_emis'], ascending=[True])  # se debe ordenar el df para poder conbinar
            df_data_bcv = historico_tasas_bcv()[['fecha', 'venta_ask2']]  # archivo BCV
            data_bcv_sort = df_data_bcv.sort_values(by=['fecha'], ascending=[True])  # se debe ordenar el df para poder conbinar
            facturas_x_tasa = merge_asof(facturas_sort, data_bcv_sort, left_on='fec_emis', right_on='fecha', direction="nearest")  # Combinar por aproximación
            facturas_x_tasa['fecha'] = facturas_x_tasa['fecha'].dt.strftime('%d/%m/%Y')
            facturas_x_tasa['venta_ask2'] = facturas_x_tasa['venta_ask2'].apply(lambda x: str(x).replace('.', ','))  # reemplazar punto por coma
            #print(facturas_x_tasa)
            gestor_trasacc = GestorTransacciones(self.conexion)
            cursor = gestor_trasacc.get_cursor()
            gestor_trasacc.iniciar_transaccion()
            for index, row in facturas_x_tasa.iterrows():  
                index += 1      
                sql = f"""
                    UPDATE saFacturaVenta SET campo1='{row['venta_ask2']}', campo3='{row['fecha']}'  
                    WHERE doc_num = '{row['doc_num']}'
                    """
                cursor.execute(sql)
            
            gestor_trasacc.confirmar_transaccion()