import random
from nicegui import app, ui
from pydantic import BaseModel
from typing import Dict
from fastapi import Depends
from dataclasses import dataclass
import drag_and_drop as dnd
from collections import defaultdict, Counter
import seaborn as sns

class Task(BaseModel):
    name: str
    description: str | None = None
    status: str

class ChangeTask(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None

########################
### Helper Functions ###
########################

# helper functions for the table/grid view
def handle_cell_value_change(e, aggrid):
    repo = get_app_repo()

    new_row = e.args['data']
    ui.notify(f'Updated row to: {e.args["data"]}')
    print(e.args["data"])
    
    change = ChangeTask(**e.args["data"])
    repo.update(e.args["data"]['id'], change)
    
    aggrid.options['rowData'][:] = [
        row | new_row if row['id'] == new_row['id'] else row
        for row in aggrid.options['rowData']
    ]


def add_row():
    repo = get_app_repo()
    repo.add_blank_task()
    ui.notify(f'New task added!')


async def delete_selected(aggrid: ui.aggrid) -> None:
    repo: ToDoRepo = get_app_repo()

    selected = await aggrid.get_selected_rows()
    if not selected:
        ui.notify("No rows selected", type="warning")
        return

    ids_to_delete = [row["id"] for row in selected]

    for rid in ids_to_delete:          
        repo.delete(rid)

    ui.notify(f"Deleted {len(ids_to_delete)} task(s)")
####################

# Kanban view helper functions
@dataclass
class ToDo:
    name: str
    description: str
    id: int


def handle_drop(todo: ToDo, location: str):
    repo = get_app_repo()
    ui.notify(f'"{todo.name}" is now in {location}')
    change = ChangeTask(status=location)
    repo.update(todo.id, change)


def group_by_status(data: dict[int, dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for _id, task in data.items():         
        task_with_id = task | {"id": _id}   
        grouped[task["status"]].append(task_with_id)
    return dict(grouped)

############################
### UI Builder Functions ###
############################

@ui.refreshable
def to_do_table():
    repo = get_app_repo()
    rows = [dict(id=k, **v) for k, v in repo.get_all().items()]
    aggrid = ui.aggrid({
        'columnDefs': [
            {'headerName': 'ID',   'field': 'id', 'editable': False},
            {'headerName': 'Name', 'field': 'name', 'editable': True},
            {'headerName': 'Description', 'field': 'description', 'editable': True},
            {'headerName': 'Status', 'field': 'status', 'editable': True},
        ],
        'rowData': rows,
        'defaultColDef': {
            'sortable': True,
            'filter': True,
            'resizable': True,
            'editable': True,  
        },
        'rowSelection': {'mode': 'multiRow'},
        'stopEditingWhenCellsLoseFocus': True,
    }).style('height:75vh')

    aggrid.on('cellValueChanged', lambda e: handle_cell_value_change(e, aggrid))
    return aggrid

@ui.refreshable
def kanban() -> None:
    repo = get_app_repo()
    # print(repo.get_all())
    repo = group_by_status(repo.get_all())
    # print(repo)
    with ui.row():
        for column in repo:
            # print(column)
            with dnd.column(column, on_drop=handle_drop):
                for item in repo[column]:
                    # print(item)
                    dnd.card(ToDo(name=item['name'], description=item['description'], id=item['id']))

@ui.refreshable
def statistics() -> None:
    repo = get_app_repo()
    tasks = repo.get_all()
    status_counts = Counter(task["status"] for task in tasks.values())

    with ui.tab_panel('Statistics'):
        ui.label('Content of Statistics')

        with ui.matplotlib(figsize=(6, 4)).figure as fig:
            ax = fig.gca()
            sns.barplot(
                x=list(status_counts.keys()),
                y=list(status_counts.values()),
                hue=list(status_counts.keys()),   
                palette='viridis',
                legend=False,                     
                ax=ax
            )
            ax.set_title('Task Count by Status')
            ax.set_xlabel('Status')
            ax.set_ylabel('Number of Tasks')


#################
### ToDo Repo ###
#################

# Class for dependancy injection. Stops global usage and is setup for potential future async/thread safety
# All the state for the webapp lives inside an instance of this class.
# This class also provides a stable API for the frontend. We can change whatever we like in here (i.e. migrate to a DB)
# without breaking/needing to change the frontend. We just need to provide the same data in the same format for the frontend.
class ToDoRepo:
    def __init__(self, table_refresh, kanban_refresh, statistics_refresh) -> None:
        self._id = 0
        self._todo: Dict[int, dict] = {}
        self._updatable_fields: list[str] = ['name', 'description', 'status']
        self._table_refresh = table_refresh
        self._kanban_refresh = kanban_refresh
        self._statistics_refresh = statistics_refresh

    def get_all(self):
        return self._todo

    def add(self, task: Task) -> bool:
        self._todo[self._id] = task.model_dump()
        self._id += 1
        self._table_refresh()
        self._kanban_refresh()
        self._statistics_refresh()
        return True

    def update(self, id: int, changes: ChangeTask) -> bool:
        print('Before change:')
        print(self._todo[id])
        if id in self._todo:
            for field in self._updatable_fields:
                if field in changes.model_fields_set:
                    self._todo[id][field] = getattr(changes, field)
            
            self._table_refresh()
            self._kanban_refresh()
            self._statistics_refresh()

            print('After change:')
            print(self._todo[id])
            return True
        else:
            return False
        
    def add_blank_task(self) -> None:
        self.add(Task(name='new task', description='new description', status='unknown'))

    def delete(self, id: int) -> bool:
        result = self._todo.pop(id, None) is not None
        self._table_refresh()
        self._kanban_refresh()
        self._statistics_refresh()
        return result

to_do_repo = ToDoRepo(to_do_table.refresh, kanban.refresh, statistics.refresh)


# Seed webapp with sample data
t1 = Task(name='milk the soy beans', description='milk the soy beans in shed one', status='pending')
t2 = Task(name='Farm alfalfa', description='collect alfalfa from field 2', status='pending')
t3 = Task(name='Organise the Marionettes', description='puppets need to be sorted in ascending order', status='pending')
t4 = Task(name='Arrange the bees', description='watch for the queen, she barks', status='continuing')
t5 = Task(name='Filter the walnuts', description='walnuts must weigh under 5kg each', status='continuing')
t6 = Task(name='Host hotdog eating competition', description='be wary of the talented Japanese contestent', status='finished')

@app.on_startup   
def init():
    to_do_repo.add(t1)
    to_do_repo.add(t2)
    to_do_repo.add(t3)
    to_do_repo.add(t4)
    to_do_repo.add(t5)
    to_do_repo.add(t6)
    print(to_do_repo.get_all())

def get_app_repo() -> ToDoRepo:
    return to_do_repo 


#######################
### FastAPI Backend ###
#######################

# FastAPI backend is kept very simple. Essentially just a wrapper around the ToDoRepo.
@app.get('/tasks')
def get_tasks(repo: ToDoRepo = Depends(get_app_repo)):
    return repo.get_all()

@app.post('/task')
def add_task(task: Task, repo: ToDoRepo = Depends(get_app_repo)):
    return repo.add(task)

@app.put('/task/{id}')
def update_task(id: int, change: ChangeTask, repo: ToDoRepo = Depends(get_app_repo)):
    return repo.update(id, change)

@app.delete('/task/{id}')
def delete_task(id: int, repo: ToDoRepo = Depends(get_app_repo)):
    return repo.delete(id)


########################
### NiceGUI Frontend ###
########################

@ui.page('/')
def page():

    # --- Header ---
    with ui.header().classes(replace='row items-center') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')

    # --- Left Menu ---
    with ui.left_drawer().classes('bg-blue-100') as left_drawer:
        # ui.label('Side menu')
        with ui.column():
            with ui.tabs().props('vertical') as tabs:
                ui.tab('Grid View', icon='grid_view').props('left')
                ui.tab('Kanban View', icon='view_kanban')
                ui.tab('Statistics', icon='insights')

    
    with ui.tab_panels(tabs, value='Grid View').classes('w-full'):
        
        # --- Table ---
        with ui.tab_panel('Grid View'):
            aggrid = to_do_table()
            ui.button('Delete selected', on_click=lambda: delete_selected(aggrid))
            ui.button('New row', on_click=add_row)
        
        # --- Kanban ---
        with ui.tab_panel('Kanban View'):
            kanban()

        # --- Statistics ---
        with ui.tab_panel('Statistics'):
            statistics()         

ui.run(port=8000, show=False)