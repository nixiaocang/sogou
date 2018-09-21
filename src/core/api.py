import asyncio
import pandas as pd
from core.sougousemservice import SogouSemService

class DatasourceAuth(object):
    @staticmethod
    async def auth_account(userinfo):
        try:
            code, message = await SogouSemService().auth_account(userinfo)
            if code == "SUCCESS":
                return {"status":2000, "message":"OK"}
            else:
                return {"status":2100, "message":message}
        except Exception as e:
            return {"status":2101, "message":str(e)}
        finally:
            # log
            print("username:%s auth over" % userinfo['username'])

class ReportService(object):
    @staticmethod
    async def get_report_data(userinfo, ReportRequestBag):
        sogou_core = SogouSemService()
        bag = {}
        for platform in (1, 2):
            ReportRequestBag['platform'] = platform
            reportId = await sogou_core.get_report_Id(userinfo, ReportRequestBag)
            await asyncio.sleep(2)
            count = 0
            ready = False
            while count < 3:
                try:
                    isGenerated = await sogou_core.get_report_status(reportId)
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
                url = await sogou_core.get_report_url(reportId)
                bag[device] = await sogou_core.get_file(reportId, url)
                bag[device]['设备'] = str_device
        if bag.get(1) is not None and bag.get(2) is not None:
            fres = pd.concat([bag[1],bag[2]])
        elif bag.get(1) is not None:
            fres = bag[1]
        elif bag.get(2) is not None:
            fres = bag[2]
        else:
            fres = None
        return fres




class KeywordReport(ReportService):
    @staticmethod
    async def get_keyword_report(userinfo, startDate, endDate):
        try:
            ReportRequestBag = {
                'performanceData': ['cost','cpc','click','impression','ctr','position'],
                'startDate':startDate,
                'endDate':endDate,
                'reportType':2,
                'unitOfTime':4
                }
            res = await get_report_data(userinfo, ReportRequestBag)
            return res
        except Exception as e:
            raise e
        finally:
            # log
            print("get keyword report over")



