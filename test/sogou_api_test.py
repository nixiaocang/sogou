# coding:utf-8
"""
sogou api  测试脚本
"""

import time
import json
import unittest
import requests
import warnings
warnings.filterwarnings('ignore')

class TestSogouApi(unittest.TestCase):
    def setUp(self):
        self.data = {
                "pt_source":"搜狗推广",
                "pt_company_id":"12345abcde",
                "pt_email":"12345@email.cn",
                "account":"li.zechao@xhgroup.cn",
                "password":"Bj-Wtqx$2018WySgo",
                "token":"6ea7815dcd298a2d9a48ab674fde9f03",
                "from_date": "2018-08-26",
                "to_date":"2018-08-26",
                "account_id":18612035,

                }

    def tearDown(self):
        pass

    # 接口测试
    def test_auth_account(self):
        url = 'http://127.0.0.1:8000/auth_account'
        data = json.dumps(self.data)
        start = time.time()
        res = requests.post(url, data=data)
        cost = time.time()-start
        print("auth_account 耗时:%s" % str(cost))
        result = json.loads(res.content)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(result['status'], 2000)
        self.assertEquals(result['message'], "OK")

    def test_keyword_sougou_sem(self):
        url = 'http://127.0.0.1:8000/keyword_sougou_sem'
        data = json.dumps(self.data)
        start = time.time()
        res = requests.post(url, data=data)
        cost = time.time()-start
        print("keyword_sougou_sem 耗时:%s" % str(cost))
        result = json.loads(res.content)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(result['status'], 2000)
        self.assertEquals(result['message'], "OK")
        self.assertEquals(type(result['content']), type({}))

    def test_search_report_sougou_sem(self):
        url = 'http://127.0.0.1:8000/search_report_sougou_sem'
        data = json.dumps(self.data)
        start = time.time()
        res = requests.post(url, data=data)
        cost = time.time()-start
        print("search_report_sougou_sem 耗时:%s" % str(cost))
        result = json.loads(res.content)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(result['status'], 2000)
        self.assertEquals(result['message'], "OK")
        self.assertEquals(type(result['content']), type({}))

    def test_campaign_report_sougou_sem(self):
        url = 'http://127.0.0.1:8000/campaign_report_sougou_sem'
        data = json.dumps(self.data)
        start = time.time()
        res = requests.post(url, data=data)
        cost = time.time()-start
        print("campaign_report_sougou_sem 耗时:%s" % str(cost))
        result = json.loads(res.content)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(result['status'], 2000)
        self.assertEquals(result['message'], "OK")
        self.assertEquals(type(result['content']), type({}))

    def test_keyword_report_sougou_sem(self):
        url = 'http://127.0.0.1:8000/keyword_report_sougou_sem'
        data = json.dumps(self.data)
        start = time.time()
        res = requests.post(url, data=data)
        cost = time.time()-start
        print("keyword_report_sougou_sem 耗时:%s" % str(cost))
        result = json.loads(res.content)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(result['status'], 2000)
        self.assertEquals(result['message'], "OK")
        self.assertEquals(type(result['content']), type({}))

    def test_creative_report_sougou_sem(self):
        url = 'http://127.0.0.1:8000/creative_report_sougou_sem'
        data = json.dumps(self.data)
        start = time.time()
        res = requests.post(url, data=data)
        cost = time.time()-start
        print("creative_report_sougou_sem 耗时:%s" % str(cost))
        result = json.loads(res.content)
        self.assertEquals(res.status_code, 200)
        self.assertEquals(result['status'], 2000)
        self.assertEquals(result['message'], "OK")
        self.assertEquals(type(result['content']), type({}))

    # 功能测试
    def test_format_data(self):
        """
        编号,日期,账户,推广计划ID,推广计划,推广组ID,推广组,关键词id,关键词,消耗,点击均价,点击数,展示数,点击率,关键词平均排名
        1,2018-08-26,li.zechao@xhgroup.cn,197236017,退伍,941396050,哪招-退伍军人,29039369674,招退伍军人,0.62,0.62,1,4,25.00%,1.5
        """
        import os
        import sys
        import asyncio
        import pandas as pd
        from core.sougousemservice import SogouSemService

        pwd = os.path.realpath(__file__)
        path = os.path.abspath(os.path.dirname(pwd))
        filename = os.path.join(path, 'example.csv')
        fres = pd.read_csv(filename, encoding='gbk')
        fmap = {
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
                "关键词id": "f_keyword_id",
                "推广计划ID": "f_campaign_id",
                "推广组ID": "f_company_group_id",
                "关键词": "f_keyword"
                }
        number_list = ["f_impression_count", "f_click_count","f_cpc_rate","f_keyword_avg_billing", "f_cost", "f_cpc_avg_price"]
        special = False
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(SogouSemService().format_data(self.data, fres, fmap, number_list, special))
        loop.close()
        except_res = {
                "f_date":"2018-08-26",
                "f_account":"li.zechao@xhgroup.cn",
                "f_campaign":"退伍",
                "f_campaign_group":"哪招-退伍军人",
                "f_cost":0.62,
                "f_cpc_avg_price":0.62,
                "f_impression_count":4,
                "f_click_count":1,
                "f_cpc_rate":0.25,
                "f_keyword_avg_billing":1.5,
                "f_keyword_id":29039369674,
                "f_campaign_id":197236017,
                "f_company_group_id":941396050,
                "f_keyword":"招退伍军人",
                "f_account_id":18612035,
                "f_source": "搜狗推广",
                "f_company_id": "12345abcde",
                "f_email": "12345@email.cn"

                }
        self.assertEquals(type(res), type({}))
        sub_res = res["2018-08-26"][0]
        for k in sub_res:
            self.assertEquals(sub_res[k], except_res[k])



if __name__ == '__main__':
    unittest.main()

