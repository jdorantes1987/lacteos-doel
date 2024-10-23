from scripts.transacciones import GestorTransacciones
from scripts.sql_read import get_read_sql


class AddDocumento:
        def __init__(self, conexion):
                self.conexion = conexion #  Crea un objeto conexión
                self.conexion.conectar()  # inicia la conexión
                self.gestor_trasacc = GestorTransacciones(self.conexion)
                self.gestor_trasacc.iniciar_transaccion()
                self.cursor = self.gestor_trasacc.get_cursor()
                
        def exe_sql_insert_doc(self, tip_doc, id_doc, descrip, cod_cli, vendedor, fecha_fact, fecha_cur, monto_base, monto_iva,
                               monto_total, nro_control, sucursal, user, cta_ie, doc_orig, num_orig):

                # SQL para insertar el documento, se coloca dentro del insert encabezado de factura ya que usa los mismos datos
                strsql = "INSERT INTO [dbo].[saDocumentoVenta] ([co_tipo_doc],[nro_doc],[co_cli],[co_ven],[co_mone]," \
                        "[mov_ban],[tasa],[observa],[fec_reg],[fec_emis],[fec_venc],[anulado],[aut],[contrib],[doc_orig]," \
                        "[tipo_origen],[nro_orig],[nro_che],[saldo],[total_bruto],[porc_desc_glob],[monto_desc_glob]," \
                        "[porc_reca],[monto_reca],[total_neto],[monto_imp],[monto_imp2],[monto_imp3],[tipo_imp],[tipo_imp2]," \
                        "[tipo_imp3],[porc_imp],[porc_imp2],[porc_imp3],[num_comprobante],[feccom],[numcom],[n_control]," \
                        "[dis_cen],[comis1],[comis2],[comis3],[comis4],[comis5],[comis6],[adicional],[salestax],[ven_ter]," \
                        "[impfis],[impfisfac],[imp_nro_z],[otros1],[otros2],[otros3],[campo1],[campo2],[campo3],[campo4]," \
                        "[campo5],[campo6],[campo7],[campo8],[co_us_in],[co_sucu_in],[fe_us_in],[co_us_mo],[co_sucu_mo]," \
                        "[fe_us_mo],[co_cta_ingr_egr]) " \
                        "VALUES ('{tdoc}','{doc}','{c_cli}','{ven}','BS', NULL, 1, '{descr}', '{f_fact}'," \
                        "'{f_fact}','{f_fact}',0,1,0,'{d_orig}', 0,'{n_orig}',NULL,{m_total},{m_base},NULL,0,NULL,0," \
                        "{m_total},{m_iva},0,0,'7',NULL,NULL,0,0,0,NULL,NULL,NULL,'{n_contr}',NULL,0,0,0,0,0,0,0,NULL,0,NULL,NULL,NULL," \
                        "0,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'{p_user}','{suc}','{f_act}','{p_user}','{suc}'," \
                        "'{f_act}', '{cie}')".format(tdoc=tip_doc,
                                                doc=id_doc,
                                                descr=descrip,
                                                c_cli=cod_cli,
                                                ven=vendedor,
                                                f_fact=fecha_fact,
                                                f_act=fecha_cur,
                                                m_base=monto_base,
                                                m_iva=monto_iva,
                                                m_total=monto_total,
                                                n_contr=nro_control,
                                                suc=sucursal,
                                                p_user=user,
                                                cie=cta_ie,
                                                d_orig=doc_orig,
                                                n_orig=num_orig)    
                self.cursor.execute(strsql)
                
        def confirmar_transaccion(self):
            self.gestor_trasacc.confirmar_transaccion()
            