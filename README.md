# `fds-be`: Async Web Backend for RDOGS-Friendz

A `python=3.9`-`asyncio`-based web backend, using web framework `fastapi`.

## Note
* We have deployed our backend website on https://be.rdogs.dodofk.xyz/docs. No need to start the server on your local environment.
* API 討論文件: https://hackmd.io/@icheft/S1guJIOBY
* Please ask develop team to get .env file. 

## Setup database
There two ways to setup your database.
### 1. Connect to our database 
* You only have to ask developer to get .env file.
### 2. Build your own database on localhost
First, import schemas.sql to postgresql server
Second, on your postgresql cmd
```
# please remember to replace your path
\COPY location(name) FROM '/path/fds-be/data_collection/location.csv' DELIMITER ',' CSV HEADER;
\COPY category(name) FROM '/path/fds-be/data_collection/category.csv' DELIMITER ',' CSV HEADER;
\COPY department(school, department_name) FROM '/path/fds-be/data_collection/department.csv' DELIMITER ',' CSV HEADER;
```
Finally, revise .env file to connect to your local database.

## Setup test server

### 0. `python` virtual environment
(name whatever you like)
```shell
conda create --name fds-async python=3.9
conda activate fds-async
```
or
```
python3 -m venv fds-async
./fds-async/Scripts/activate
```

or create a virtual environment using `pipenv` (faster and lighter)

```shell
pip install pipenv
pipenv shell
```

### 1. Environment
```shell
pip install -r requirements.txt
copy .env.example .env
```

Or on Unix-based system, run

```shell
pip install -r requirements.txt
cp .env.example .env
```

Then fill out the environment variables in `.env`
### 2. Start the server

```shell
pip install uvicorn
uvicorn main:app
```

On your terminal you should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process xxxx using watchgod
INFO:     Started server process xxxx
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```
Now you can go to `http://127.0.0.1:8000` and test it.  
You may also turn up the auto-reload option, or change the host & port with `--host` and `--port`:
```shell
uvicorn main:app --reload --host 0.0.0.0 --port 80
```
