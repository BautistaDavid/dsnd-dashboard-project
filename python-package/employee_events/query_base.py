from .sql_execution import QueryMixin
import pandas as pd

class QueryBase(QueryMixin):

    name = ""

    def names(self):
        return []

    def event_counts(self, id):
        sql = f"""
        SELECT event_date,
               SUM(positive_events) as positive_events,
               SUM(negative_events) as negative_events
        FROM {self.name}
        JOIN employee_events USING ({self.name}_id)
        WHERE {self.name}.{self.name}_id = {id}
        GROUP BY event_date
        ORDER BY event_date
        """
        return self.pandas_query(sql)

    def notes(self, id):
        sql = f"""
        SELECT note_date, note
        FROM notes
        JOIN {self.name} USING ({self.name}_id)
        WHERE {self.name}.{self.name}_id = {id}
        ORDER BY note_date
        """
        return self.pandas_query(sql)
