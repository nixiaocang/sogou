import os
import json
import gzip
import asyncio
import requests
import threading
import pandas as pd
from suds.client import Client
from util.config import Configuration, Singleton
import warnings
warnings.filterwarnings('ignore')

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

    async def get_keyword_info(self, infos, keyword_ids, device, fmap, date, campaign_dict):
        client = self._create_client("CpcService", infos)
        kword_infos = client.service.getCpcByCpcId(cpcIds=keyword_ids, getTemp=0)
        data = []
        for kinfo in kword_infos:
            bag = {}
            for key in fmap.keys():
                bag[fmap[key]] = getattr(kinfo, key)
            bag['f_source'] = infos['pt_source']
            bag['f_email'] = infos['pt_email']
            bag['f_date'] = date
            bag['f_account'] = infos['account']
            bag['f_account_id'] = infos['account_id']
            bag['f_device'] = device
            bag['f_campaign_id'] = campaign_dict.get(bag['f_keyword_id'])
            data.append(bag)
        return data

    async def get_file(self, reportId, url):
        path = Configuration().get('global', 'log_path')
        res = requests.get(url)
        gzipname = os.path.join(path, reportId + '.csv.gz')
        filename = os.path.join(path, reportId + '.csv')
        with open(gzipname, "wb") as code:
            code.write(res.content)
        g = gzip.GzipFile(mode="rb", fileobj=open(gzipname,'rb'))
        with open(filename, "wb") as writer:
            writer.write(g.read())
        df = pd.read_csv(filename, encoding='gbk')
        df = df.drop([0])
        return df

    async def format_data(self, infos, fres, fmap, number_list, special):
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
                pass
        if 'f_cpc_rate' in new_cols:
            fres['f_cpc_rate'] = pd.to_numeric(fres['f_cpc_rate'].str.split('%',expand=True)[0])/100
        fres[number_list] = fres[number_list].apply(pd.to_numeric)
        fres['f_source'] = infos['pt_source']
        fres['f_company_id'] = infos['pt_company_id']
        fres['f_email'] = infos['pt_email']
        fres['f_account_id'] = infos['account_id']
        if special:
            return await self.deal_two(fres, infos)
        else:
            return await self.deal_one(fres, infos)

    async def deal_one(self, fres, infos):
        dates = pd.date_range(infos['from_date'], infos['to_date'])
        result = {}
        for date in dates:
            date = str(date)[:10]
            temp_df = fres[fres['f_date']==date]
            tres = temp_df.to_json(orient="records")
            ttres = json.loads(tres)
            result[date] = ttres
        return result

    async def deal_two(self, fres, infos):
        startDate = infos['from_date'] + ' 00:00:00'
        endDate = infos['to_date'] + ' 23:00:00'
        dates = pd.date_range(startDate, endDate, freq='1h')
        result = {}
        hour_list = [
                    "00:00:00","01:00:00","02:00:00","03:00:00",
                    "04:00:00","05:00:00","06:00:00","07:00:00",
                    "08:00:00","09:00:00","10:00:00","11:00:00",
                    "12:00:00","13:00:00","14:00:00","15:00:00",
                    "16:00:00","17:00:00","18:00:00","19:00:00",
                    "20:00:00","21:00:00","22:00:00","23:00:00"
                    ]
        for date in dates:
            sub_date = str(date)[:10]
            edate = str(date)[11:]
            sub_key = "%s-%s" % (edate, hour_list[(hour_list.index(edate)+1)%24])
            if sub_date not in result:
                result[sub_date] = {}
            temp_df = fres[fres['f_date'] == str(date)[:13]]
            temp_df['f_date'] = str(date)
            tres = temp_df.to_json(orient="records")
            ttres = json.loads(tres)
            result[sub_date][sub_key] = ttres
        return result




