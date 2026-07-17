"""
企业微信Webhook推送测试脚本
用于验证Webhook配置是否正确
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_webhook():
    """测试企业微信Webhook推送"""

    webhook = os.getenv("WECOM_WEBHOOK")

    print("=" * 60)
    print("企业微信Webhook推送测试")
    print("=" * 60)

    if not webhook:
        print("[ERROR] 未配置WECOM_WEBHOOK")
        print("请在.env文件中添加:")
        print("WECOM_WEBHOOK='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx'")
        return False

    print(f"[OK] Webhook已配置")
    print(f"     地址: {webhook}")

    # 发送测试消息
    print("\n正在发送测试消息...")
    try:
        payload = {
            "msgtype": "text",
            "text": {
                "content": "测试消息 - 库存预警系统配置成功!\n\n如果你收到这条消息,说明企业微信机器人已正常工作。"
            }
        }

        response = requests.post(webhook, json=payload, timeout=5)

        if response.status_code == 200:
            result = response.json()
            if result.get("errcode") == 0:
                print("[SUCCESS] 消息发送成功!")
                print("         请检查企业微信群是否收到消息")
                return True
            else:
                print(f"[ERROR] 发送失败: {result.get('errmsg')}")
                print(f"        错误码: {result.get('errcode')}")
                return False
        else:
            print(f"[ERROR] HTTP错误: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print("[ERROR] 请求超时,请检查网络连接")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 网络错误: {str(e)}")
        return False

def test_stock_alert():
    """测试库存预警推送"""
    from tools import send_wecom_msg

    print("\n" + "=" * 60)
    print("库存预警推送测试")
    print("=" * 60)

    print("\n模拟商品P001库存42件(低于50)...")
    send_wecom_msg("预警:商品P001库存42低于50")

    print("\n提示:")
    print("   如果推送成功,企业微信应该收到预警消息")

if __name__ == "__main__":
    # 测试Webhook推送
    success = test_webhook()

    if success:
        # 测试库存预警
        test_stock_alert()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)