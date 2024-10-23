class GestorTransacciones:
    def __init__(self, conexion):
        self.conexion = conexion
        self.conexion.conectar()
        
    def iniciar_transaccion(self):
        self.conexion.iniciar_transaccion()

    def confirmar_transaccion(self):
        self.conexion.confirmar_transaccion()

    def revertir_transaccion(self):
        self.conexion.revertir_transaccion()
        
    def get_cursor(self):
        try:
            cursor = self.conexion.conn.cursor()
        except Exception as e:
            print("Error al crear cursor: ", e)
        return cursor