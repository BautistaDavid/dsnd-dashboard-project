from .query_base import QueryBase
from .sql_execution import QueryMixin, query

class Team(QueryBase):

    name = "team"

    @query
    def names(self):
        return f"""
        SELECT team_name, team_id FROM team
        """

    @query
    def username(self, id):
        return f"""
        SELECT team_name FROM team WHERE team_id = {id}
        """

    def model_data(self, id):
        sql = f"""
        SELECT positive_events, negative_events FROM (
            SELECT employee_id,
                   SUM(positive_events) positive_events,
                   SUM(negative_events) negative_events
            FROM team
            JOIN employee_events USING(team_id)
            WHERE team.team_id = {id}
            GROUP BY employee_id
        )
        """
        return self.pandas_query(sql)
