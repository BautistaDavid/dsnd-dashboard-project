from fasthtml.common import *
import matplotlib.pyplot as plt

# Imports de employee_events
from employee_events import QueryBase, Employee, Team

# Importar load_model
from utils import load_model

# Importar clases base para UI
from base_components import Dropdown, BaseComponent, Radio, MatplotlibViz, DataTable
from combined_components import FormGroup, CombinedComponent

# Dropdown personalizado
class ReportDropdown(Dropdown):
    def build_component(self, entity_id, model):
        self.label = model.name
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        return model.names()

# Header
class Header(BaseComponent):
    def build_component(self, entity_id, model):
        # model.name es 'employee' o 'team', lo usamos para el título
        if model.name == "employee":
            title = "Desempeño del empleado"    
        elif model.name == "team":
            title = "Desempeño del equipo"
        else:
            title = "Desempeño"

        return H1(title)
# LineChart
class LineChart(MatplotlibViz):
    def visualization(self, asset_id, model):
        df = model.event_counts(asset_id)
        df = df.fillna(0)
        df = df.set_index('event_date')
        df = df.sort_index()
        df = df.cumsum()
        df.columns = ['Positive', 'Negative']
        fig, ax = plt.subplots()
        df.plot(ax=ax)
        self.set_axis_styling(ax)
        ax.set_title('Cumulative Events Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        return fig

# BarChart
class BarChart(MatplotlibViz):
    predictor = load_model()

    def visualization(self, asset_id, model):
        data = model.model_data(asset_id)
        proba = self.predictor.predict_proba(data)
        risk = None
        if model.name == 'team':
            risk = proba[:,1].mean()
        else:
            risk = proba[0,1]
        fig, ax = plt.subplots()
        ax.barh([''], [risk])
        ax.set_xlim(0,1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)
       # self.set_axis_styling(ax)
        return fig
class EmployeeEventsBar(MatplotlibViz):
    def visualization(self, asset_id, model):
        conn = sqlite3.connect("employee_events.db")
        df = pd.read_sql_query("SELECT team, COUNT(DISTINCT employee_id) as count FROM employee_events GROUP BY team", conn)
        conn.close()

        fig, ax = plt.subplots()
        ax.bar(df["team"], df["count"])
        ax.set_title("Empleados por equipo")
        ax.set_ylabel("Cantidad")
        ax.set_xticklabels(df["team"], rotation=45, ha="right")
        self.set_axis_styling(ax)
        return fig

class EmployeeEventsLine(MatplotlibViz):
    def visualization(self, asset_id, model):
        conn = sqlite3.connect("employee_events.db")
        df = pd.read_sql_query("SELECT event_date, COUNT(*) as count FROM employee_events GROUP BY event_date", conn)
        conn.close()

        df["event_date"] = pd.to_datetime(df["event_date"])
        df = df.sort_values("event_date")

        fig, ax = plt.subplots()
        ax.plot(df["event_date"], df["count"], marker="o")
        ax.set_title("Eventos por fecha")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Cantidad de eventos")
        self.set_axis_styling(ax)
        return fig

# Visualizaciones combinadas
class Visualizations(CombinedComponent):
    children = [LineChart(), BarChart()]
    outer_div_type = Div(cls='grid')

# Tabla de notas
class NotesTable(DataTable):
    def component_data(self, entity_id, model):
        return model.notes(entity_id)

# Filtros del dashboard
class DashboardFilters(FormGroup):
    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
        ),
        ReportDropdown(
            id="selector",
            name="user-selection"
        )
    ]

# Reporte completo
class Report(CombinedComponent):
    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable()
    ]

# Inicializar app y reporte
app = FastHTML()
report = Report()

@app.get('/')
def index():
    return report(1, Employee())

@app.get('/employee/{id}')
def employee_page(id: str):
    return report(id, Employee())

@app.get('/team/{id}')
def team_page(id: str):
    return report(id, Team())

@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())

@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)

serve()
