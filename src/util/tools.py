import copy
all_fmap = {
    "创意展示URL": "f_creative_present_url",
    "搜索词": "f_search_word",
    "日期": "f_date",
    "点击率": "f_cpc_rate",
    "时间": "f_date",
    "推广组": "f_campaign_group",
    "账户": "f_account",
    "创意访问URL": "f_creative_visit_url",
    "推广组ID": "f_company_group_id",
    "消耗": "f_cost",
    "设备": "f_device",
    "推广计划ID": "f_campaign_id",
    "创意标题": "f_creative_title",
    "点击数": "f_click_count",
    "点击均价": "f_cpc_avg_price",
    "推广计划": "f_campaign",
    "创意id": "f_creative_id",
    "关键词平均排名": "f_keyword_avg_billing",
    "匹配方式": "f_matched_type",
    "展示数": "f_impression_count",
    "创意移动访问URL": "f_creative_mobile_visit_url",
    "关键词id": "f_keyword_id",
    "创意移动展示URL": "f_creative_mobile_present_url",
    "创意描述2": "f_creative_memo2",
    "创意描述1": "f_creative_memo1",
    "关键词": "f_keyword"
        }

unuse_field_dict = {
        "creative_report_sougou_sem": ["关键词id","时间","搜索词","关键词","匹配方式"],
        "search_report_sougou_sem": ["展示数","时间","关键词id","点击率","关键词平均排名"],
        "keyword_report_sougou_sem":[
                    "创意id","创意展示URL","搜索词","创意移动展示URL",
                    "匹配方式","时间","创意移动访问URL","创意访问URL",
                    "创意标题","创意描述2","创意描述1"],
        "campaign_report_sougou_sem": [
                    "创意id","创意展示URL","搜索词","日期","匹配方式",
                    "推广组","创意移动访问URL","创意访问URL","关键词id",
                    "推广组ID","创意标题","创意描述2","创意描述1",
                    "创意移动展示URL","关键词"]
        }

number_field_dict = {
        "keyword_report_sougou_sem":[
                    "f_impression_count", "f_click_count","f_cpc_rate",
                    "f_keyword_avg_billing", "f_cost", "f_cpc_avg_price"],
        "search_report_sougou_sem": ["f_click_count", "f_cost"],
        "creative_report_sougou_sem":["f_cpc_avg_price","f_impression_count",
                    "f_cpc_rate","f_click_count","f_cost", "f_keyword_avg_billing"],
        "campaign_report_sougou_sem": ["f_impression_count","f_click_count","f_cost", "f_keyword_avg_billing", "f_cpc_rate"]
        }

keyword_info_fmap = {
        "cpcGrpId": "f_company_group_id",
        "cpcId": "f_keyword_id",
        "cpc": "f_keyword",
        "price": "f_keyword_offer_price",
        "visitUrl": "f_pc_url",
        "mobileVisitUrl": "f_mobile_url",
        "matchType": "f_matched_type",
        "cpcQuality": "f_keyword_quality"
        }
report_type = {
        "search_report_sougou_sem": 6,
        "keyword_report_sougou_sem": 7,
        "creative_report_sougou_sem": 4,
        "campaign_report_sougou_sem": 2,
        }
def get_report_conf_info(route):
    un_need_field = unuse_field_dict[route]
    fmap = copy.deepcopy(all_fmap)
    for key in un_need_field:
        del fmap[key]
    return fmap, number_field_dict[route], report_type[route]


