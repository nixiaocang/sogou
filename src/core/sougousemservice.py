import asyncio
import threading
import pandas as pd
from suds.client import Client

def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


def Singleton(cls):
    instances = {}

    @synchronized
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return get_instance

@Singleton
class SogouSemService(object):

    def _create_client(self, service, userinfo):
        URL = 'http://api.agent.sogou.com/sem/sms/v1/' + service + '?wsdl'
        client = Client(URL)
        header = client.factory.create('ns0:AuthHeader')
        header.username = userinfo['username']
        header.password = userinfo['password']
        header.token =  userinfo['token']
        client.set_options(soapheaders=[header,])
        return client

    def _deal_res(self, res):
        res = str(res)
        if '<ns3:desc>failure' in res:
            code = res.split('<ns3:code>')[1].split('</ns3:code>')[0]
            message = res.split('<ns3:message>')[1].split('</ns3:message>')[0]
        elif '<ns3:desc>success' in res:
            code = 'SUCCESS'
            message = ''
        else:
            code = 'FAIL'
            message = '未知错误'
        return code, message

    async def auth_account(self, userinfo):
        client = self._create_client("AccountService", userinfo)
        res = client.service.getAccountInfo()
        fres = client.last_received()
        code, message = self._deal_res(fres)
        return code, message

    async def get_report_Id(self, userinfo, ReportRequestBag):
        client = self._create_client("ReportService", userinfo)
        ReportRequestType = client.factory.create('ReportRequestType')
        ReportRequestType.performanceData = ReportRequestBag['performanceData']
        ReportRequestType.startDate = ReportRequestBag['startDate']
        ReportRequestType.endDate = ReportRequestBag['endDate']
        ReportRequestType.reportType = ReportRequestBag['reportType']
        ReportRequestType.unitOfTime = ReportRequestBag['unitOfTime']
        ReportRequestType.platform = ReportRequestBag['platform']
        reportId = client.service.getReportId(ReportRequestType)
        fres = client.last_received()
        print(fres)
        code, message = self._deal_res(fres)
        if str(code) != 'SUCCESS':
            raise Exception(message)
        return reportId

    async def get_report_status(self, userinfo, reportId):
        client = self._create_client("ReportService", userinfo)
        isGenerated = client.service.getReportState(reportId)
        fres = client.last_received()
        code, message = self._deal_res(fres)
        if str(code) != 'SUCCESS':
            raise Exception(message)
        return isGenerated

    async def get_report_url(self, userinfo, reportId):
        client = self._create_client("ReportService", userinfo)
        reportFilePath = client.service.getReportPath(reportId)
        fres = client.last_received()
        code, message = self._deal_res(fres)
        if str(code) != 'SUCCESS':
            raise Exception(message)
        return reportFilePath

    async def get_keyword_info(self, userinfo, keyword_ids):
        client = self._create_client("CpcService", userinfo)
        infos = client.service.getCpcByCpcId(cpcIds=keyword_ids, getTemp=0)
        data = []
        key_list = ['cpcId','cpcGrpId','cpc','price','visitUrl','mobileVisitUrl', 'matchType','cpcQuality']
        for info in infos:
            bag = {}
            for key in key_list:
                bag[key] = getattr(info, key)
            data.append(bag)
        return data

    async def get_file(self, reportId, url):
        res = requests.get(url)
        gzipname = reportId + '.csv.gz'
        filename = reportId + '.csv'
        with open(gzipname, "wb") as code:
            code.write(res.content)
        g = gzip.GzipFile(mode="rb", fileobj=open(gzipname,'rb'))
        with open(filename, "wb") as writer:
            writer.write(g.read())
        df = pd.read_csv(filename, encoding='gbk')
        df = df.drop([0])
        return df
