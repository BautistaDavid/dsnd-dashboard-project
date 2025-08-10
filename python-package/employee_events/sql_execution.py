from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

# Ruta absoluta a la base de datos
db_path = Path(__file__).resolve().parent / "employee_events.db"

# Opción Mixin
class QueryMixin:

    def pandas_query(self, sql_query: str):
        conn = connect(db_path)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df

    def query(self, sql_query: str):
        conn = connect(db_path)
        cursor = conn.cursor()
        result = cursor.execute(sql_query).fetchall()
        conn.close()
        return result

# Decorador (ya dado, no modificar)
def query(func):
    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result
    return run_query
