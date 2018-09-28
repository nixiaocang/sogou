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

un_need_dict = {
        "keyword":[
                    "创意id","创意展示URL","搜索词","创意移动展示URL",
                    "匹配方式","时间","创意移动访问URL","创意访问URL",
                    "创意标题","创意描述2","创意描述1"],
        "search": ["展示数","时间","关键词id","点击率","关键词平均排名"],
        "creative": ["关键词id","时间","搜索词","关键词","匹配方式"],
        "plan": [
                    "创意id","创意展示URL","搜索词","日期","匹配方式",
                    "推广组","创意移动访问URL","创意访问URL","关键词id",
                    "推广组ID","创意标题","创意描述2","创意描述1",
                    "创意移动展示URL","关键词"]
        }

number_field_dict = {
        "keyword":[
                    "f_impression_count", "f_click_count","f_cpc_rate",
                    "f_keyword_avg_billing", "f_cost", "f_cpc_avg_price"],
        "search": ["f_click_count", "f_cost"],
        "creative":["f_cpc_avg_price","f_impression_count",
                    "f_cpc_rate","f_click_count","f_cost"],
        "plan": ["f_impression_count","f_click_count","f_cost"]
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
def get_report_field_map(name):
    un_need_field = un_need_dict[name]
    fmap = copy.deepcopy(all_fmap)
    for key in un_need_field:
        del fmap[key]
    return fmap, number_field_dict[name]


