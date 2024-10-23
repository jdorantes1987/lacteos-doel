from numpy import nan
import math
from pandas import merge
from scripts.pedidos import PedidosVentasConsultas
from scripts.notas_entrega_consultas import NotasEntregaConsultas
from scripts.estado_cuenta_rutero import EstadoCuentaRutero
from scripts.consultas_generales import ConsultasGenerales
from scripts.stock import Stock
from scripts.transacciones import GestorTransacciones
from scripts.utilidades import date_today
from scripts.datos_profit import DatosProfit

class Devoluciones:
      def __init__(self, conexion):
          self.conexion = conexion    
          self.estado_de_cuenta_rutero = EstadoCuentaRutero(conexion)
          self.pedido_ventas = PedidosVentasConsultas(conexion)
          self.notas_entrega = NotasEntregaConsultas(conexion)
          self.consultas_generales = ConsultasGenerales(conexion)
          self.stock = Stock(conexion)
          self.gestor_trasacc = GestorTransacciones(conexion)
          self.cursor = self.gestor_trasacc.get_cursor()

      def resumen_pedidos(self, anio, mes):
          """_Retorna la data de los pedidos que no han sido asociados a una devolución_

          Args:
              anio (_año de consulta_): _corresponde al año en que se emitió el pedido, valor para todos los años 'all'_
              mes (_mes de consulta_): _corresponde al mes en que se emitió el pedido, valor para todos los mes 'all'_

          Returns:
              _DataFrame_: _Retorna la DataFrame de los pedidos que no han sido asociados a una devolución_
          """
          df1 = self.estado_de_cuenta_rutero.resumen_pedidos(anio=anio, mes=mes) 
          return df1[df1['campo8'].str.contains('DEV')] # Extrae todos los pedidos por asignar devolucion    
          
      
      def datos_devolucion(self, anio, mes):
          pedido_x_rutero = self.resumen_pedidos(anio=anio, mes=mes)
          if len(pedido_x_rutero) > 0:
             articulos = DatosProfit(self.conexion).articulos_profit()[['co_art', 'art_des', 'tipo_imp']]
             set_numeros_pedidos = set(pedido_x_rutero['doc_num'])
             pedido_detalle = self.pedido_ventas.data_pedido_con_detalle(anio=anio, mes=mes)
             pedidos_filtrados = pedido_detalle[pedido_detalle['doc_num'].isin(set_numeros_pedidos)][['co_tran', 'co_art', 'co_alma', 'es_unidad', 'co_precio', 'co_uni', 'equivalencia', 'total_art', 'monto_base_item']]
             pedidos_filtrados = pedidos_filtrados.groupby(['co_tran', 'co_art', 'co_alma', 'es_unidad', 'co_precio', 'co_uni', 'equivalencia']).agg({'total_art':'sum', 'monto_base_item':'sum'}).reset_index()
             precios_ultimas_notas_entrega = self.notas_entrega.ultimos_precios_notas(anio=anio, mes=mes)[['co_cli', 'co_art', 'doc_num', 'prec_vta_uni']]
             pedidos_con_precio2 = merge(pedidos_filtrados, precios_ultimas_notas_entrega, how='left', left_on=['co_tran', 'co_art'], right_on=['co_cli', 'co_art'], suffixes=('_t1', '_t2'))
            # Asigno el codigo precio 2 a todos los articulo para usarlo en la devolucion
             pedidos_con_precio2['co_precio'] = '02'
             # asignar precio2 a facturas de ruteros sin despacho previo. Asigna precio 2 del litado de precios
             articulos_precio = self.consultas_generales.art_precio()
             articulos_precio2 = articulos_precio[articulos_precio['co_precio'] == '02'][['co_art', 'co_precio', 'monto']]
             articulos_precio2.set_index(['co_art'], inplace=True)
             pedidos_con_precio2['co_cli'] =  pedidos_con_precio2.apply(lambda x: x['co_tran'] if x['co_cli'] is nan else x['co_cli'], axis=1)
             pedidos_con_precio2['doc_num'] =  pedidos_con_precio2.apply(lambda x: 's/despacho' if x['doc_num'] is nan else x['doc_num'], axis=1)
             pedidos_con_precio2['prec_vta_uni'] =  pedidos_con_precio2.apply(lambda x: articulos_precio2.loc[x['co_art'], 'monto'] if math.isnan(x['prec_vta_uni']) else x['prec_vta_uni'], axis=1)
             pedidos_con_precio2['base_precio_2'] =  pedidos_con_precio2.apply(lambda x: (x['prec_vta_uni'] / x['equivalencia']) * x['total_art'] if x['es_unidad'] else x['prec_vta_uni'] * x['total_art'], axis=1)
             pedidos_con_precio2['base_precio_2_uni'] =  pedidos_con_precio2.apply(lambda x: x['base_precio_2'] / x['total_art'], axis=1)
             # se incluye el iva de acuerdo a cada producto
             merge_pedidos_art_profit =  merge(pedidos_con_precio2, articulos, how='left', left_on=['co_art'], right_on=['co_art'], suffixes=('_pd', '_artpro'))
             merge_pedidos_art_profit['iva_precio_dos'] = merge_pedidos_art_profit.apply(lambda x: (x['base_precio_2'] * 16 /100) if x['tipo_imp'] == '1' else 0, axis=1)
             merge_pedidos_art_profit['total_item_precio_dos'] =  merge_pedidos_art_profit['iva_precio_dos'] +  merge_pedidos_art_profit['base_precio_2']
             merge_pedidos_art_profit['ganancia'] =  merge_pedidos_art_profit.apply(lambda x: x['monto_base_item'] - x['base_precio_2'], axis=1)
             return merge_pedidos_art_profit
             
      def datos_devolucion_x_rutero(self, anio, mes, rutero):
          datos_dev = self.datos_devolucion(anio=anio, mes=mes)
          if len(datos_dev) > 0:
              datos_dev = datos_dev[datos_dev['co_tran'] == rutero]
          return datos_dev
           
      def procesar_devolucion(self, anio, mes):
          self.gestor_trasacc.iniciar_transaccion()
          pedidos_devolucion = self.resumen_pedidos(anio=anio, mes=mes)
          # Es importante ordenar por rutero para que cada devolucion sea generada en base a ese orden
          ruteros = pedidos_devolucion['co_tran'].value_counts().reset_index().sort_values(by='co_tran', ascending=True)
          ruteros = ruteros.reset_index(drop=True)
          for i in range(len(ruteros)):
            rutero = ruteros.loc[i, "co_tran"]
            pedidos_devolucion_rutero = pedidos_devolucion[pedidos_devolucion['co_tran'] == rutero]
            numeros_pedidos = set(pedidos_devolucion_rutero['doc_num'])
            datos_dev = self.datos_devolucion_x_rutero(anio=anio, mes=mes, rutero=rutero)
            total_nota_entrega = round(datos_dev['total_item_precio_dos'].sum(), ndigits=2)
            total_monto_bruto = round(datos_dev['base_precio_2'].sum(), ndigits=2)
            total_iva = round(datos_dev['iva_precio_dos'].sum(), ndigits=2)
            numero_dev = int(str(self.consultas_generales.get_last_number_devol()).replace('DV', '')) + 1
            cliente = datos_dev['co_tran'].iloc[0]
            num_devolucion = f'DV{str(numero_dev).zfill(7)}'
            # descrip = f"Dev. s/ped. {', '.join(numeros_pedidos)}" # convvierte Set a String
            descrip = f"Dev. s/ped." # convvierte Set a String
            hoy = date_today().strftime('%Y%m%d %H:%M:%S') # Convierte la fecha a YYYYMMDD
            data_encabezado = f"""
                            '{num_devolucion}', '{descrip}', '{cliente}', 'NA', 'BS', 'GNR', null, '{hoy}', '{hoy}', '{hoy}', 
                            0, '0', null, 0, 1, null, 0, null, 0, {total_monto_bruto}, 
                            {total_iva}, 0, 0, 0, 0, 0, {total_nota_entrega}, {total_nota_entrega}, '', '', 
                            null, '', null, 0, 0, null, null, null, null, null, 
                            null, null, null, null, null, null, null, null, null, null, 
                            null, '999', null, '{hoy}', '999', null, '{hoy}', null, null
                        """
            sql = f"""INSERT INTO saDevolucionCliente (doc_num, descrip, co_cli, co_tran, co_mone, co_ven, co_cond, fec_emis, fec_venc, fec_reg, 
                                                        anulado, status, n_control, ven_ter, tasa, porc_desc_glob, monto_desc_glob, porc_reca, monto_reca, total_bruto, 
                                                        monto_imp, monto_imp2, monto_imp3, otros1, otros2, otros3, total_neto, saldo, dir_ent, comentario, 
                                                        dis_cen, feccom, numcom, contrib, impresa, seriales_e, salestax, impfis, impfisfac, co_tipo_doc, 
                                                        nro_doc, mov_num_b, mov_num_c, campo1, campo2, campo3, campo4, campo5, campo6, campo7, 
                                                        campo8, co_us_in, co_sucu_in, fe_us_in, co_us_mo, co_sucu_mo, fe_us_mo, revisado, trasnfe) 
                                                        VALUES({data_encabezado})"""
            self.cursor.execute(sql)
            
            for index, row in datos_dev.iterrows():
                index += 1
                data_datalle = f"""
                        '{index}', '{num_devolucion}', '{row["co_art"]}', '{row["art_des"]}', '{row['co_alma']}', {row['total_art']}, 0, '{row['co_uni']}', null, '{row['co_precio']}', 
                            {row['base_precio_2_uni']}, null, null, 0, {row['tipo_imp']}, null, null, {16 if row['tipo_imp'] == 1 else 0}, 0, 0, 
                            {row['iva_precio_dos']}, 0, 0, {row['base_precio_2']}, 0, 0, 'NENT', null, null, 0, 
                            0, 0, null, 0, null, 0, 0, 0, 0, 0, 
                            0, 0, 0, '999', null, '{hoy}', '999', null, '{hoy}', null
                            """
                        
                sql2 = f"""INSERT INTO saDevolucionClienteReng (reng_num, doc_num, co_art, des_art, co_alma, total_art, stotal_art, co_uni, sco_uni, co_precio, 
                                                                prec_vta, prec_vta_om, porc_desc, monto_desc, tipo_imp, tipo_imp2, tipo_imp3, porc_imp, porc_imp2, porc_imp3,
                                                                monto_imp, monto_imp2, monto_imp3, reng_neto, pendiente, pendiente2, tipo_doc, num_doc, rowguid_doc, total_dev, 
                                                                monto_dev, otros, comentario, lote_asignado, dis_cen, monto_desc_glob, monto_reca_glob, otros1_glob, otros2_glob, otros3_glob, 
                                                                monto_imp_afec_glob, monto_imp2_afec_glob, monto_imp3_afec_glob, co_us_in, co_sucu_in, fe_us_in, co_us_mo, co_sucu_mo, fe_us_mo, revisado) 
                                                        VALUES({data_datalle})"""
                self.cursor.execute(sql2)
                
            self.pedido_ventas.asociar_devolucion_pedido(cursor=self.cursor,
                                                            numero_devolucion=num_devolucion,
                                                            numeros_pedidos=numeros_pedidos)  
            self.gestor_trasacc.confirmar_transaccion()
            self.stock.update_stock()