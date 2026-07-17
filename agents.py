# agents.py
from langchain_openai import ChatOpenAI  # 修改1: 改用 langchain_openai
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from tools import crawl_competitor, query_order, get_ad_data, get_stock, send_wecom_msg
from rules import get_rules

load_dotenv()


llm = ChatOpenAI(
    model="qwen3.7-plus",
    temperature=0.7,
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # 从环境变量读取
    base_url=os.environ.get("OPENAI_BASE_URL"),  # 通义千问兼容模式地址
)


# ---------- 1. 商品创作 Agent ----------
def product_agent(params: dict) -> dict:
    keyword = params.get("keyword", "未知商品")
    competitors = crawl_competitor(keyword)
    rule = get_rules("product")

    from langchain_core.messages import SystemMessage, HumanMessage
    
    messages = [
        SystemMessage(content=f"你是电商运营专家。根据竞品信息和规则生成商品标题和详情。规则：{rule}"),
        HumanMessage(content=f"关键词：{keyword}，竞品：{competitors}")
    ]
    
    response = llm.invoke(messages)
    content = response.content
    
    # 优化：提取第一行作为标题
    lines = content.strip().split('\n')
    title = lines[0][:50] if lines else "商品标题"
    
    return {
        "title": title,
        "detail": content,
        "need_human": True
    }


# ---------- 2. 投放优化 Agent ----------
def ad_agent(params: dict) -> dict:
    shop_id = params.get("shop_id", "SHOP001")
    ad_data = get_ad_data(shop_id)
    rule = get_rules("ad")
    
    from langchain_core.messages import SystemMessage, HumanMessage
    
    messages = [
        SystemMessage(content=f"你是广告优化师，根据规则调整出价。规则：{rule}"),
        HumanMessage(content=f"当前投放数据：{ad_data}")
    ]
    
    response = llm.invoke(messages)
    return {
        "suggestion": response.content,
        "need_human": False
    }


# ---------- 3. 售后工单 Agent ----------
def service_agent(params: dict) -> dict:
    order_id = params.get("order_id")
    order_info = query_order(order_id)
    if not order_info:
        return {"error": "订单不存在", "need_human": True}
    
    # 安全检查
    if len(order_info) == 0:
        return {"error": "订单数据异常", "need_human": True}
    
    amount = order_info[0].get("amount", 0)
    rule = get_rules("service")
    
    from langchain_core.messages import SystemMessage, HumanMessage
    
    messages = [
        SystemMessage(content=f"你是售后专员，按规则处理。规则：{rule}"),
        HumanMessage(content=f"订单信息：{order_info}")
    ]
    
    response = llm.invoke(messages)
    return {
        "result": response.content,
        "need_human": amount > 200
    }


# ---------- 4. 差评处理 Agent ----------
def comment_agent(params: dict) -> dict:
    comment_text = params.get("comment", "")
    
    from langchain_core.messages import SystemMessage, HumanMessage
    
    messages = [
        SystemMessage(content="你是舆情客服，分析差评情绪，生成安抚话术。"),
        HumanMessage(content=f"差评内容：{comment_text}")
    ]
    
    response = llm.invoke(messages)
    need_human = "严重" in comment_text or "投诉" in comment_text
    return {
        "reply": response.content,
        "need_human": need_human
    }


# ---------- 5. 库存管理 Agent ----------
def stock_agent(params: dict) -> dict:
    product_id = params.get("product_id")
    stock = get_stock(product_id)
    rule = get_rules("stock")
    if stock < 50:
        suggestion = f"库存仅剩{stock}件，建议立即补货。"
        send_wecom_msg(f"⚠️ 预警：商品{product_id}库存{stock}低于50")
    else:
        suggestion = f"库存充足（{stock}件），无需操作。"
    return {
        "stock": stock,
        "suggestion": suggestion,
        "need_human": False
    }


# 导出映射，方便路由调用
AGENT_MAP = {
    "product": product_agent,
    "ad": ad_agent,
    "service": service_agent,
    "comment": comment_agent,
    "stock": stock_agent,
}