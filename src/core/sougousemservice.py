import json
import gzip
import asyncio
import requests
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

    def _create_client(self, service, infos):
        URL = 'http://api.agent.sogou.com/sem/sms/v1/' + service + '?wsdl'
        client = Client(URL)
        header = client.factory.create('ns0:AuthHeader')
        header.username = infos['account']
        header.password = infos['password']
        header.token =  infos['token']
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

    async def auth_account(self, infos):
        account_id = None
        client = self._create_client("AccountService", infos)
        res = client.service.getAccountInfo()
        fres = client.last_received()
        code, message = self._deal_res(fres)
        if code == 'SUCCESS':
            account_id = res.accountid
        return code, message, account_id

    async def get_report_Id(self, infos, ReportRequestBag):
        client = self._create_client("ReportService", infos)
        ReportRequestType = client.factory.create('ReportRequestType')
        ReportRequestType.performanceData = ReportRequestBag['performanceData']
        ReportRequestType.startDate = ReportRequestBag['startDate']
        ReportRequestType.endDate = ReportRequestBag['endDate']
        ReportRequestType.reportType = ReportRequestBag['reportType']
        ReportRequestType.unitOfTime = ReportRequestBag['unitOfTime']
        ReportRequestType.platform = ReportRequestBag['platform']
        reportId = client.service.getReportId(ReportRequestType)
        fres = client.last_received()
        code, message = self._deal_res(fres)
        if str(code) != 'SUCCESS':
            raise Exception(message)
        return reportId

    async def get_report_status(self, infos, reportId):
        client = self._create_client("ReportService", infos)
        isGenerated = client.service.getReportState(reportId)
        fres = client.last_received()
        code, message = self._deal_res(fres)
        if str(code) != 'SUCCESS':
            raise Exception(message)
        return isGenerated

    async def get_report_url(self, infos, reportId):
        client = self._create_client("ReportService", infos)
        reportFilePath = client.service.getReportPath(reportId)
        fres = client.last_received()
        code, message = self._deal_res(fres)
        if str(code) != 'SUCCESS':
            raise Exception(message)
        return reportFilePath

    async def get_keyword_info(self, infos, keyword_ids):
        client = self._create_client("CpcService", infos)
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

    async def format_data(self, infos, fres, fmap, number_list):
        cols = [col for col in fres]
        new_cols = []
        for col in cols:
            if col not in fmap.keys():
                del fres[col]
            else:
                new_cols.append(fmap[col])
        fres.columns = new_cols
        for col in new_cols:
            try:
                if col in number_list:
                    default = 0 if col != "f_cpc_rate" else "0.0"
                else:
                    default = ""
                fres.ix[fres[col] == '--', col] = default
            except Exception as e:
                print(str(e))
                pass
        if 'f_cpc_rate' in new_cols:
            fres['f_cpc_rate'] = pd.to_numeric(fres['f_cpc_rate'].str.split('%',expand=True)[0])/100
        fres[number_list] = fres[number_list].apply(pd.to_numeric)
        dates = pd.date_range(infos['from_date'], infos['to_date'])
        result = {}
        for date in dates:
            date = str(date)[:10]
            temp_df = fres[fres['f_date']==date]
            tres = temp_df.to_json(orient="records")
            ttres = json.loads(tres)
            result[date] = ttres
        return result

