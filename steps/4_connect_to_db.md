# 4. Connect to Database
This section will go over connecting our FastAPI application to a SQLite database.
As well as, creating a database migration tool to manage our database schema.

### Table of Contents
1. [Add dependencies](#add-dependencies)
2. [Setup configuration](#setup-configuration)
3. [Setup database config](#setup-database-config)
4. [Create database connection](#create-database-connection)
5. [Test database connection](#test-database-connection)
7. [Challenge](#challenge)


### Add dependencies
To setup and manage our database we will need to install a few dependencies.
1. [sqlalchemy](https://pypi.org/project/sqlalchemy/)
3. [pydantic](https://pypi.org/project/pydantic/)

We will add these to our `requirements.txt` file then run `pip install -r requirements.txt` to install them:
```bash
sqlalchemy~=2.0.31
aiosqlite~=0.20.0
```

`Sqlalchemy` - is a ORM library for python that also handles database connections, transactions, and more. It provides a way to interact with databases in a pythonic way.


### Setup configuration
SQLite is an database engine that is encapusalted in a file.
For our server to talk to our database, we need to tell it the location of the database file.
To do this we will create a `settings.py` file in our `app` directory:

You can see the full settings file at [settings.py](https://github.com/awile/api-club/blob/main/app/settings.py).
Here we will look a few key parts:
1. The settings class which will hold our database configuration
```python
class Settings(BaseModel):
    DB_FILE_PATH: str

    def get_db_connection_string(self, is_async: bool = True):
        format = "sqlite+aiosqlite" if is_async else "sqlite"
        return f"{format}://{self.DB_FILE_PATH}"
```
We can see that we have a variable to tell our server where to find our database.
Also, we have a method that will return a connection string for our database. Note that we can make this connection string async by passing in a boolean. This will be helpful for production and testing, but more on this in future steps.

2. We will create a cached function to hold our settings

FastAPI requests are stateless by default, meaning that each request is independent of the others. This is great for scaling and performance, but we don't want to have to re-read our settings for every request. To solve this we will create a cache class that will hold our settings and only read them once.
```python
@lru_cache
def init_settings() -> Settings:
    variables = {field: os.environ[field] for field in Settings.model_fields.keys()}
    return Settings(**variables)
```
We use the `lru_cache` decorator to cache our settings. This means that the settings will only be read once and then stored in memory for future requests.

3. We will create a function to get our settings

FastAPI has a dependency injection system that allows us to inject dependencies into our routes. We will use this to inject our settings into services and routes that need them. Importantly, we will use this for connecting to our database. Below we create our `get_settings` function that will return our settings dependency.
```python
def get_settings() -> Settings:
    return init_settings()
```


### Setup database config
Our settings class is ready to go, but we need to setup our environment variables to pass the database connection.
To do this we can use our `.docker-compose.yml` file.
```yaml
services:
  api_server:
    container_name: api_server
    image: api
    ...
    environment:
      DB_FILE_PATH: /data/api.db
    ...
```

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
This factory creates database sessions which in sqlalchemy are wrap all activity in a database transaction and allows us to perform updates in batches and isolation. A good primer on this can be found in the [fivetran db transactions](https://www.fivetran.com/blog/databases-demystified-transactions-part-1).
Since our fastapi server is asynchronous and handles multiple api requests concurrently, we will create one async session per request. To do that we will use a session maker that cretes a configured session which in turn takes a engine that handles settings for interacting with out database.
More on this in the [sqlalchemy documentation](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks).

Note: We use the `lru_cache` decorator to cache the session factory. This is because we only want to create one session factory per server instance and cache.


```python
def get_session(request: Request) -> AsyncSession:
    if not hasattr(request.state, 'session') or request.state.session is None:
        session = session_factory()()
        request.state.session = session
    return request.state.session

async def get_db_session(request: Request) -> AsyncSession:
    return get_session(request)
```

Then using fastapi's dependency injection system and request object we will create a function to get a db session for each request.
This gives us an easy way to interact with our database in our routes and services while isolating db transactions for each request.


### Test database connection
Now that we have our database connection setup we can test it by creating a route that connects to our database and returns a response.
```python
from sqlalchemy import text

@app.get("/db-check")
async def test_db(session = Depends(get_db_session)):
    resp = await session.execute(text('SELECT 1'))
    return {"results": [row[0] for row in resp.all()]}
```

Here we are getting a database session using our get_db_session and fastapi dependency injection system.
Then we are executing a raw sql query that returns the number 1.
Finally, we are returning the results of the query as a json response.


### Challenge
1. Try breaking the connection by changing the database settings in the docker-compose file and see what happens when you run the `/db-check` route.
2. Why are we adding the session to the request? Hint: How many times is the function  `get_session` called in a request?


### Extra
To avoid linting errors we can ignore unused imports in our `__init__.py` file:
Create a `ruff.toml` file and add the following:
```toml
[lint.extend-per-file-ignores]
# Skip unused variable rules (`F841`).
"__init__.py" = ["F841"]
```
