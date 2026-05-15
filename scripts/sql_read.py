from pandas import DataFrame
from pandas import read_sql_query
from sqlalchemy import text


def get_read_sql(sql, conexion) -> DataFrame:
    try:
        engine = conexion.conn_engine()
        df = read_sql_query(text(sql), engine)
    except Exception as e:
        print("Ocurrió un error al consultar: ", e)
        return DataFrame()
    return df
