import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado
import asyncio
import functools
from src.core.api import DatasourceAuth, KeywordReport
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class IndexHandler(tornado.web.RequestHandler):
    async def get(self):
        greeting = self.get_argument('greeting', 'Hello')
        self.write(greeting + ', friendly user!')

class AuthAccountHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)
        res = await DatasourceAuth().auth_account(data)
        self.add_header("Content-Type", "application/json;charset=utf-8")
        self.write(json.dumps(res))

class KeywordReportHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)
        res = await KeywordReport().get_keyword_report(data)
        self.add_header("Content-Type", "application/json;charset=utf-8")
        self.write(json.dumps(res))


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
        (r"/", IndexHandler),
        (r"/auth_account", AuthAccountHandler),
        (r"/keyword_sougou_sem", KeywordReportHandler)
        ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
