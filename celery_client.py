import time

from celery import Celery

from settings import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from api.redis_client import redis_model
from executor.docker_service import DockerService


app = Celery('code-executor', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, check_user_available_time)


@app.task
def check_user_available_time():
    for user_id in redis_model.get_user_ids():
        redis_model.set_user_new_available_time(user_id)
        service = DockerService(user_id)
        if not service.is_container_running():
            service.remove_user_container()

