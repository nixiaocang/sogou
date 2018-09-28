import time
import asyncio
import pandas as pd
from util.logger import print_stack, runtime_logger
from util.tools import get_report_field_map
from core.sougousemservice import SogouSemService

logger = runtime_logger()

class DatasourceAuth(object):
    @staticmethod
    async def do_action(userinfo):
        try:
            code, message, account_id = await SogouSemService().auth_account(userinfo)
            if code == "SUCCESS":
                return {"status":2000, "message":"OK"}
            else:
                return {"status":2100, "message":message}
        except Exception as e:
            logger.info("验证用户信息时出现错误:%s" % str(e))
            print_stack()
            return {"status":2101, "message":str(e)}
        finally:
            logger.info("trace_id: %s auth over" % userinfo['trace_id'])

class ReportService(object):
    @staticmethod
    async def get_report_data(infos, ReportRequestBag, fmap, number_list, special=False):
        sogou_core = SogouSemService()
        logger.info("trace_id: %s 开始进行日期合法性校验" % infos['trace_id'])
        if infos['from_date'] > infos['to_date']:
            raise Exception("日期范围不合法" % infos["account"])
        logger.info("trace_id: %s 进行用户信息校验" % infos['trace_id'])
        code, message, account_id = await sogou_core.auth_account(infos)
        if code != "SUCCESS":
            raise Exception(message)
        infos['account_id'] = account_id
        bag = {}
        for platform in (1, 2):
            str_device = '计算机' if platform == 1 else '移动'
            ReportRequestBag['platform'] = platform
            logger.info("trace_id: %s 开始获取:%s报告ID" % (infos['trace_id'], str_device))
            reportId = await sogou_core.get_report_Id(infos, ReportRequestBag)
            logger.info("trace_id: %s 获取:%s报告ID:%s" % (infos['trace_id'], str_device, reportId))
            await asyncio.sleep(2)
            count = 0
            ready = False
            logger.info("trace_id: %s 获取报告ID:%s的生成状态" % (infos['trace_id'], reportId))
            while count < 3:
                try:
                    isGenerated = await sogou_core.get_report_status(infos, reportId)
                    if str(isGenerated) != '1':
                        raise Exception("trace_id: %s 报告还未生成" % infos["trace_id"])
                    ready = True
                    break
                except Exception as e:
                    if str(e) == 'Request report data is null':
                        break
                    await asyncio.sleep(3)
                    count += 1
                    if count == 3:
                        raise e
            if ready:
                logger.info("trace_id: %s 获取报告ID:%s的下载链接" % (infos['trace_id'], reportId))
                url = await sogou_core.get_report_url(infos, reportId)
                logger.info("trace_id: %s 获取报告ID:%s的下载链接:%s" % (infos['trace_id'], reportId, url))
                bag[platform] = await sogou_core.get_file(reportId, url)
                logger.info("trace_id: %s 获取报告ID:%s的下载报告完成" % (infos['trace_id'], reportId))
                bag[platform]['设备'] = str_device
        if bag.get(1) is not None and bag.get(2) is not None:
            fres = pd.concat([bag[1],bag[2]])
        elif bag.get(1) is not None:
            fres = bag[1]
        elif bag.get(2) is not None:
            fres = bag[2]
        else:
            fres = None
            return {}
        logger.info("trace_id: %s 开始格式化数据" % infos['trace_id'])
        start = time.time()
        result = await sogou_core.format_data(infos, fres, fmap, number_list, special)
        cost = time.time()-start
        logger.info("trace_id: %s 格式化数据完成耗时:%s" % (infos['trace_id'], cost))
        return result

class KeywordReport(ReportService):
    @staticmethod
    async def do_action(infos):
        fmap, number_list = get_report_field_map("keyword")
        try:
            ReportRequestBag = {
                'performanceData': ['cost','cpc','click','impression','ctr','position'],
                'startDate': infos['from_date'],
                'endDate': infos['to_date'],
                'reportType':7,
                'unitOfTime':1
                }
            res = await ReportService().get_report_data(infos, ReportRequestBag, fmap, number_list)
            return {"status":2000, "message":"OK", "content":res}
        except Exception as e:
            print_stack()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            logger.info("trace_id: %s get keyword report over" % infos["trace_id"])


class KeywordInfoReport(ReportService):
    async def do_action(infos):
        fmap = keyword_info_fmap
        try:
            keyword_infos = await KeywordReport.do_action(infos)
            if keyword_infos['status'] != 2000:
                raise Exception(keyword_infos['message'])
            start = time.time()
            logger.info("trace_id: %s 开始请求&格式化关键词信息数据" % infos['trace_id'])
            kres = keyword_infos['content']
            res = {}
            for k, v in kres.items():
                for device in ('计算机', '移动'):
                    company_dict = {}
                    ids = []
                    for item in v:
                        if item['f_device']== device and item['f_keyword_id']:
                            company_dict[item['f_keyword_id']] = item['f_campaign_id']
                            ids.append(item['f_keyword_id'])
                    if ids:
                        res[k] = await SogouSemService().get_keyword_info(infos, list(set(ids)), device, fmap, k, company_dict)
            cost = time.time()-start
            logger.info("trace_id: %s 请求&格式化关键词信息数据完毕,耗时：%s" % (infos['trace_id'], cost))
            return {"status":2101, "message": "OK", "content":res}
        except Exception as e:
            print_stack()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            logger.info("trace_id: %s get keyword info over" % infos["trace_id"])

class SearchReport(ReportService):
    @staticmethod
    async def do_action(infos):
        fmap, number_list = get_report_field_map("search")
        try:
            ReportRequestBag = {
                'performanceData': ['cost', 'click', 'cpc'],
                'startDate': infos['from_date'],
                'endDate': infos['to_date'],
                'reportType':6,
                'unitOfTime':1
                }
            res = await ReportService().get_report_data(infos, ReportRequestBag, fmap, number_list)
            return {"status":2000, "message":"OK", "content":res}
        except Exception as e:
            print_stack()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            logger.info("trace_id: %s get search report over" % infos["trace_id"])


class CreativeReport(ReportService):
    @staticmethod
    async def do_action(infos):
        fmap, number_list = get_report_field_map("creative")
        try:
            ReportRequestBag = {
                'performanceData': ['cost','cpc','click','impression','ctr','position'],
                'startDate': infos['from_date'],
                'endDate': infos['to_date'],
                'reportType':4,
                'unitOfTime':1
                }
            res = await ReportService().get_report_data(infos, ReportRequestBag, fmap, number_list)
            return {"status":2000, "message":"OK", "content":res}
        except Exception as e:
            print_stack()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            logger.info("trace_id: %s get creative report over" % infos["trace_id"])


class PlanReport(ReportService):
    @staticmethod
    async def do_action(infos):
        fmap, number_list = get_report_field_map("plan")
        try:
            ReportRequestBag = {
                'performanceData': ['cost','cpc','click','impression','ctr','position'],
                'startDate': infos['from_date'],
                'endDate': infos['to_date'],
                'reportType':2,
                'unitOfTime':4
                }
            res = await ReportService().get_report_data(infos, ReportRequestBag, fmap, number_list, special=True)
            return {"status":2000, "message":"OK", "content":res}
        except Exception as e:
            print_stack()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            logger.info("trace_id: %s get plan report over" % infos["trace_id"])


ActionMap = {
        "auth_account": DatasourceAuth,
        "keyword_sougou_sem": KeywordInfoReport,
        "search_report_sougou_sem": SearchReport,
        "creative_report_sougou_sem": CreativeReport,
        "campaign_report_sougou_sem": PlanReport,
        "keyword_report_sougou_sem": KeywordReport
                }
