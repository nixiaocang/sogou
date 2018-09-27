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
    route = "keyword_report_sougou_sem"

class KeywordInfoReportHandler(BaseHandler):
    route = 'keyword_sougou_sem'

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
        (r"/keyword_sougou_sem", KeywordInfoReportHandler),
        (r"/search_report_sougou_sem", SearchReportHandler),
        (r"/campaign_report_sougou_sem", PlanReportHandler),
        (r"/keyword_report_sougou_sem", KeywordReportHandler),
        (r"/creative_report_sougou_sem", CreativeReportHandler)
        ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    http_server.start(10)

    tornado.ioloop.IOLoop.current().start()
    """""
    port = Configuration().get("global", "port")
    debug_model = int(Configuration().get('global', 'debug'))
    sys.stderr.write("listen server on port %s ..\n" % port)
    application = KstApplication(handler, **{
        'debug':True if debug_model else False,
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        #"template_path": os.path.join(os.path.dirname(__file__), "templates"),
        #"cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        #"login_url": "/api/login"
    })
    server = tornado.httpserver.HTTPServer(application, max_buffer_size=1024*1024*1024)
    server.bind(port)
    server.start(1 if debug_model else 10)
    tornado.ioloop.IOLoop.instance().start()
    """""
