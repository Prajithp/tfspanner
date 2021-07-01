from config.celery import celery_app

if __name__ == "__main__":
    celery_app.worker_main(
        argv=[
            "worker",
            "-E",
            "--loglevel=info",
            "--concurrency=4",
            "--pool=eventlet",
        ]
    )
