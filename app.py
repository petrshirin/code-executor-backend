from flask import Flask
from flask_restful import Api
from settings import HOST, PORT
from api.resources import ExecuteResource, LogResource


app = Flask(__name__)
api = Api(app)

api.add_resource(ExecuteResource, '/api/execute/')
api.add_resource(LogResource, '/api/get_logs/')


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
