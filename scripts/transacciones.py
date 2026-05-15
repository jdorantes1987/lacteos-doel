class GestorTransacciones:
    def __init__(self, conexion):
        self.conexion = conexion

    def iniciar_transaccion(self):
        autocommit_fn = getattr(self.conexion, "autocommit", None)
        if callable(autocommit_fn):
            autocommit_fn(False)

    def confirmar_transaccion(self):
        commit_fn = getattr(self.conexion, "commit", None)
        if callable(commit_fn):
            commit_fn()

    def revertir_transaccion(self):
        rollback_fn = getattr(self.conexion, "rollback", None)
        if callable(rollback_fn):
            rollback_fn()

    def get_cursor(self):
        cursor = None
        try:
            get_cursor_fn = getattr(self.conexion, "get_cursor", None)
            if callable(get_cursor_fn):
                cursor = get_cursor_fn()
        except Exception as e:
            print("Error al crear cursor: ", e)
        return cursor
