from pandas import read_excel, merge_asof, DataFrame, concat
from scripts.notas_entrega_consultas import NotasEntregaConsultas
from scripts.datos_profit import DatosProfit
from scripts.facturas_ventas import FacturaVentasConsultas

path_file_fondo_garantia = './tabla_fondo_de_garantia.xlsx'

class FondoGarantia:
    
    def __init__(self, conexion):
        self.conexion = conexion
        self.notas_entrega = NotasEntregaConsultas(conexion)
        self.datos_profit = DatosProfit(self.conexion)
        self.ventas = FacturaVentasConsultas(conexion)
        
    def movimientos_fondo_garantia(self, anio, mes):
        fondo_garantia = DataFrame(columns=['co_cli', 'co_art', 'doc_num', 'fec_emis', 'co_uni', 'total_art', 'valor', 'total_fondo'])
        articulos_unidad = self.datos_profit.unidades()
        set_unidades_manejan_fondo = set(articulos_unidad[articulos_unidad['campo1'] == 'FG']['co_art'])  #  FG = Fondo de Garantia
        tabla_fondo_garantia = read_excel(path_file_fondo_garantia, dtype={'co_cli':'object'}, parse_dates=['fec_emis'])
        set_clientes_fondo = set(tabla_fondo_garantia['co_cli'])
        movimientos_nota_entrega = self.notas_entrega.data_notas_entrega_con_detalle(anio=anio, mes=mes)[['co_cli', 'co_art', 'doc_num', 'fec_emis', 'co_uni', 'total_art']]
        movimientos_nota_entrega = movimientos_nota_entrega[(movimientos_nota_entrega['co_cli'].isin(set_clientes_fondo)) & (movimientos_nota_entrega['co_uni'].isin(set_unidades_manejan_fondo))]
        movimientos_nota_entrega['fec_emis'] = movimientos_nota_entrega['fec_emis'].dt.normalize()
        if len(movimientos_nota_entrega) > 0 and len(tabla_fondo_garantia) > 0 :
            fondo_garantia_ne = merge_asof(movimientos_nota_entrega, tabla_fondo_garantia, on='fec_emis', by='co_cli')  # Combinar por aproximación
            fondo_garantia_ne['total_fondo'] = fondo_garantia_ne['total_art'] * fondo_garantia_ne['valor']
        ventas = self.ventas.data_factura_venta_con_detalle(anio=anio, mes=mes)[['co_cli', 'co_art', 'doc_num', 'fec_emis', 'tip_cli', 'co_uni', 'total_art']]
        ventas_ruteros = ventas[ventas['tip_cli'] == 'R'].copy()
        ventas_ruteros['fec_emis'] = ventas_ruteros['fec_emis'].dt.normalize()
        ventas_ruteros = ventas_ruteros[(ventas_ruteros['co_cli'].isin(set_clientes_fondo)) & (ventas_ruteros['co_uni'].isin(set_unidades_manejan_fondo))]
        if len(ventas_ruteros) > 0 and len(tabla_fondo_garantia) > 0 :
            fondo_garantia_fact = merge_asof(ventas_ruteros, tabla_fondo_garantia, on='fec_emis', by='co_cli')
            fondo_garantia_fact['total_fondo'] = fondo_garantia_fact['total_art'] * fondo_garantia_fact['valor']
        fondo_garantia = concat([fondo_garantia_ne, fondo_garantia_fact], axis=0, ignore_index=True)
        return fondo_garantia
        
        
        
    