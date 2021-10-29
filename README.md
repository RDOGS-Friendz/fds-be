# `fds-be`: Async Web Backend for RDOGS-Friendz

A `python=3.9`-`asyncio`-based web backend, using web framework `fastapi`.

## Setup test server

### 0. `python` virtual environment
(name whatever you like)
```shell
conda create --name fds-async python=3.9
conda activate fds-async
```

### 1. Environment
```shell
pip install -r requirements.txt
copy .env.example .env
copy logging.yaml.example logging.yaml
```

Then 
1. fill out the environment variables in `.env`
2. Manually create your log folder (default `/log` under your cloned `fds-be` project folder).

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