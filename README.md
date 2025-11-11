# TSA Group Challenge
## Setup Instructions
### Python uv
[install uv](https://docs.astral.sh/uv/getting-started/installation/)

`uv run python main.py`

`http://localhost:8000`

### Docker
`docker build -t tsa .`

`docker run -p 8000:8000 tsa`

`http://localhost:8000`

## Technologies
**Backend** - Python + FastAPI

**Frontend** - [NiceGUI](https://nicegui.io/) (Vue + Quasar)

**Database** - SQLite with [peewee ORM](https://github.com/coleifer/peewee)

**Project Manager** - [uv](https://github.com/astral-sh/uv)

I've selected this stack for the following reasons:
 - I'm familiar with Python, along with FastAPI and uv.
 - NiceGUI looks like a good fit for rapid prototyping of UIs, while being closely tied to underlying Python code.
 - peewee ORM looked nice and I wanted to try it.

## How It Works
This todo webapp is built as a monolith, mostly within the main.py file. 
Data can be added to the app via the REST API or by interacting with the table on the main page.
The state of the table/kanban/stats page is updated live using NiceGUI's @refreshable decorator, which is triggered using
`to_do_table.refresh, kanban.refresh, statistics.refresh` in the ToDoRepo class.

The code for the table/grid component uses AGGrid, which has filtering provided out of the box.
To get edit/add/delete working for this table, I connected the table to the ToDoRepo with handle_cell_value_change(), add_row(), delete_selected() helpers.

I grabbed most of the kanban code from [this](https://github.com/zauberzeug/nicegui/blob/main/examples/trello_cards/main.py) example, no point reinventing the wheel.
To connected the kanban view to ToDoRepo via the helper function handle_drop(), which updates the status when the card is moved around. Helper group_by_status() reorganises the dict so items are grouped by status, makes kanban easier to build.

## CURL commands for interacting with the backend
### Add Task
`curl -X POST http://localhost:8000/task   -H "Content-Type: application/json"   -d '{"name":"Buy milk","description":"Low-fat","status":"todo"}'`

### Delete Task
`curl -X DELETE http://localhost:8000/task/2`

### Update Task
`curl -X PUT http://localhost:8000/task/0   -H "Content-Type: application/json"   -d '{"name":"eee","description":"eee","status":"eee"}'`

### Get Tasks
`curl localhost:8000/tasks`


## Jobs
### Backend
| Endpoint | Description | Status
|--|--|--|
| GET /tasks | Return list of tasks | ✅ 
| POST /tasks | Add new task | ✅ |
| PUT /tasks/:id | Update task details | ✅ |
| DELETE /tasks/:id | Delete a task | ✅ |

### Frontend
| Task | Description | Status
|--|--|--|
| Task list | In table, show name/description/status/id | ✅ 
| Stats Page | tasks completed/tasks with X status | ✅ |

### Optional
| Task | Description | Status |
|--|--|--|
| Docker | add | ✅ |
| View Implementation | Implement list + kanban | ✅ |
| Input Validation | Add basic input validation | ✅ |
| Task Filters | Add filters for tasks | ✅ |
| Database Integration | Integration with any database you prefer | ❌ |

## Future Improvement
- Error handling not using proper FastAPI HTTP errors (just True/False). NiceGUI was intercepting errors raised by FastAPI, not enough time/experience to troubleshoot.
- No auth for the API
- Charts on stats page don't automatically resize, just simple seaborn tables.
- The delete button will only work once. To click it again, the page needs to be refreshed.
- The table changes its size when swapping between tabs, and when items are added/removed sometimes.
- Multiple users are not supported with the way state management is done.
- Needs proper backend/frontend test suite. Only adhoc testing done.
- No logging.