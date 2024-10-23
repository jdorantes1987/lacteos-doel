from scripts.sql_read import get_read_sql
from  user import usuarios, control_roles
from scripts.transacciones import GestorTransacciones


class ControlAcceso:
    def __init__(self, conexion):
            self.conexion = conexion
              
    def data_user(self, user, pw):
        sql = f"""
            select * from usuarios where idusuario ='{user}' and PWDCOMPARE('{pw}', passw) = 1
            """
        return get_read_sql(sql=sql,
                            conexion=self.conexion)

    def aut_user(self, user, pw):
        aut = False
        df_users = self.data_user(user, pw)
        if len(df_users) > 0:
            usuarios.ClsUsuarios(df_users['idusuario'][0], df_users['nombre'][0], df_users['categoria'][0])
            control_roles.set_roles(user, self.conexion)
            aut = True  
        return aut

    def change_password(self, user, pw):
        gestor_trasacc = GestorTransacciones(self.conexion)
        cursor = gestor_trasacc.get_cursor()
        gestor_trasacc.iniciar_transaccion()
        sql = f"""
            UPDATE usuarios SET passw=PWDENCRYPT('{pw}') WHERE idusuario='{user}'
            """
        cursor.execute(sql)
        gestor_trasacc.confirmar_transaccion()


