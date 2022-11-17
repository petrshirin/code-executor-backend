from dataclasses import dataclass
import logging

from flask_restful import Resource
from flask import request

from executor.docker_service import DockerService, ServiceException
from utils.exception import BaseApiException, RequestException
from utils.validators import RequiredValidator, AuthKeyValidator, TypeValidator
from settings import AUTH_KEY, SITE_URL
from api.redis_client import redis_model


LOG = logging.getLogger(__name__)


@dataclass
class BaseRequestDataclass:
    auth_key: str


@dataclass
class ExecuteRequestDataclass(BaseRequestDataclass):
    user_id: int
    available_time: float
    code: str


@dataclass
class LogRequestDataclass(BaseRequestDataclass):
    user_id: int


class BaseResource(Resource):
    ERROR_MESSAGES = {
        'not_json': 'Запрос должен быть в JSON формате'
    }
    request_data: BaseRequestDataclass

    VALIDATOR_SCHEMA = {}
    dataclass = BaseRequestDataclass

    @staticmethod
    def create_response(success=True, content=None, code=None):
        if content is None:
            content = {}
        response = {'success': success}
        response.update(content)
        if not code:
            code = 200 if success else 400
        return response, code

    def validate_request(self):
        if not request.is_json:
            raise RequestException(self.ERROR_MESSAGES['not_json'])
        self.validate_body(request.json)
        self.request_data = self.dataclass(**request.json)

    def validate_body(self, data):
        for key, value in self.VALIDATOR_SCHEMA.items():
            for validator in value:
                validator(key, data.get(key))

    def post(self):
        try:
            self.validate_request()
        except BaseApiException as e:
            LOG.error(e)
            return self.create_response(False, {'error': e.message}, e.status)
        return self.create_response()


class ExecuteResource(BaseResource):
    VALIDATOR_SCHEMA = {
        'auth_key': [RequiredValidator(), TypeValidator(str), AuthKeyValidator(AUTH_KEY)],
        'user_id': [RequiredValidator(), TypeValidator(int)],
        'available_time': [RequiredValidator(), TypeValidator(float)],
        'code': [RequiredValidator(), TypeValidator(str)]
    }
    request_data: ExecuteRequestDataclass
    dataclass = ExecuteRequestDataclass

    def post(self):
        response, code = super(ExecuteResource, self).post()
        if code >= 400:
            return response, code
        LOG.info(self.request_data)
        docker_service = DockerService(self.request_data.user_id)
        redis_model.set_user_available_time(self.request_data.user_id, self.request_data.available_time)
        try:
            docker_service.run(self.request_data.code)
        except ServiceException as e:
            redis_model.set_user_new_available_time(self.request_data.user_id)
            return self.create_response(False, {'logs': docker_service.get_logs(), 'error': e.message})
        return self.create_response(True, {'url_to_logs': f'{SITE_URL}/logs/'}, 201)


class LogResource(BaseResource):
    VALIDATOR_SCHEMA = {
        'auth_key': [RequiredValidator(), TypeValidator(str), AuthKeyValidator(AUTH_KEY)],
        'user_id': [RequiredValidator(), TypeValidator(int)],
    }
    request_data: LogRequestDataclass
    dataclass = LogRequestDataclass

    def post(self):
        response, code = super(LogResource, self).post()
        if code >= 400:
            return response, code
        docker_service = DockerService(self.request_data.user_id)
        try:
            logs = docker_service.get_logs()
        except ServiceException as e:
            return self.create_response(False, {'logs': None, 'error': e.message})
        return self.create_response(content={'logs': logs, })

