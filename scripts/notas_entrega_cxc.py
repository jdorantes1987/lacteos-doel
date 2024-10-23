import os
from  user import usuarios
from scripts.add_doc import AddDocumento
from scripts.consulta_data import ClsData

class NotasEntregaACxc:
        def __init__(self, conexion):
                self.conexion = conexion #  Crea un objeto conexión
                self.conexion.conectar()  # inicia la conexión
                self.cursor = self.gestor_trasacc.get_cursor()
                self.oData = ClsData(conexion)
                self.add_doc = AddDocumento(conexion)
                
        def set_numeros_notas_entrega_profit(self):
                return set(self.oData.encabezado_notas_entrega()['doc_num'])
        
        def set_documentos_notas_entrega_profit(self):
                return set(self.oData.data_documentos(anio='all',
                                                      mes='all',
                                                      tipo_doc='NENT')['doc_num'])
        
        def set_numeros_notas_entrega_por_agregar(self):
            return self.set_numeros_notas_entrega_profit() - self.set_documentos_notas_entrega_profit()    
                
                
        def df_notas_de_entrega_por_agregar(self):
                numeros_notas_entrega_por_agregar = self.set_numeros_notas_entrega_por_agregar()    
                encabezado_notas_de_entrega = self.oData.encabezado_notas_entrega()   
                return encabezado_notas_de_entrega[encabezado_notas_de_entrega['doc_num'].isin(numeros_notas_entrega_por_agregar)]
                
        def agregar_notas_entrega_a_cxc(self):
            notas_entrega_por_agregar = self.df_notas_de_entrega_por_agregar()
            user = usuarios.ClsUsuarios.id_usuario()
            for index, row in notas_entrega_por_agregar.iterrows():
               self.add_doc.exe_sql_insert_doc('NENT', 
                                                row["doc_num"],
                                                row["descrip"],
                                                row["co_cli"],
                                                row["co_ven"],
                                                row["fec_emis"].strftime('%Y%m%d %H:%M:%S'),
                                                row["fec_reg"].strftime('%Y%m%d %H:%M:%S'),
                                                row["total_bruto"],
                                                row["monto_imp"],
                                                row["total_neto"],
                                                row["n_control"],
                                                row["co_sucu_in"],
                                                user,
                                                '')
            self.add_doc.confirmar_transaccion()    
            return notas_entrega_por_agregar 



