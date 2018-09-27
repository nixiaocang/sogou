import json
import time
import tornado
import asyncio
import functools
from src.core.api import ActionMap
from src.util.config import get
from src.util.logger import runtime_logger

class BaseHandler(tornado.web.RequestHandler):
    route = None
    async def post(self):
        runtime_logger().info("请求参数:%s" % self.request.body)
        start = time.time()
        data = json.loads(self.request.body)
        res = await ActionMap[self.route].do_action(data)
        self.add_header("Content-Type", "application/json;charset=utf-8")
        runtime_logger().info("请求结束,耗时:%s" % time.time()-start)
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
    app = tornado.web.Application(handlers=[
        (r"/auth_account", AuthAccountHandler),
        (r"/keyword_sougou_sem", KeywordInfoReportHandler),
        (r"/search_report_sougou_sem", SearchReportHandler),
        (r"/campaign_report_sougou_sem", PlanReportHandler),
        (r"/keyword_report_sougou_sem", KeywordReportHandler),
        (r"/creative_report_sougou_sem", CreativeReportHandler)
        ])
    http_server = tornado.httpserver.HTTPServer(app)
    port = get("global", 'port')
    debug_model = int(get('global', 'debug'))
    http_server.listen(int(port))
    http_server.start(1 if debug_model else 10)
    tornado.ioloop.IOLoop.current().start()
