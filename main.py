import random
from nicegui import app, ui
from pydantic import BaseModel
from typing import Dict
from fastapi import Depends

class Task(BaseModel):
    name: str
    description: str | None = None
    status: str

class ChangeTask(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None

# class for dependancy injection. Stops global usage and is setup for async/thread safety
class ToDoRepo:
    def __init__(self) -> None:
        self._id = 0
        self._todo: Dict[int, dict] = {}
        self._updatable_fields: list[str] = ['name', 'description', 'status']

    def get_all(self):
        return self._todo

    def add(self, task: Task) -> bool:
        self._todo[self._id] = task.model_dump()
        self._id += 1
        return True


    def update(self, id: int, changes) -> bool:
        if id in self._todo:
            for field in self._updatable_fields:
                if field in changes.model_fields_set:
                    self._todo[id][field] = getattr(changes, field)
            return True
        else:
            return False

    def delete(self, id: int) -> bool:
        return self._todo.pop(id, None) is not None

to_do_repo = ToDoRepo()

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


@app.get('/random/{max}')
def generate_random_number(max: int):
    return {'min': 0, 'max': max, 'value': random.randint(0, max)}

@ui.page('/')
def page():
    max = ui.number('max', value=100)
    ui.button('generate random number',
              on_click=lambda: ui.navigate.to(f'/random/{max.value:.0f}'))

ui.run(port=8000)