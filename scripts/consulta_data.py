import os
from datetime import datetime
# from gestion_user.usuarios import ClsUsuarios
from scripts.datos_profit import DatosProfit

class ClsData:
    @staticmethod
    def audit(method):
        def wrapper(self, *args, **kwargs):
            today = datetime.now()
            # print(f'Fecha: {today} Usuario: {ClsUsuarios.nombre()} running: {method.__name__}')
            return method(self, *args, **kwargs)  # Ojo llamada!
        return wrapper
    
    def __init__(self, conexion):
        self.odata = DatosProfit(conexion)
       
    def ventas_dt(self, **kwargs):
        return self.odata.ventas_con_detalle(**kwargs)
    
    def ventas_rsm(self, **kwargs):
        return self.odata.ventas_sin_detalle(**kwargs)
    
    def ventas_dicc(self, **kwargs):
        return self.odata.dicc_ventas_total_por_anio(**kwargs)
    
    def ventas_dicc_x_vendedor(self, **kwargs):
        return (
            self.ventas_dicc(**kwargs)
            if kwargs.get('vendedor') == 'Todos'
            else self.odata.dicc_ventas_total_por_anio_vendedor(**kwargs)
        )
    
    def cuentas_por_cobrar_agrupadas(self, **kwargs):
        return self.odata.cxc_clientes_resum_grouped(**kwargs)
    
    def cuentas_por_cobrar_det(self, **kwargs):
        return self.odata.facturacion_saldo_x_clientes_detallado(**kwargs)
    
    # @audit
    # def cuentas_por_cobrar_pivot(self, anio, mes, usd, vendedor):
    #     return self.odata.cxc_clientes_resum_pivot(anio=anio, mes=mes, usd=usd, vendedor=vendedor)
    
    def generar_cod_cliente(self):
        return self.odata.new_cod_client()
    
    def articulos(self):
       return self.odata.articulos_profit()    
    
    def clientes(self):
       return self.odata.clientes()
    
    def clintes_search(self, str_search, resumir_info):
        return self.odata.search_clients(str_search, resumir_datos=resumir_info)
    
    def get_tasa_bcv_dia(self):
        return self.odata.get_monto_tasa_bcv_del_dia()
    
    def get_fecha_tasa_bcv_dia(self):
        return self.odata.get_fecha_tasa_bcv_del_dia()
    
    def articulos(self):
        return self.odata.articulos_profit()
    
    def data_documentos(self, anio, mes, tipo_doc):
        return self.odata.data_documentos(anio=anio, mes=mes, tipo_doc=tipo_doc)
    
    def encabezado_notas_entrega(self):
        return self.odata.encabezado_notas_entrega()
    
