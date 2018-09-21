import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado
import asyncio
import functools
from src.core.api import DatasourceAuth
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    async def get(self):
        greeting = self.get_argument('greeting', 'Hello')
        self.write(greeting + ', friendly user!')

class AuthAccountHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)
        username = data['username']
        password = data['password']
        token = data['token']
        userinfo = {
                "username":username,
                "password":password,
                "token":token
                }
        print(userinfo)
        print("******")
        res = await DatasourceAuth().auth_account(userinfo)
        print(res)
        self.write(res)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
        (r"/", IndexHandler),
        (r"/auth_account", AuthAccountHandler)
        ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
