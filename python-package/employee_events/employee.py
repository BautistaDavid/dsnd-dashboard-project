from .query_base import QueryBase
from .sql_execution import QueryMixin, query

class Employee(QueryBase):

    name = "employee"

    @query
    def names(self):
        return f"""
        SELECT full_name, employee_id FROM employee
        """

    @query
    def username(self, id):
        return f"""
        SELECT full_name FROM employee WHERE employee_id = {id}
        """

    def model_data(self, id):
        sql = f"""
        SELECT SUM(positive_events) as positive_events,
               SUM(negative_events) as negative_events
        FROM employee
        JOIN employee_events USING(employee_id)
        WHERE employee.employee_id = {id}
        """
        return self.pandas_query(sql)
