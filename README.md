# TfSpanner 
TfSpanner is a simple api service wriiten in Python and FastAPI for managing Terraform resources and states for new users and developers.   

## Requirements
 TfSpanner needs following components.
 
 * Postgresql Server
 * Redis Server
 * Python >= 3.8
 * Celery
 * FastApi

## Development
If you want to develop a feature, or contribute code in some way, you need a development setup. 

* Start Postgresql Server
```bash
docker run --rm \
--name pg-docker \
-e POSTGRES_PASSWORD=test -d \
-p 5432:5432 -v $(pwd)/data/:/var/lib/ \
 postgresql/data postgres
```

* Start  Redis
```bash
docker run --rm \
--name redis-server -d \
-p 6379:6379 redis
```

* Clone the repo
```bash
git clone https://github.com/Prajithp/terraspanner.git
cd terraspanner
```

* Install python dependecies using virtualenv
```bash
virtualenv --python=python3.8 venv
source venv/bin/activate
pip install -r requirements.txt
```

* Start Celery worker.
```bash
python worker.py
```

* Start Web App.
```bash
venv/bin/uvicorn main:app --reload
# open http://127.0.0.1:8000/docs to get the openapi
```

## Todo
* Web Interface using vuejs 
