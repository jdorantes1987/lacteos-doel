from scripts.sql_read import get_read_sql

class ComprasConsultas:
    def __init__(self, conexion):
        self.conexion = conexion

    def datos_vencimientos_productos(self):
        sql = f"""
               SELECT RTRIM(fc.doc_num) AS doc_num, RTRIM(fc.nro_fact) AS nro_fact, fc.fec_emis, RTRIM(fc.co_prov) AS co_prov, p.prov_des, RTRIM(fcr.co_art) AS co_art,
                      a.art_des, fcr.total_art, fcr.comentario
               FROM saFacturaCompra AS fc LEFT JOIN saFacturaCompraReng AS fcr ON fc.doc_num = fcr.doc_num 
                                          LEFT JOIN saProveedor AS p ON fc.co_prov = p.co_prov
                                          LEFT JOIN saArticulo AS a ON fcr.co_art = a.co_art
               """
        cxc = get_read_sql(sql, self.conexion)
        return cxc