import json
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado
import asyncio
import functools
from src.core.api import ActionMap
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class BaseHandler(tornado.web.RequestHandler):
    route = None
    async def post(self):
        data = json.loads(self.request.body)
        res = await ActionMap[self.route].do_action(data)
        self.add_header("Content-Type", "application/json;charset=utf-8")
        self.write(json.dumps(res))

class AuthAccountHandler(BaseHandler):
    route = "auth_account"

class KeywordReportHandler(BaseHandler):
    route = "keyword_sougou_sem"

class SearchReportHandler(BaseHandler):
    route = "search_report_sougou_sem"

class CreativeReportHandler(BaseHandler):
    route = "creative_report_sougou_sem"

class PlanReportHandler(BaseHandler):
    route = "campaign_report_sougou_sem"

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[
        (r"/auth_account", AuthAccountHandler),
        (r"/keyword_sougou_sem", KeywordReportHandler),
        (r"/search_report_sougou_sem", SearchReportHandler),
        (r"/creative_report_sougou_sem", CreativeReportHandler),
        (r"/campaign_report_sougou_sem", PlanReportHandler)
        ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
