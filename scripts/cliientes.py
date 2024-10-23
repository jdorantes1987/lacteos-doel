import os
from scripts.transacciones import GestorTransacciones 
from scripts.datos_profit import DatosProfit
from scripts.conexion import ConexionBD

class Clientes:
        def __init__(self, conexion):
                self.conexion = conexion #  Crea un objeto conexión
                self.conexion.conectar()  # inicia la conexión
                self.gestor_trasacc = GestorTransacciones(self.conexion)
                self.gestor_trasacc.iniciar_transaccion()
                self.cursor = self.gestor_trasacc.get_cursor()

        def set_codigos_clientes_doel(self):
            return set(DatosProfit(ConexionBD(base_de_datos=os.getenv('DB_NAME_PROFIT_DOEL'))).clientes()['co_cli'])
                  
        def set_codigos_clientes_pana(self):
            return set(DatosProfit(ConexionBD(base_de_datos=os.getenv('DB_NAME_PROFIT_PANA'))).clientes()['co_cli'])
        
        def clientes_por_sinc_doel(self):
            codigod_x_sinc_doel = self.set_codigos_clientes_doel()
            codigod_x_sinc_pana = self.set_codigos_clientes_pana()
            codigod_x_sinc =  codigod_x_sinc_pana - codigod_x_sinc_doel
            data_clientes = DatosProfit(ConexionBD(base_de_datos=os.getenv('DB_NAME_PROFIT_PANA'))).clientes()
            return data_clientes[data_clientes['co_cli'].isin(codigod_x_sinc)]
        
        def clientes_por_sinc_pana(self):
            codigod_x_sinc_doel = self.set_codigos_clientes_doel()
            codigod_x_sinc_pana = self.set_codigos_clientes_pana()
            codigod_x_sinc =  codigod_x_sinc_doel - codigod_x_sinc_pana
            data_clientes = DatosProfit(ConexionBD(base_de_datos=os.getenv('DB_NAME_PROFIT_DOEL'))).clientes()
            return data_clientes[data_clientes['co_cli'].isin(codigod_x_sinc)]

        def exe_sql_insert_cliente(self, datos):
            clientes = datos.copy()
            clientes['fecha_reg'] = clientes['fecha_reg'].dt.strftime('%Y%m%d %H:%M:%S')
            clientes['fe_us_in'] = clientes['fe_us_in'].dt.strftime('%Y%m%d %H:%M:%S')
            clientes['fe_us_mo'] = clientes['fe_us_mo'].dt.strftime('%Y%m%d %H:%M:%S')
            for index, row in clientes.iterrows():
                index += 1
                data_datalle = f"""
                            '{row['co_cli']}', '{row['tip_cli']}', '{row['cli_des']}', '{row['direc1']}','{row['dir_ent2']}', '{row['direc2']}', '{row['telefonos']}' , '{row['fax']}', {row['inactivo']}, '{row['comentario']}',  
                            '{row['respons']}', '{row['fecha_reg']}', {row['puntaje']}, {row['mont_cre']},'{row['co_mone']}', '{row['cond_pag']}' , '{row['plaz_pag']}', {row['desc_ppago']}, '{row['co_zon']}', '{row['co_seg']}',   
                             '{row['co_ven']}', {row['desc_glob']}, '{row['horar_caja']}', '{row['frecu_vist']}', {row['lunes']}, {row['martes']} , {row['miercoles']}, {row['jueves']}, {row['viernes']}, {row['sabado']},   
                             {row['domingo']}, '{row['rif']}', '{row['nit']}', {row['contrib']},'{row['numcom']}', '{row['feccom']}' , '{row['dis_cen']}', '{row['email']}', '{row['co_cta_ingr_egr']}', {row['juridico']},   
                             {row['tipo_adi']}, '{row['matriz']}', '{row['co_tab']}', '{row['tipo_per']}', {row['valido']}, '{row['ciudad']}' , '{row['zip']}', '{row['login']}', '{row['password']}', '{row['website']}',   
                            {row['sincredito']}, {row['contribu_e']}, {row['rete_regis_doc']}, {row['porc_esp']},'{row['co_pais']}', '{row['serialp']}' , '{row['Id']}', '{row['salestax']}', '{row['estado']}', '{row['campo1']}',   
                            '{row['campo2']}', '{row['campo3']}', '{row['campo4']}', '{row['campo5']}','{row['campo6']}', '{row['campo7']}' , '{row['campo8']}', '{row['co_us_in']}', '{row['fe_us_in']}', '{row['co_sucu_in']}',   
                            '{row['co_us_mo']}', '{row['fe_us_mo']}', '{row['co_sucu_mo']}'
                            """.replace("'None'", 'null').replace('True', '1').replace('False', '0')
                        
                sql = f"""INSERT INTO saCliente (co_cli, tip_cli, cli_des, direc1, dir_ent2, direc2, telefonos, fax, inactivo, comentario, 
                                                  respons, fecha_reg, puntaje, mont_cre, co_mone, cond_pag, plaz_pag, desc_ppago, co_zon, co_seg, 
                                                  co_ven, desc_glob, horar_caja, frecu_vist, lunes, martes, miercoles, jueves, viernes, sabado, 
                                                  domingo, rif, nit, contrib, numcom, feccom, dis_cen, email, co_cta_ingr_egr, juridico, 
                                                  tipo_adi, matriz, co_tab, tipo_per, valido, ciudad, zip, login, password, website, 
                                                  sincredito, contribu_e, rete_regis_doc, porc_esp, co_pais, serialp, Id, salestax, estado, campo1, 
                                                  campo2, campo3, campo4, campo5, campo6, campo7, campo8, co_us_in, fe_us_in, co_sucu_in, 
                                                  co_us_mo, fe_us_mo, co_sucu_mo) 
                                        VALUES({data_datalle})"""
                self.cursor.execute(sql)  
                self.gestor_trasacc.confirmar_transaccion()  
            