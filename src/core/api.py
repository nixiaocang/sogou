import traceback
import asyncio
import pandas as pd
from core.sougousemservice import SogouSemService

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
            return {"status":2101, "message":str(e)}
        finally:
            # log
            print("username:%s auth over" % userinfo['account'])

class ReportService(object):
    @staticmethod
    async def get_report_data(infos, ReportRequestBag, fmap, number_list, special=False):
        sogou_core = SogouSemService()
        if infos['from_date'] > infos['to_date']:
            raise Exception("日期范围不合法")
        code, message, account_id = await sogou_core.auth_account(infos)
        if code != "SUCCESS":
            raise Exception(message)
        bag = {}
        for platform in (1, 2):
            str_device = '计算机' if platform == 1 else '移动'
            ReportRequestBag['platform'] = platform
            reportId = await sogou_core.get_report_Id(infos, ReportRequestBag)
            await asyncio.sleep(2)
            count = 0
            ready = False
            while count < 3:
                try:
                    isGenerated = await sogou_core.get_report_status(infos, reportId)
                    if str(isGenerated) != '1':
                        raise Exception("报告还未生成")
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
                url = await sogou_core.get_report_url(infos, reportId)
                bag[platform] = await sogou_core.get_file(reportId, url)
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
        fres['f_account_id'] = account_id
        return await sogou_core.format_data(infos, fres, fmap, number_list, special)

class KeywordReport(ReportService):
    @staticmethod
    async def do_action(infos):
        fmap = {
                "f_email": "f_email",
                "f_source": "f_source",
                "f_company_id": "f_company_id",
                "f_account_id": "f_account_id",
                "日期": "f_date",
                "账户": "f_account",
                "推广计划": "f_campaign",
                "推广组": "f_campaign_group",
                "消耗": "f_cost",
                "点击均价": "f_cpc_avg_price",
                "展示数": "f_impression_count",
                "点击数": "f_click_count",
                "点击率": "f_cpc_rate",
                "关键词平均排名": "f_keyword_avg_billing",
                "设备": "f_device",
                "关键词id": "f_keyword_id",
                "推广计划ID": "f_campaign_id",
                "推广组ID": "f_company_group_id"
                }
        number_list = ["f_impression_count", "f_click_count", "f_keyword_avg_billing", "f_cost", "f_cpc_avg_price", "f_cpc_rate"]
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
            traceback.print_exc()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            print("get keyword report over")


class SearchReport(ReportService):
    @staticmethod
    async def do_action(infos):
        fmap = {
                "f_source": "f_source",
                "f_company_id": "f_company_id",
                "f_email": "f_email",
                "f_account_id": "f_account_id",
                "日期": "f_date",
                "账户": "f_account",
                "推广计划": "f_campaign",
                "推广组": "f_campaign_group",
                "关键词": "f_keyword",
                "创意标题": "f_creative_title",
                "创意描述1": "f_creative_memo1",
                "创意描述2": "f_creative_memo2",
                "创意访问URL": "f_creative_visit_url",
                "创意展示URL": "f_creative_present_url",
                "创意移动访问URL": "f_creative_mobile_visit_url",
                "创意移动展示URL": "f_creative_mobile_present_url",
                "搜索词": "f_search_word",
                "点击数": "f_click_count",
                "消耗": "f_cost",
                "设备": "f_device",
                "推广计划ID": "f_campaign_id",
                "推广组ID": "f_company_group_id",
                }
        number_list = ["f_click_count", "f_cost"]
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
            traceback.print_exc()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            print("get search report over")


class CreativeReport(ReportService):
    @staticmethod
    async def do_action(infos):
        fmap = {
                "f_source": "f_source",
                "f_company_id": "f_company_id",
                "f_email": "f_email",
                "日期": "f_date",
                "账户": "f_account",
                "推广计划": "f_campaign",
                "推广组": "f_campaign_group",
                "创意描述1": "f_creative_memo1",
                "创意描述2": "f_creative_memo2",
                "创意访问URL": "f_creative_visit_url",
                "创意展示URL": "f_creative_present_url",
                "创意移动访问URL": "f_creative_mobile_visit_url",
                "创意移动展示URL": "f_creative_mobile_present_url",
                "点击均价": "f_cpc_avg_price",
                "展示数": "f_impression_count",
                "点击率": "f_cpc_rate",
                "点击数": "f_click_count",
                "消耗": "f_cost",
                "设备": "f_device",
                "f_account_id": "f_account_id",
                "推广计划ID": "f_campaign_id",
                "推广组ID": "f_company_group_id"
                }
        number_list = ["f_cpc_avg_price","f_impression_count","f_cpc_rate","f_click_count","f_cost"]
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
            traceback.print_exc()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            print("get creative report over")


class PlanReport(ReportService):
    @staticmethod
    async def do_action(infos):
        fmap = {
                "f_source": "f_source",
                "f_company_id": "f_company_id",
                "f_email": "f_email",
                "时间": "f_date",
                "账户": "f_account",
                "f_account_id": "f_account_id",
                "推广计划": "f_campaign",
                "推广计划ID": "f_campaign_id",
                "展示数": "f_impression_count",
                "点击数": "f_click_count",
                "消耗": "f_cost",
                "设备": "f_device"
                }
        number_list = ["f_impression_count","f_click_count","f_cost"]
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
            traceback.print_exc()
            return {"status":2101, "message": str(e), "content":{}}
        finally:
            print("get plan report over")


ActionMap = {
        "auth_account": DatasourceAuth,
        "keyword_sougou_sem": KeywordReport,
        "search_report_sougou_sem": SearchReport,
        "creative_report_sougou_sem": CreativeReport,
        "campaign_report_sougou_sem": PlanReport
                }
