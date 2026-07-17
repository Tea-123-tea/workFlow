"""
库存监控定时任务
每1分钟扫描所有库存,低于50自动推送企业微信预警
"""

import sqlite3
import time
import logging
from datetime import datetime
from tools import send_wecom_msg

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

DB_PATH = "./ecom_shop.db"
LOW_STOCK_THRESHOLD = 50  # 库存预警阈值
SCAN_INTERVAL = 60  # 扫描间隔(秒)
ALERT_INTERVAL = 60**60*2  # 预警推送间隔(秒), 默认2小时

# 记录上次推送时间,用于降频推送
last_alert_time = {}  # {product_id: 上次推送时间戳}

def get_all_products():
    """查询所有商品信息"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, name, stock FROM product")
        products = cursor.fetchall()
        conn.close()
        return products
    except Exception as e:
        logger.error(f"查询商品失败: {str(e)}")
        return []

def scan_stock():
    """扫描库存并推送预警"""
    logger.info("=" * 60)
    logger.info(f"开始扫描库存 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    products = get_all_products()

    if not products:
        logger.warning("未查询到商品信息")
        return

    alert_count = 0

    for product_id, name, stock in products:
        try:
            stock = int(stock)
            current_time = time.time()

            # 判断库存是否低于阈值
            if stock < LOW_STOCK_THRESHOLD:
                # 检查是否到达推送间隔(降频推送)
                last_time = last_alert_time.get(product_id, 0)
                time_since_last = current_time - last_time

                if time_since_last >= ALERT_INTERVAL:
                    # 推送预警消息
                    message = f"⚠️ 库存预警\n\n商品ID: {product_id}\n商品名称: {name}\n当前库存: {stock}件\n\n库存已低于安全阈值({LOW_STOCK_THRESHOLD}件),请及时补货!"

                    send_wecom_msg(message)
                    last_alert_time[product_id] = current_time

                    logger.warning(f"[预警] 商品 {name}({product_id}) 库存{stock}件,已推送预警")
                    alert_count += 1
                else:
                    remaining = int(ALERT_INTERVAL - time_since_last)
                    logger.info(f"[等待中] 商品 {name}({product_id}) 库存{stock}件,距离下次推送还需{remaining}秒")
            else:
                # 库存恢复正常,清除推送记录
                if product_id in last_alert_time:
                    del last_alert_time[product_id]
                    logger.info(f"[恢复正常] 商品 {name}({product_id}) 库存{stock}件")

        except Exception as e:
            logger.error(f"处理商品 {product_id} 时出错: {str(e)}")

    logger.info(f"扫描完成 - 共{len(products)}个商品, {alert_count}个预警")
    logger.info(f"下次扫描时间: {SCAN_INTERVAL}秒后")

def run_monitor():
    """运行库存监控"""
    logger.info("=" * 60)
    logger.info("库存监控服务启动")
    logger.info(f"扫描间隔: {SCAN_INTERVAL}秒")
    logger.info(f"预警阈值: {LOW_STOCK_THRESHOLD}件")
    logger.info("=" * 60)

    try:
        while True:
            scan_stock()
            time.sleep(SCAN_INTERVAL)
    except KeyboardInterrupt:
        logger.info("收到停止信号,监控服务已停止")
    except Exception as e:
        logger.error(f"监控服务异常: {str(e)}")

if __name__ == "__main__":
    run_monitor()