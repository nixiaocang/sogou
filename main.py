import json
import time
import uuid
import tornado
import asyncio
import functools
import tornado.web
import tornado.ioloop
import tornado.httpserver
from src.core.api import ActionMap
from util.config import Configuration
from src.util.logger import runtime_logger

class BaseHandler(tornado.web.RequestHandler):
    route = None
    async def post(self):
        trace_id = str(uuid.uuid4()).replace('-','')
        runtime_logger().info("trace_id:%s 请求参数:%s" % (trace_id, self.request.body))
        start = time.time()
        data = json.loads(self.request.body)
        data['trace_id'] = trace_id
        data['route'] = self.route
        res = await ActionMap[self.route].do_action(data)
        self.add_header("Content-Type", "application/json;charset=utf-8")
        cost = time.time() - start
        runtime_logger().info("trace_id:%s 请求结束,耗时:%s" % (trace_id, str(cost)))
        res['trace_id'] = trace_id
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
    conf = Configuration()
    port = int(conf.get("global", 'port'))
    debug_model = int(conf.get('global', 'debug'))
    process_num = int(conf.get('global', 'process_num'))
    http_server.listen(int(port))
    http_server.start(1 if debug_model else process_num)
    tornado.ioloop.IOLoop.current().start()
