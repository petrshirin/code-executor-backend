import time

import docker
from docker.models.containers import Container
from settings import DEFAULT_IMAGE, DOCKER_HOST
from docker.errors import DockerException
import logging
from api.redis_client import redis_model

logger = logging.getLogger(__name__)


class ServiceException(Exception):

    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class DockerService:
    """
    Сервис для управления контейнером пользователя
    """
    IMAGE = DEFAULT_IMAGE
    COMMAND = './entrypoint.sh'
    ERRORS = {
        'read_error': 'Ошибка чтения логов',
        'run_error': 'Ошибка при запуске контейнера',
        'container_not_found': 'Контейнер не найдет'
    }

    REDIS_KEY = 'container_id_{}'

    def __init__(self, user_id):
        self.user_id = user_id
        self.client = docker.DockerClient(DOCKER_HOST)

    def run_container(self, command) -> Container:
        return self.client.containers.run(self.IMAGE, command, detach=True)

    def get_container(self, uuid=None) -> Container:
        uuid = uuid or self._get_container_uuid()
        if not uuid:
            raise ServiceException(self.ERRORS['container_not_found'])
        return self.client.containers.get(uuid)

    def _get_container_uuid(self):
        return redis_model.get_container_id_by_user(self.user_id)

    def get_logs(self) -> str:
        try:
            return self.get_container().logs().decode('utf-8')
        except UnicodeDecodeError:
            raise DockerException(self.ERRORS['read_error'])

    def remove_user_container(self):
        try:
            container = self.get_container()
            container.remove()
        except ServiceException:
            logger.error(f'Пытались удалить контейнер пользователя которого не существует {self.user_id}')
        except DockerException as e:
            logger.exception(e)
        finally:
            redis_model.del_user_container_info(self.user_id)
        return True

    def run(self, code):
        command = [self.COMMAND] + code.split('\n')
        try:
            container = self.run_container(command)
            redis_model.set_container_info(self.user_id, container.id)
        except DockerException as e:
            logger.exception(e)
            raise ServiceException(self.ERRORS['run_error'])

    def is_container_running(self):
        try:
            container = self.get_container()
        except ServiceException:
            return False
        except DockerException as e:
            logger.exception(e)
            return False
        return container.attrs['State'] == 'running'

