# 3. Configure Database
This section will go over connecting our FastAPI application to a PostgreSQL database.
As well as, creating a database migration tool to manage our database schema.

### Table of Contents
1. [Add dependencies](#add-dependencies)
2. [Setup configuration](#setup-configuration)
3. [Setup database config](#setup-database-config)
4. [Create database connection](#create-database-connection)
5. [Create a migration tool](#create-a-migration-tool)
6. [Setup Auto Migrations](#setup-auto-migrations)
7. [Challenge](#challenge)


### Add dependencies
To setup and manage our database we will need to install a few dependencies.
1. [sqlalchemy](https://pypi.org/project/sqlalchemy/)
2. [alembic](https://pypi.org/project/alembic/)
3. [pydantic](https://pypi.org/project/pydantic/)

We will add these to our `requirements.txt` file then run `pip install -r requirements.txt` to install them:
```bash
alembic~=1.13.2
pydantic~=2.8.2
sqlalchemy~=2.0.31
```

`Sqlalchemy` - is a ORM library for python that also handles database connections and transactions. It provides a way to interact with databases in a pythonic way.

`Alembic` - is a lightweight database migration tool for SQLAlchemy. It provides a way to manage database schema changes in a way that is database agnostic. This means that we can use the same migration scripts for different databases like PostgreSQL, MySQL, SQLite, etc.


### Setup configuration
For our server to talk to our database, we need to tell it the locations and credentials.
To do this we will create a `settings.py` file in our `app` directory:

You can see the full settings file at [settings.py](https://github.com/awile/api-club/blob/main/app/settings.py).
Here we will look a few key parts:
1. The settings class which will hold our database configuration
```python
class Settings(BaseModel):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str

    def get_db_connection_string(self, is_async: bool = True):
        format = "postgresql+asyncpg" if is_async else "postgresql"
        return f"{format}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}"
```
We can see that we have variables that tell our server where to find our database.
Also, we have a method that will return a connection string for our database. Note that we can make this connection string async by passing in a boolean. This will be helpful for production and testing, but more on this in future steps.

2. We will create a cache class to hold our settings

FastAPI requests are stateless by default, meaning that each request is independent of the others. This is great for scaling and performance, but we don't want to have to re-read our settings for every request. To solve this we will create a cache class that will hold our settings and only read them once.
```python
@lru_cache
def init_settings() -> Settings:
    variables = {field: os.environ[field] for field in Settings.model_fields.keys()}
    return Settings(**variables)
```
We use the `lru_cache` decorator to cache our settings. This means that the settings will only be read once and then stored in memory for future requests.

3. We will create a function to get our settings

FastAPI has a dependency injection system that allows us to inject dependencies into our routes. We will use this to inject our settings into services and routes that need them. Importantly, we will use this for connecting to our database.
```python
settings_cache = SettingsCache()

def get_settings() -> Settings:
    return settings_cache.get()
```


### Setup database config
Our settings class is ready to go, but we need to setup our environment variables to pass the database connection.
To do this we can use our `.docker-compose.yml` file.
```yaml
services:
  api_server:
    container_name: api_server
    image: api
    ports:
      - "8000:8000"
    environment:
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_HOST: db
      DB_NAME: postgres
    networks:
      - api

  db:
    ...
    networks:
      - api
```

Notice how our `DB_HOST=db` is not set to localhost. This because docker uses container names as hostnames. This means that our server can connect to our database using the hostname `db`. We also added a network to our services to ensure they can communicate with each other through a docker. More info in docker's [user-defined networks](https://docs.docker.com/network/#user-defined-networks).


### Create database connection
Now that we have our settings and environment variables setup, we can create a database connection.
To do this we will create a `db.py` file in our `app` director of which you can see the full file at [db.py](https://github.com/awile/api-club/blob/main/app/db.py):

```python
@lru_cache
def session_factory() -> async_sessionmaker[AsyncSession]:
    settings = get_settings()
    uri = settings.get_db_connection_string()
    engine = create_async_engine(uri, pool_pre_ping=True)
    return async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
    )
```
The main part of our database is initializing a database session factory.
This factory creates database sessions which in sqlalchemy are effectively single database transactions.
Since our fastapi server is asynchronous and handles multiple api requests concurrently, we will create one async session per request.
More on this in the [sqlalchemy documentation](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks).

Note: We use the `lru_cache` decorator to cache the session factory. This is because we only want to create one session factory per server instance and cache.


```python
def get_session(request: Request) -> AsyncSession:
    if not request.state.session:
        session = session_factory()()
        request.state.session = session
    return request.state.session

async def get_db_session(request: Request) -> AsyncSession:
    return get_session(request)
```

Then using fastapi's dependency injection system and request object we will create a function to get a db session for each request.
This gives us an easy way to interact with our database in our routes and services while isolating db transactions for each request.


### Create a migration tool
Alembic provides a way to manage ourt database schema and can automatically detect changes to our database models defined in python code.
To set this up we will have to do the following:

1. Create an alembic configuration file
```bash
alembic init alembic
```
This will create a directory called `alembic` with a `alembic.ini` file and a `versions` directory.

2. Update the `alembic/env.py` file
```python
from app.settings import get_settings

config = context.config # this line exists already
settings = get_settings()
url = settings.get_db_connection_string()
config.set_main_option("sqlalchemy.url", url)
```

Here we are importing our settings and setting the database url so alembic can connect to the database.

3. Setup sqlalchemy db base model in `app/db.py`
```python
from sqlalchemy.orm import declarative_base
Base = declarative_base(
    type_annotation_map={
        dict[str, Any]: JSONB,
    }
)
```
This will allow us to use the `Base` class to define our database models.
Alembic will also use this to detect model changes and create migration scripts.


4. Create a database model
To do this we will create a `models/` directory with two files
- `task.py`
```python
class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(BigInteger, default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
```

- `__init__.py`
```python
from .task import Task
from app.db import Base
```
This will allow us to import all our models for detection by alembic and sql alchemy.

5. import our models in `alembic/env.py`
```python
from app.models import Base
```

Now you can run `alembic upgrade head` to run the latest migration but we don't have settings configured outside of docker.


### Setup Auto Migrations
Now we will setup a way to create migrations and have them auto run when we start our server.
This will be crucial for when we deploy our server to production and need to update our database schema with the latest api code.

1. We need to add alembic to our Dockerfile
```Dockerfile
```



### Challenge
