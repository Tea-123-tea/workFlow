import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "./ecom_shop.db"

# 1. 模拟竞品爬虫（根据关键词生成假数据）
def crawl_competitor(keyword: str):
    return [
        {"title": f"{keyword} 夏季爆款透气款", "price": 59.9, "tags": ["纯棉", "显瘦"]},
        {"title": f"{keyword} 宽松百搭学生款", "price": 49.9, "tags": ["平价", "大码"]}
    ]

# 2. 查询订单详情
def query_order(order_id: str):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT * FROM orders WHERE order_id='{order_id}'", conn)
    conn.close()
    return df.to_dict("records")

# 3. 模拟广告投放数据
def get_ad_data(shop_id: str):
    return {"消耗": 1200, "点击量": 2300, "成交订单": 116, "ROI": 3.45}

# 4. 查询库存
def get_stock(product_id: str):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(f"SELECT stock FROM product WHERE product_id='{product_id}'", conn)
    conn.close()
    if len(df) == 0:
        return 0
    return int(df.iloc[0, 0])

# 5. 更新库存（模拟）
def update_stock(product_id: str, new_stock: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE product SET stock=? WHERE product_id=?", (new_stock, product_id))
    conn.commit()
    conn.close()
    return f"库存已更新为 {new_stock}"

# 6. 发送企业微信消息(使用Webhook方式)
import requests

def send_wecom_msg(content: str):
    """发送企业微信消息"""
    webhook = os.getenv("WECOM_WEBHOOK")

    if not webhook:
        print(f"[模拟推送] {content}")
        return "模拟推送完成"

    try:
        payload = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        response = requests.post(webhook, json=payload, timeout=5)

        if response.status_code == 200:
            result = response.json()
            if result.get("errcode") == 0:
                print(f"[企业微信推送成功] 消息已发送")
                return "消息推送完成"
            else:
                print(f"[推送失败] {result.get('errmsg', '未知错误')}")
                return "推送失败"
        else:
            print(f"[HTTP错误] 状态码: {response.status_code}")
            return "推送失败"
    except Exception as e:
        print(f"[推送异常] {str(e)}")
        return "推送失败"