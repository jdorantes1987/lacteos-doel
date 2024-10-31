import os
from user.control_usuarios import ControlAcceso
from scripts.conexion import ConexionBD
from scripts.consultas_generales import ConsultasGenerales
from scripts.notas_entrega_consultas import NotasEntregaConsultas
from scripts.pedidos import PedidosVentasConsultas
from scripts.estado_cuenta_rutero import EstadoCuentaRutero
from scripts.devoluciones import Devoluciones
from scripts.ajustes import Ajustes
from scripts.stock import Stock
from scripts.notas_entrega_cxc import NotasEntregaACxc
from scripts.datos_profit import DatosProfit
from scripts.update_all import UpdateAll
from scripts.cliientes import Clientes
from scripts.facturas_ventas import FacturaVentasConsultas
from scripts.bcv.bcv_estadisticas_tasas import actulizar_file_tasas
from scripts.cxc import CXC
from scripts.libro_compra_venta import LibroCompraVenta
from scripts.inventario import Inventario
from scripts.compras import ComprasConsultas 
from scripts.cobros import Cobros
from scripts.devoluciones_consultas import DevolucionesConsultas
from scripts.fondo_garantia import FondoGarantia




conexion = ConexionBD(base_de_datos='LDOEL_A')

#dev = ConsultasGenerales(conexion)
#print(dev.get_last_number_devol())

# fact = PedidosVentasConsultas(conexion)
# fact.data_pedido_con_detalle(anio='all', mes='all').to_excel('data_pedido_con_detalle.xlsx')

#NotasEntregaConsultas(conexion).data_notas_entrega_con_detalle(anio='all', mes='all').to_excel('data_notas_entrega_con_detalle.xlsx')

# print(ConsultasGenerales(conexion).resumen_inventario_x_articulo())
# EstadoCuentaRutero(conexion).datos_ganacia_por_factura_a_comercios(anio='all', mes='all').to_excel('datos_ganacia_por_factura_a_comercios.xlsx')
#EstadoCuentaRutero(conexion).resumen_nota_entrega(anio='all', mes='all').to_excel('resumen_nota_entrega.xlsx')
#EstadoCuentaRutero(conexion).resumen_ganancia(anio='all', mes='all').to_excel('resumen_ganancia.xlsx')
# Stock(conexion).update_stock()
#Devoluciones(conexion).data_devolucion_con_detalle(anio='all', mes='all').to_excel('data_devolucion_con_detalle.xlsx')
#print(DatosProfit(conexion).encabezado_factura_ventas(fecha_ini='20240819 00:00:00', fecha_fin='20240823 23:59:59')['campo1'])
#UpdateAll(conexion).agregar_info_tasa_facturas(fecha_ini='20240823 00:00:00', fecha_fin='20240829 23:59:59')
#df = DatosProfit(conexion).clientes()
#df2 = df[df['co_cli']=='999']
#Clientes(ConexionBD(base_de_datos='LDOEL_A')).exe_sql_insert_cliente(datos=df2)
# print(Clientes(conexion).clientes_por_sinc_doel())
#print(CXC(conexion).view_cxc())
#print(LibroCompraVenta(conexion).libro_compras(fecha_d='20240901', fecha_h='20240904'))
Inventario(conexion).resumen_mov_inventario_filtrado(fecha_d='20241001', fecha_h='20241031').to_excel('resumen_mov_inventario_filtrado.xlsx')
#print(Inventario(conexion).resumen_inventario_x_articulo_sin_facturas_almacen_principal())
#EstadoCuentaRutero(conexion).calculo_ganacia_por_factura_comercio(anio='all', mes='all').to_excel('calculo_ganacia_por_factura_comercio.xlsx')
#EstadoCuentaRutero(conexion).resumen_facturas_comercio_rutero(anio='all', mes='all').to_excel('resumen_facturas_comercio_rutero.xlsx')
#FacturaVentasConsultas(conexion).data_factura_venta_sin_ruta(fecha_d='20241001', fecha_h='20241025').to_excel('data_factura_venta_sin_ruta.xlsx')
#NotasEntregaConsultas(conexion).data_notas_entrega_con_detalle(anio='all', mes='all').to_excel('data_notas_entrega_con_detalle.xlsx')
#NotasEntregaConsultas(conexion).ultimos_precios_notas(anio='all', mes='all').to_excel('ultimos_precios_notas.xlsx')
#print(ComprasConsultas(conexion).datos_vencimientos_productos())
#EstadoCuentaRutero(conexion).resumen_movimiento_cuenta(anio='all', mes='all').to_excel('resumen_movimiento_cuenta.xlsx')
#DevolucionesConsultas(conexion).data_devolucion_con_detalle(anio='all', mes='all').to_excel('data_devolucion_con_detalle.xlsx')
#Devoluciones(conexion).datos_devolucion(anio='all', mes='all').to_excel('datos_devolucion.xlsx')
#cobros = Cobros(conexion).view_cobros_x_cliente()
#cobros.to_excel('view_cobros_x_cliente.xlsx')
#print(Ajustes(conexion).ganancias_aplicadas())
#print(str(str(int(ConsultasGenerales(conexion).get_last__nro_ajuste_negativo()) + 1).zfill(10)))
#ControlAcceso(conexion).aut_user(user='YRODRI', pw='1234')
#FondoGarantia(conexion).movimientos_fondo_garantia(anio='all', mes='all').to_excel('movimientos_fondo_garantia.xlsx')
