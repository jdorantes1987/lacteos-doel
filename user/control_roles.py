from scripts.sql_read import get_read_sql
from user.usuarios_roles import ClsUsuariosRoles

def __dict_users_rols__(id_user, conexion):
    sql = f"""
          select * from usuarios_roles where idusuario ='{id_user}'
          """
    df = get_read_sql(sql=sql, 
                      conexion = conexion)
    users = df.set_index('modulo')['habilitado']
    return users.to_dict()

def set_roles(id_user, conexion):
    diccionario_roles = __dict_users_rols__(id_user, conexion)
    ClsUsuariosRoles(diccionario_roles)



