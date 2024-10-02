# 6. Add CRUD endpoints


### Table of Contents
1. [Create a router](#create-a-router)
2. [Create a list endpoint](#create-a-list-endpoint)
3. [Create a create endpoint](#create-a-create-endpoint)
4. [Create a read endpoint](#create-a-read-endpoint)
5. [Create an update endpoint](#create-an-update-endpoint)
6. [Create a delete endpoint](#create-a-delete-endpoint)
7. [Challenge](#challenge)


### Create a router
We want to create basic CRUD functionality or:
- Create
- Read
- Update
- Delete

This will allow us to interact with our database models through HTTP requests.
To do this we will define all our endpoints in a routers file and then add the routes to our application.

First in the app directory create a new directory `routers/` and file `app/routers/task_router.py`:
```python
from fastapi import APIRouter

task_router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={404: {"description": "Not found"}},
)

@task_router.get("/")
  async def list_tasks():
    return {"tasks": []}
```

Then in the `app/main.py` file import the router and add it to the application:
```python
...
from app.routers.task_router import task_router

app = FastAPI()

app.include_router(task_router)
```


### Create a list endpoint
We will start by creating a list endpoint that will return all tasks in our database.

First we need to access our database connection in the router.
We can do this by using the `Depends` function from FastAPI combined with the Annotated type.
Add the following to the `/app/routers/task_router.py` file:
```python
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

DBSession = Annotated[AsyncSession, Depends(get_db_session)]

@task_router.get("/")
async def list_tasks(session: DBSession):
  return {"tasks": []}
```

Here we are using FastAPI's dependency injection system to get a database session for each request.
Now, that we have a session let's add two query params for pagination and return a list of tasks:
```python
...
from sqlalchemy.sql.expression import select
...

@task_router.get("/")
async def list_tasks(session: DBSession, page: int = 1, page_size: int = 10):
    results = await session.execute(select(Task).limit(page_size).offset((page - 1) * page_size))
    tasks = [
        {
            "id": task.id,
            "name": task.name,
            "created_at": task.created_at
        }
        for task in results.scalars().all()
    ]
    return {"tasks": tasks}
```

Now we can call this endpoint and see a list of tasks in our database.

### Create a create endpoint
Next we will create a create endpoint that will allow us to add tasks to our database.
```python
...
from pydantic import BaseModel
...

class TaskCreateDTO(BaseModel):
    name: str

@task_router.post("/")
async def create_task(task_create: TaskCreateDTO):
    return {"name": task_create.name}
```

First we define a Pydantic model that will be used to validate and parse the request body.
This is call TaskCreateDTO where DTO stands for Data Transfer Object and acts as a contract for interacting with the api.
Now we can add the sqlalchemy query to insert the data.
```python
@task_router.post("/")
async def create_task(task_create: TaskCreateDTO, session: DBSession):
    task = Task(**task_create.dict())
    session.add(task)
    await session.commit()
    return {"id": task.id, "name": task.name, "created_at": task.created_at}
```

Now we can call this endpoint with a JSON body and see a new task in our database.

### Create a read endpoint
Next we will create a read endpoint that will allow us to get a single task by its id.
```python
@task_router.get("/{task_id}")
async def get_task(task_id: int, session: DBSession):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task.id, "name": task.name, "created_at": task.created_at}
```

This will return a single task by its id or a 404 if the task does not exist.

### Create an update endpoint
Next we will create an update endpoint that will allow us to update a task by its id.
```python
class TaskUpdateDTO(BaseModel):
    name: str

@task_router.put("/{task_id}")
async def update_task(task_id: int, task_update: TaskUpdateDTO, session: DBSession):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.name = task_update.name
    await session.commit()
    return {"id": task.id, "name": task.name, "created_at": task.created_at}
```

This will update a single task by its id or a 404 if the task does not exist.


### Create a delete endpoint
Finally we will create a delete endpoint that will allow us to delete a task by its id.
```python
@task_router.delete("/{task_id}")
async def delete_task(task_id: int, session: DBSession):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    await session.commit()
    return {"id": task.id, "name": task.name, "created_at": task.created_at}
```

This will delete a single task by its id or a 404 if the task does not exist.

### Challenge
1. Try add a parameter to get tasks by name in the list endpoint.
2. Add a total count of tasks to the list endpoint.
