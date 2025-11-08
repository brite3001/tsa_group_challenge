import random
from nicegui import app, ui
from pydantic import BaseModel
from typing import Dict
from fastapi import Depends
from dataclasses import dataclass
import drag_and_drop as dnd
from collections import defaultdict

class Task(BaseModel):
    name: str
    description: str | None = None
    status: str

class ChangeTask(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


### AG-TABLE ###
def add_row():
    new_id = max((dx['id'] for dx in aggrid.options['rowData']), default=-1) + 1
    aggrid.options['rowData'].append({'id': new_id, 'name': 'New name', 'age': None})
    ui.notify(f'Added row with ID {new_id}')


def handle_cell_value_change(e):
    new_row = e.args['data']
    ui.notify(f'Updated row to: {e.args["data"]}')
    aggrid.options['rowData'][:] = [row | new_row if row['id'] ==
                                    new_row['id'] else row for row in aggrid.options['rowData']]


async def delete_selected():
    selected_id = [row['id'] for row in await aggrid.get_selected_rows()]
    aggrid.options['rowData'][:] = [row for row in aggrid.options['rowData'] if row['id'] not in selected_id]
    ui.notify(f'Deleted row with ID {selected_id}')
#####################

@ui.refreshable
def to_do_table() -> None:
    repo = get_app_repo()
    rows = [dict(id=k, **v) for k, v in repo.get_all().items()]
    ui.aggrid({
        'columnDefs': [
            {'headerName': 'ID', 'field': 'id', 'maxWidth': 70},
            {'headerName': 'Name', 'field': 'name'},
            {'headerName': 'Description', 'field': 'description'},
            {'headerName': 'Status', 'field': 'status'},
        ],
        'rowData': rows,
        'defaultColDef': {'sortable': True, 'filter': True, 'resizable': True},
    }).style('height:75vh')

### KANBAN ###
@dataclass
class ToDo:
    name: str
    description: str


def handle_drop(todo: ToDo, location: str):
    ui.notify(f'"{todo.name}" is now in {location}')


def group_by_status(data: dict[int, dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for task in data.values():
        grouped[task['status']].append(task)
    return dict(grouped)
##################

@ui.refreshable
def kanban() -> None:
    repo = get_app_repo()
    repo = group_by_status(repo.get_all())
    with ui.row():
        for column in repo:
            print(column)
            with dnd.column(column, on_drop=handle_drop):
                for item in repo[column]:
                    print(item)
                    dnd.card(ToDo(name=item['name'], description=item['description']))

    # with ui.row():
    #     with dnd.column('Next', on_drop=handle_drop):
    #         dnd.card(ToDo('Simplify Layouting'))
    #         dnd.card(ToDo('Provide Deployment'))
    #     with dnd.column('Doing', on_drop=handle_drop):
    #         dnd.card(ToDo('Improve Documentation'))
    #     with dnd.column('Done', on_drop=handle_drop):
    #         dnd.card(ToDo('Invent NiceGUI'))
    #         dnd.card(ToDo('Test in own Projects'))
    #         dnd.card(ToDo('Publish as Open Source'))
    #         dnd.card(ToDo('Release Native-Mode'))

# class for dependancy injection. Stops global usage and is setup for async/thread safety
class ToDoRepo:
    def __init__(self, table_refresh, kanban_refresh) -> None:
        self._id = 0
        self._todo: Dict[int, dict] = {}
        self._updatable_fields: list[str] = ['name', 'description', 'status']
        self._table_refresh = table_refresh
        self._kanban_refresh = kanban_refresh

    def get_all(self):
        return self._todo

    def add(self, task: Task) -> bool:
        self._todo[self._id] = task.model_dump()
        self._id += 1
        self._table_refresh()
        self._kanban_refresh()
        return True


    def update(self, id: int, changes) -> bool:
        if id in self._todo:
            for field in self._updatable_fields:
                if field in changes.model_fields_set:
                    self._todo[id][field] = getattr(changes, field)
            
            self._table_refresh()
            self._kanban_refresh()
            return True
        else:
            return False

    def delete(self, id: int) -> bool:
        result = self._todo.pop(id, None) is not None
        self._table_refresh()
        self._kanban_refresh
        return result

to_do_repo = ToDoRepo(to_do_table.refresh, kanban.refresh)

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
    # print(to_do_repo.get_all())

def get_app_repo() -> ToDoRepo:
    return to_do_repo 

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






@ui.page('/')
def page():


    
    with ui.header().classes(replace='row items-center') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')


    with ui.footer(value=False) as footer:
        ui.label('Footer')

    with ui.left_drawer().classes('bg-blue-100') as left_drawer:
        # ui.label('Side menu')
        with ui.column():
            with ui.tabs().props('vertical') as tabs:
                ui.tab('Grid View', icon='grid_view').props('left')
                ui.tab('Kanban View', icon='view_kanban')
                ui.tab('Statistics', icon='insights')

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

    with ui.tab_panels(tabs, value='Grid View').classes('w-full'):
        # --- TODO TABLE ---
        with ui.tab_panel('Grid View'):
            to_do_table()
            ui.button('Delete selected', on_click=delete_selected)
            ui.button('New row', on_click=add_row)
        with ui.tab_panel('Kanban View'):
            ui.label('Content of Kanban View')
            # --- KANBAN ---
            kanban()

        with ui.tab_panel('Statistics'):
            ###  --- STATISTICS ---
            ui.label('Content of Statistics')
            # sample data
            labels = ['A', 'B', 'C', 'D']
            sizes  = [15, 30, 45, 10]

            with ui.matplotlib(figsize=(5, 6)).figure as fig:
                ax = fig.gca()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')          
            
            with ui.matplotlib(figsize=(5, 6)).figure as fig:
                ax = fig.gca()
                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')          

ui.run(port=8000, show=False)