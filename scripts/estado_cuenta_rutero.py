from numpy import nan
import math
import locale
from datetime import datetime, timedelta
from pandas import merge, DataFrame, date_range, concat
from scripts.consultas_generales import ConsultasGenerales
from scripts.notas_entrega_consultas import NotasEntregaConsultas
from scripts.facturas_ventas import FacturaVentasConsultas
from scripts.pedidos import PedidosVentasConsultas
from scripts.devoluciones_consultas import DevolucionesConsultas
from scripts.ajustes import Ajustes
from scripts.datos_profit import DatosProfit
from scripts.cobros import Cobros
from scripts.fondo_garantia import FondoGarantia
from scripts.documentos_ventas import DocumentosVentasConsultas

class EstadoCuentaRutero:
    def __init__(self, conexion):
        self.conexion = conexion
        self.consultas_generales = ConsultasGenerales(conexion)
        self.notas_entrega = NotasEntregaConsultas(conexion) 
        self.ventas = FacturaVentasConsultas(conexion)
        self.pedidos = PedidosVentasConsultas(conexion)
        self.devoluciones_consultas = DevolucionesConsultas(conexion)
        self.ajustes = Ajustes(conexion)
        self.cobros = Cobros(conexion)
        self.fondo = FondoGarantia(conexion)
        self.facturas_saldo_ant = DocumentosVentasConsultas(conexion)
          
    def resumen_pedidos(self):
        pedidos = self.pedidos.data_pedido_con_detalle()
        agrupacion_pedido = pedidos.groupby(['co_tran', 'des_tran', 'co_cli', 'cli_des', 'doc_num', 'co_alma', 'co_art', 'art_des', 'co_uni', 'campo8']).agg({'total_art': 'sum',
                                                'iva': 'sum',                                                                                                       
                                                'monto_base_item': 'sum',
                                                'total_item':'sum'}).reset_index()
        return agrupacion_pedido
    
    def resumen_nota_entrega(self, **kwargs):
        notas = self.notas_entrega.data_notas_entrega_con_detalle(**kwargs)
        agrupacion_notas = notas.groupby(['co_cli', 'cli_des', 'co_alma', 'co_art', 'art_des', 'co_uni', 'equivalencia', 'co_precio', 'prec_vta_uni', 'prec_vta']).agg({'total_art': 'sum', 
                                                                                                                                                                        'monto_base_item': 'sum',
                                                                                                                                                                        'total_item':'sum'}).reset_index()
        return agrupacion_notas
    
    #  SUMA TOTAL NE A RUTERO (DESPACHOS)
    def resumen_nota_entrega_rutero(self, **kwargs):
        notas = self.notas_entrega.data_notas_entrega_con_detalle(**kwargs)
        agrupacion_notas = notas.groupby(['co_cli', 'cli_des', 'doc_num', 'fec_emis']).agg({'total_item': 'sum'}).reset_index()
        return agrupacion_notas
    
    #  SUMA TOTAL FACTURAS DE RUTEROS (FACTURACIÓN DIRECTA)
    def resumen_facturas_rutero(self, **kwargs):
        ventas = self.ventas.data_factura_venta_con_detalle(**kwargs)
        ventas_ruteros = ventas[ventas['tip_cli'] == 'R']
        return ventas_ruteros.groupby(['co_cli', 'cli_des', 'doc_num', 'fec_emis']).agg({'monto_base_item': 'sum',
                                                                                         'total_item': 'sum',
                                                                                         'monto_abonado': 'sum',
                                                                                         'saldo_total_doc': 'sum'}).reset_index()
    
    #  RESTA SALDO A RUTERO (FACTURACIÓN COMERCIOS)    
    def resumen_facturas_comercio(self, **kwargs):
        fecha_d, fecha_h = kwargs.get('fecha_d', 'all'), kwargs.get('fecha_h', 'all')
        ventas = self.ventas.data_factura_venta_con_detalle(fecha_d=fecha_d, fecha_h=fecha_h, tip_cli='C')
        ventas =  ventas.groupby(['co_cli', 
                                                            'cli_des', 
                                                            'doc_num', 
                                                            'fec_emis',
                                                            'co_art', 
                                                            'co_uni',
                                                            'equivalencia', 
                                                            'co_tran',
                                                            'es_unidad']).agg({'total_art': 'sum',
                                                                             'monto_base_item': 'sum',
                                                                             'total_item': 'sum',
                                                                             'monto_abonado': 'sum',
                                                                             'saldo_total_doc': 'sum'}).reset_index()
                                                            
        clientes = DatosProfit(self.conexion).clientes()[['co_cli', 'tip_cli']]
        merge1 = merge(ventas, clientes, how='left', left_on='co_tran', right_on='co_cli', suffixes = ('_v', '_rut'))
        merge1.drop(columns=['co_cli_rut'], inplace=True)
        merge1.rename(columns={'co_cli_v': 'co_cli'}, inplace=True)
        ventas_solo_ruteros = merge1[merge1['tip_cli'] == 'R']
        return ventas_solo_ruteros

    #  RESTA SALDO A RUTERO (CALCULO DE GANANCIA EN FACTURACIÓN COMERCIOS)    
    def calculo_ganacia_por_factura_comercio(self, **kwargs):
        articulos = DatosProfit(self.conexion).articulos_profit()[['co_art', 'tipo_imp']]
        ventas_comercio_rutero =  self.resumen_facturas_comercio(**kwargs)
        ultimos_precios_ne = self.notas_entrega.ultimos_precios_notas()
        ventas_comercio_rutero_precio2 = merge(ventas_comercio_rutero, ultimos_precios_ne[['co_cli', 'co_art', 'doc_num', 'prec_vta_uni']], how='left', left_on=['co_tran', 'co_art'], right_on=['co_cli', 'co_art'], suffixes = ('_t1', '_t2'))
        # asignar precio2 a facturas de ruteros sin despacho previo. Asigna precio 2 del litado de precios
        articulos_precios = self.consultas_generales.art_precio()
        articulos_precio2 = articulos_precios[articulos_precios['co_precio'] == '02'][['co_art', 'co_precio', 'monto']]
        articulos_precio2.set_index(['co_art'], inplace=True)
        merge_facturas_art_profit =  merge(ventas_comercio_rutero_precio2, articulos, how='left', left_on=['co_art'], right_on=['co_art'], suffixes=('_pd', '_artpro'))
        if len(merge_facturas_art_profit) > 0:
            merge_facturas_art_profit['co_cli_t2'] =  merge_facturas_art_profit.apply(lambda x: x['co_tran'] if x['co_cli_t2'] is nan else x['co_cli_t2'], axis=1)
            merge_facturas_art_profit['doc_num_t2'] =  merge_facturas_art_profit.apply(lambda x: 's/despacho' if x['doc_num_t2'] is nan else x['doc_num_t2'], axis=1)
            merge_facturas_art_profit['prec_vta_uni'] =  merge_facturas_art_profit.apply(lambda x: articulos_precio2.loc[x['co_art'], 'monto'] if math.isnan(x['prec_vta_uni']) else x['prec_vta_uni'], axis=1)
            merge_facturas_art_profit['base_precio_2'] =  merge_facturas_art_profit.apply(lambda x: (x['prec_vta_uni'] / x['equivalencia']) * x['total_art'] if x['es_unidad'] else x['prec_vta_uni'] * x['total_art'], axis=1)
            merge_facturas_art_profit['iva_precio_2'] = merge_facturas_art_profit.apply(lambda x: (x['base_precio_2'] * 16 /100) if x['tipo_imp'] == '1' else 0, axis=1)
            merge_facturas_art_profit['total_item_precio_2'] =  round(merge_facturas_art_profit['iva_precio_2'] +  merge_facturas_art_profit['base_precio_2'], ndigits=2)
            merge_facturas_art_profit['ganancia'] =  merge_facturas_art_profit.apply(lambda x: x['monto_base_item'] - x['base_precio_2'], axis=1)
        else:
            merge_facturas_art_profit['total_item_precio_2'] = 0.0
        return merge_facturas_art_profit
    
    def saldo_anterior_calculo_ganacia_por_factura_comercio(self, **kwargs):
        fecha_d = kwargs.get('fecha_d') 
        # converte el formato de fecha pasado por parametro a date, luego resta un día,
        # finalmente devuelve la fecha obtenida en formato fecha requerido
        fecha_h = (datetime.strptime(fecha_d, '%Y%m%d') + timedelta(days=-1)).strftime('%Y%m%d')
        facturas_comercios_ruteros = self.calculo_ganacia_por_factura_comercio(fecha_d='20010101', fecha_h=fecha_h)
        resumen_facturas_comercios = facturas_comercios_ruteros.groupby(['co_tran']).agg({'total_item_precio_2':'sum'}).reset_index()
        resumen_facturas_comercios['fecha_anterior_a'] = datetime.strptime(fecha_d, '%Y%m%d')
        resumen_facturas_comercios.rename(columns={"co_tran": "co_cli", 'total_item_precio_2':'sa_facturas_comerc'}, inplace=True)
        return resumen_facturas_comercios[['fecha_anterior_a', 'co_cli', 'sa_facturas_comerc']]
        
    
    def resumen_movimiento_cuenta(self, **kwargs):
        clientes = DatosProfit(self.conexion).clientes()[['co_cli', 'cli_des', 'tip_cli']]
        ruteros = clientes[clientes['tip_cli'] == 'R']
        # (+ más Notas)
        notas_entrega = self.resumen_nota_entrega_rutero(**kwargs)
        resumen_ne = notas_entrega.groupby(['co_cli']).agg({'total_item':'sum'}).reset_index()
        resumen_ne.rename(columns={'total_item':'total_ne'}, inplace=True)
        # (+ más Facturas directas)
        facturas_directas = self.resumen_facturas_rutero(**kwargs)
        resumen_facturas_directas = facturas_directas.groupby(['co_cli']).agg({'total_item':'sum'}).reset_index()
        resumen_facturas_directas.rename(columns={'total_item':'total_fd'}, inplace=True)
        # (- menos Facturas comercios ruteros)
        facturas_comercios_ruteros = self.calculo_ganacia_por_factura_comercio(**kwargs)
        resumen_facturas_comercios = facturas_comercios_ruteros.groupby(['co_tran']).agg({'total_item_precio_2':'sum'}).reset_index()
        resumen_facturas_comercios.rename(columns={'co_tran':'co_cli', 'total_item_precio_2':'total_fcp2'}, inplace=True)
        # (+- más o menos Ajustes)
        # este monto se maneja por saldo, es decir; una vez cobrado el documento desaparece del edo cta. Rutero
        ajustes = self.ajustes.documentos_ajustes(**kwargs)
        ajutes_ruteros = ajustes[(ajustes['tip_cli'] == 'R') & (~ajustes['co_tipo_doc'].isin(['IVAN', 'AJPA', 'AJNA'])) & (ajustes['co_cta_ingr_egr'] != 'APS')]
        resumen_ajustes = ajutes_ruteros.groupby(['co_cli']).agg({'total_neto':'sum'}).reset_index()
        resumen_ajustes.rename(columns={'total_neto':'total_ajust'}, inplace=True)
        # (- menos cobro documentos)
        cobros = self.cobros.view_cobros_x_cliente(**kwargs)
        resumen_cobros = cobros.groupby(['co_cli']).agg({'cargo':'sum'}).reset_index()
        resumen_cobros.rename(columns={'cargo':'total_cobro'}, inplace=True)
        # (- menos ganancias)
        ajustes_ganancia = self.ajustes.ganancias_aplicadas(**kwargs)
        resumen_ganancias_aplicadas = ajustes_ganancia.groupby(['co_cli']).agg({'total_neto':'sum'}).reset_index()
        resumen_ganancias_aplicadas.rename(columns={'total_neto':'total_ganancia'}, inplace=True)
        # (- menos fondo de garantía)
        fondo_garantia = self.fondo.movimientos_fondo_garantia(**kwargs)
        resumen_fondo_garantia = fondo_garantia.groupby(['co_cli']).agg({'total_fondo':'sum'}).reset_index()
        # MOVIMIENTOS
        merge_rutero_ne = merge(ruteros, resumen_ne, how='left', left_on=['co_cli'], right_on=['co_cli'])
        merge_ne_fact = merge(merge_rutero_ne, resumen_facturas_directas, how='left', left_on=['co_cli'], right_on=['co_cli'])
        merge_ne_fact_fcomer = merge(merge_ne_fact, resumen_facturas_comercios, how='left', left_on=['co_cli'], right_on=['co_cli'])
        merge_ne_fact_fcomer_ajus = merge(merge_ne_fact_fcomer, resumen_ajustes, how='left', left_on=['co_cli'], right_on=['co_cli'])
        merge_ne_fact_fcomer_ajus_cob = merge(merge_ne_fact_fcomer_ajus, resumen_cobros, how='left', left_on=['co_cli'], right_on=['co_cli'])
        merge_ganancia = merge(merge_ne_fact_fcomer_ajus_cob, resumen_ganancias_aplicadas, how='left', left_on=['co_cli'], right_on=['co_cli'])
        movimientos = merge(merge_ganancia, resumen_fondo_garantia, how='left', left_on=['co_cli'], right_on=['co_cli'])
        movimientos = movimientos.infer_objects(copy=False).replace(nan, 0)  # Reemplaza todos los valores nan por cero 0
        # SALDO ANTERIOR
        sa_notas = self.notas_entrega.saldo_anterior_notas(**kwargs)
        sa_facturas = self.facturas_saldo_ant.saldo_anterior_facturas_ventas(**kwargs)
        sa_fact_comercios_ruta = self.saldo_anterior_calculo_ganacia_por_factura_comercio(**kwargs)
        sa_ajustes = self.ajustes.saldo_anterior_ajustes(**kwargs)
        sa_cobros = self.cobros.saldo_anterior_view_cobros_x_cliente(**kwargs)
        sa_ganancias_aplicadas = self.ajustes.saldo_anterior_ganancias_aplicadas(**kwargs)
        sa_fondo = self.fondo.saldo_anterior_fondo_garantia(**kwargs)
        df_list = [sa_notas, sa_facturas, sa_fact_comercios_ruta, sa_ajustes, sa_cobros, sa_ganancias_aplicadas, sa_fondo]
        # Agrupa los dataframe vacios en una lista para luego determinar su cantidad y comparar con la lista de dataframes
        lista_vacios = [df for df in df_list if df.empty]
        # Si al menos existe un dataframe de saldos anteriores combinar
        # por ejemplo cuando se consulta entre fechas que cubre todos los movimientos 
        if len(lista_vacios) != len(df_list): 
            # Prevee el caso de un dataframe o marco de datos vacío en df_list
            saldo_anterior = concat([df for df in df_list if not df.empty],
                                    ignore_index=True, 
                                    axis=0)
            # Si al menos existe un dataframe vacio combinar con saldo_anterior
            # por ejemplo cuando se consultan fechas donde hay dataframes de saldos anteriores vacios 
            if len(lista_vacios) > 0:
                # Concatena todos los dataframes vacios para usar las columnas en el groupby de saldo_anterior
                df_vacios = concat([df for df in df_list if df.empty])
                saldo_anterior = merge(saldo_anterior, df_vacios, how="outer")
            saldo_anterior = saldo_anterior.groupby(['fecha_anterior_a', 
                                                    'co_cli']).agg({'sa_nota_e':'sum',
                                                                    'sa_facturas':'sum',
                                                                    'sa_facturas_comerc':'sum',
                                                                    'sa_cobros':'sum',
                                                                    'sa_gan_aplicadas':'sum',
                                                                    'sa_ajustes':'sum',
                                                                    'sa_fondo':'sum'}).reset_index()
            saldo_anterior = saldo_anterior.infer_objects(copy=False).replace(nan, 0)  # Reemplaza todos los valores nan por cero 0
            saldo_anterior['sa_total'] = saldo_anterior['sa_nota_e'] + saldo_anterior['sa_facturas'] - saldo_anterior['sa_facturas_comerc'] - saldo_anterior['sa_cobros'] - saldo_anterior['sa_gan_aplicadas'] + saldo_anterior['sa_ajustes'] - saldo_anterior['sa_fondo']
        else:
            saldo_anterior = DataFrame([['000', 0.0]], columns=['co_cli', 'sa_total'])
        edo_cta = merge(saldo_anterior[['co_cli', 'sa_total']], movimientos, how='outer')
        edo_cta = edo_cta.infer_objects(copy=False).replace(nan, 0)  # Reemplaza todos los valores nan por cero 0
        edo_cta['saldo'] = round(edo_cta['sa_total'] + edo_cta['total_ne'] + edo_cta['total_fd'] - edo_cta['total_fcp2'] + edo_cta['total_ajust'] - edo_cta['total_cobro'] - edo_cta['total_ganancia'] - edo_cta['total_fondo'], ndigits=2)
        edo_cta = edo_cta[edo_cta['saldo'] != 0.00]
        return edo_cta[['co_cli', 'cli_des', 'tip_cli', 'sa_total', 
                        'total_ne', 'total_fd', 'total_fcp2', 
                        'total_ajust', 'total_cobro', 'total_ganancia',
                        'total_fondo', 'saldo']]
    
    def movimiento_cuenta_rutero_x_dia(self, **kwargs):
        clientes = DatosProfit(self.conexion).clientes()[['co_cli', 'cli_des']]
        # (+ más Notas)
        notas_entrega = self.resumen_nota_entrega_rutero(**kwargs)[['co_cli', 'fec_emis', 'total_item']]
        notas_entrega.rename(columns={'total_item':'total_ne'}, inplace=True)
        if len(notas_entrega):
            notas_entrega['fec_emis'] = notas_entrega['fec_emis'].dt.normalize()
            notas_entrega['fec_emis'] = notas_entrega['fec_emis'].dt.normalize()
            notas_entrega = notas_entrega.groupby(['co_cli', 'fec_emis']).agg({'total_ne': 'sum'}).reset_index() 
        # (+ más Facturas directas)
        facturas_directas = self.resumen_facturas_rutero(**kwargs)[['co_cli', 'fec_emis', 'total_item']]
        facturas_directas.rename(columns={'total_item':'total_fd'}, inplace=True)
        if len(facturas_directas):
            facturas_directas['fec_emis'] = facturas_directas['fec_emis'].dt.normalize()
            facturas_directas = facturas_directas.groupby(['co_cli', 'fec_emis']).agg({'total_fd':'sum'}).reset_index()
        # (- más Facturas comercios ruteros)
        facturas_comercios_ruteros = self.calculo_ganacia_por_factura_comercio(**kwargs)[['co_tran', 'fec_emis', 'total_item_precio_2']]
        facturas_comercios_ruteros.rename(columns={'co_tran':'co_cli', 'total_item_precio_2':'total_fcp2'}, inplace=True)
        if len(facturas_comercios_ruteros):
            facturas_comercios_ruteros['fec_emis'] = facturas_comercios_ruteros['fec_emis'].dt.normalize()
            facturas_comercios_ruteros = facturas_comercios_ruteros.groupby(['co_cli', 'fec_emis']).agg({'total_fcp2':'sum'}).reset_index()
        # (+- más o menos Ajustes)
        # este monto se maneja por saldo, es decir; una vez cobrado el documento desaparece del edo cta. Rutero
        ajustes_ruteros = self.ajustes.documentos_ajustes(**kwargs)[['co_cli', 'co_tipo_doc', 'tip_cli', 'co_cta_ingr_egr', 'fec_emis', 'total_neto']]
        ajustes_ruteros.rename(columns={'total_neto':'total_ajust'}, inplace=True)
        if len(ajustes_ruteros) > 0:
            ajustes_ruteros = ajustes_ruteros[(ajustes_ruteros['tip_cli'] == 'R') & (~ajustes_ruteros['co_tipo_doc'].isin(['IVAN', 'AJPA', 'AJNA'])) & (ajustes_ruteros['co_cta_ingr_egr'] != 'APS')].copy()
            ajustes_ruteros['fec_emis'] = ajustes_ruteros['fec_emis'].dt.normalize()
            ajustes_ruteros = ajustes_ruteros.groupby(['co_cli', 'fec_emis']).agg({'total_ajust':'sum'}).reset_index()
        # (- menos cobro documentos)
        cobros = self.cobros.view_cobros_x_cliente(**kwargs)[['co_cli', 'fecha', 'cargo']]
        cobros.rename(columns={'fecha':'fec_emis', 'cargo':'total_cobro'}, inplace=True)
        if len(cobros) > 0:
            cobros['fec_emis'] = cobros['fec_emis'].dt.normalize()
            cobros = cobros.groupby(['co_cli', 'fec_emis']).agg({'total_cobro':'sum'}).reset_index()
        # (- menos ganancias)
        ganancias_aplicadas = self.ajustes.ganancias_aplicadas(**kwargs)[['co_cli', 'fec_emis', 'total_neto']]
        ganancias_aplicadas.rename(columns={'total_neto':'total_ganancia'}, inplace=True)
        if len(ganancias_aplicadas) > 0 :
            ganancias_aplicadas['fec_emis'] = ganancias_aplicadas['fec_emis'].dt.normalize()
            ganancias_aplicadas = ganancias_aplicadas.groupby(['co_cli', 'fec_emis']).agg({'total_ganancia':'sum'}).reset_index()
        # (- menos fondo de garantía)
        fondo_garantia = self.fondo.movimientos_fondo_garantia(**kwargs)[['co_cli', 'fec_emis', 'total_fondo']]
        if len(fondo_garantia) > 0 :
            fondo_garantia['fec_emis'] = fondo_garantia['fec_emis'].dt.normalize()
            fondo_garantia = fondo_garantia.groupby(['co_cli', 'fec_emis']).agg({'total_fondo':'sum'}).reset_index()
        # ESTADO DE CUENTA
        df_fechas = DataFrame(date_range(start='2021-01-01', end='2021-01-01', freq='B'), columns=['fec_emis'])
        notas_entrega = merge(df_fechas, notas_entrega, how='outer')
        #f_notas_entrega_sum.to_excel('f_notas_entrega_sum.xlsx')
        notas_entrega = notas_entrega[['fec_emis', 'co_cli', 'total_ne']]
        facturas_directas = merge(notas_entrega, facturas_directas, how='outer')
        facturas_comercios = merge(facturas_directas, facturas_comercios_ruteros, how='outer')
        ajustes_ruteros = merge(facturas_comercios, ajustes_ruteros, how='outer')
        cobros = merge(ajustes_ruteros, cobros, how='outer')
        ganancias = merge(cobros, ganancias_aplicadas, how='outer')
        fondo = merge(ganancias, fondo_garantia, how='outer')
        fondo = fondo[~fondo['co_cli'].isnull()]
        columns_edo = ['fec_emis', 'fec_mid', 'co_cli', 'cli_des', 'total_ne', 'total_fd', 'total_fcp2', 'total_ganancia', 'total_ajust', 'total_cobro', 'total_fondo']
        if len(fondo) > 0:
            movimiento_cuenta_x_dia = fondo.infer_objects(copy=False).replace(nan, 0)  # Reemplaza todos los valores nan por cero 0
            locale.setlocale(locale.LC_ALL, 'es_ES')   
            movimiento_cuenta_x_dia['fec_mid'] = movimiento_cuenta_x_dia['fec_emis'].dt.strftime('%a').str.upper()
            locale.setlocale(locale.LC_ALL, '')
            edo_cta = merge(movimiento_cuenta_x_dia, clientes, how='left', left_on='co_cli', right_on='co_cli')
        else:
            fondo['fec_mid'] = nan
            fondo['cli_des'] = nan
            edo_cta = fondo[columns_edo]
        return edo_cta[columns_edo]
    
    def calculo_ganacia_por_factura_comercio_historica(self):
        detalle_facturas = self.ventas.data_factura_venta_con_detalle()
        #pedidos_facturados = detalle_facturas[detalle_facturas['tipo_doc_origen']=='PCLI']
        #resumen_pedidos_facturados = pedidos_facturados.groupby(['tipo_doc_origen', 'num_doc']).value_counts().reset_index()
        pedidos = self.pedidos.data_pedido_con_detalle()
        # agrupa por numero de pedido y numero de devolucion calculando el tamaño de los grupos.
        resumen_pedido = pedidos.groupby(['doc_num', 'campo8'], sort=False, as_index=False).size().reset_index(drop=True)
        resumen_pedido.rename(columns={'doc_num':'doc_num_ped', 'campo8':'campo8_ped'}, inplace=True)
        merge_detalle_facturas_pedidos = merge(detalle_facturas, 
                                               resumen_pedido, 
                                               how='left', 
                                               left_on='num_doc', 
                                               right_on='doc_num_ped')
        #Filtrar sólo aquellas facturas asociadas a un pedido
        merge_detalle_facturas_pedidos = merge_detalle_facturas_pedidos[merge_detalle_facturas_pedidos['tipo_doc_origen'] == 'PCLI']
        merge_detalle_facturas_pedidos.rename(columns={'campo8_ped':'doc_num_dev'}, inplace=True)
        
        detalle_devoluciones = self.devoluciones_consultas.data_devolucion_con_detalle(anio='all', mes='all')[['doc_num', 
                                                                                                            'co_art',  
                                                                                                            'es_unidad', 
                                                                                                            'equivalencia', 
                                                                                                            'prec_vta']]
        detalle_devoluciones.rename(columns={'prec_vta':'prec_vta_uni_p2', 'doc_num':'doc_num_dev'}, inplace=True)
                                               
        detalle_fact_precio_dos = merge(merge_detalle_facturas_pedidos, detalle_devoluciones, how='left', left_on=['doc_num_dev', 'co_art'], right_on=['doc_num_dev', 'co_art']) 
        detalle_fact_precio_dos['monto_base_p2'] = detalle_fact_precio_dos['prec_vta_uni_p2'] * detalle_fact_precio_dos['total_art']
        detalle_fact_precio_dos['ganancia'] = round(detalle_fact_precio_dos['monto_base_item'] - detalle_fact_precio_dos['monto_base_p2'], ndigits=2)
        return detalle_fact_precio_dos
          
    

       
