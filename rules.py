# 店铺固定规则（关键词 -> 约束）
SHOP_RULES = {
    "标题": "禁止使用极限词（最、第一、顶级、全网最低）",
    "售后": "签收7天内可退换，质量问题包邮，个人原因买家自理运费",
    "投放": "ROI低于2.5时降低出价10%，ROI高于4时可加价扩量",
    "库存": "单品库存低于50件自动触发采购提醒",
}

def get_rules(task_type: str) -> str:
    """根据任务类型返回相关规则"""
    if task_type == "product":
        return SHOP_RULES.get("标题", "")
    elif task_type == "service":
        return SHOP_RULES.get("售后", "")
    elif task_type == "ad":
        return SHOP_RULES.get("投放", "")
    elif task_type == "stock":
        return SHOP_RULES.get("库存", "")
    else:
        return "请遵守通用电商规范。"