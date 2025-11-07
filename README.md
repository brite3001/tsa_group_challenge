# TSA Group Challenge
## Setup Instructions
install uv
uv run python main.py

## Technologies
I've selected this stack for the following reasons:
 - I'm familiar with Python, along with FastAPI and uv.
 - NiceGUI is perfect for rapid prototyping of UIs while being closely tied to underlying Python code.
 - peewee ORM looked nice and I wanted to try it.

**Backend** - Python + FastAPI
**Frontend** - [NiceGUI](https://nicegui.io/) (Vue + Quasar)
**Database** - SQLite with [peewee ORM](https://github.com/coleifer/peewee)
**Project Manager** - [uv](https://github.com/astral-sh/uv)

## How It Works
xxx

## Jobs
### Backend
| Endpoint | Description | Status
|--|--|--|
| GET /tasks | Return list of tasks | ❌ 
| POST /tasks | Add new task | ❌ |
| PUT /tasks/:id | Update task details | ❌ |
| DELETE /tasks/:id | Delete a task | ❌ |

### Frontend
| Task | Description | Status
|--|--|--|
| Task list | In table, show name/description/status/id | ❌ 
| Stats Page | tasks completed/tasks with X status | ❌ |

### Optional
| Task | Description | Status |
|--|--|--|
| Docker | ?? | ❌ |
| View Implementation | Implement list + kanban | ❌ |
| Input Validation | Add basic input validation | ❌ |
| Task Filters | Add filters for tasks | ❌ |
| Database Integration | Integration with any database you prefer | ❌ |

## Future Improvement
- Error handling not using proper FastAPI HTTP errors. NiceGUI was intercepting errors raised by FastAPI, not enough time to troubleshoot.
- No auth for the API