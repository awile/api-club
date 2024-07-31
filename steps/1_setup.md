# 1. Setup
This section will go over how we setup this repo to get a basic working api + some basic dev tools.

### Table of Contents
1. [Set python version](#set-python-version)
2. [Create virtual environment](#create-virtual-environment)
3. [Add prod requirements](#add-prod-requirements)
4. [Create basic API](#create-basic-api)
5. [Add dev requirements](#add-dev-requirements)
6. [Create a Makefile](#create-a-makefile)
7. [Add a gitignore](#add-a-gitignore)
8. [Challenge](#challenge)


### Set python version
First we want to establish which python version we are using.
This will let pyenv automatically switch to the correct version when we enter the directory.
```
echo "3.12.2" > .python-version
```

### Create Virtual Environment
First we are going to create a virtualenv to isolate our project dependencies. This will allow us to install packages without affecting the global python installation.
```bash
python -m venv venv
```
Then we need to activate the environment
```bash
source venv/bin/activate
```

### Add Prod Requirements
Next we are going to add the requirements for our project. We are going to use `fastapi` as our web framework
```bash
echo "fastapi~=0.111.1" > requirements.txt
```
Then install the requirements
```bash
pip install -r requirements.txt
```


### Create Basic API
Create a directory for our api and a file for the main entrypoint.
```bash
mkdir app && touch app/main.py
```
Then add the following contents to the file
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def status():
    return {"status": "ok"}
```

Then we can run the server with the following command.
We also get hot reloading (updating the server on file changes) for free.
```bash
fastapi dev app/main.py
```

You can test this at http://localhost:8000/


### Add Dev Requirements
Now that we have a server running let's add some basic dev tools to keep our code clean.
Create a new file for dev requirements and add the following packages.
```bash
echo "black~=24.4.2\nmypy~=1.11.1\nruff~=0.5.5" > requirements-dev.txt
```
We can install these with the following command
```bash
pip install -r requirements-dev.txt
```

### Create a Makefile
Makefiles are a great way to keep your commands organized and easy to run.
Create a new file called `Makefile` and add the following contents.
```makefile
check: format lint typecheck

lint:
	ruff check app

typecheck:
	mypy app

format:
	black app
```

### Add a gitignore
Create a new file called `.gitignore` and add the following contents.
This will keep your git repo clean and ignore any files that are not needed.
```gitignore
.DS_Store
__pycache__
venv
```


##### Extras
If you want to see all packages installed in your environment you can run the following command.
This contains the packages in requirements.txt and requirements-dev.txt plus any dependencies that the installed packages have.
```bash
ls venv/lib/python3.12/site-packages
```


### Challenge
1. Add a new endpoint that returns some data
2. Run the make check command and fix any issues with the new endpoint
