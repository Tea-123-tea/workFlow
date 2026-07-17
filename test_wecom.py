"""
企业微信机器人推送测试脚本(支持应用机器人方式)
用于验证Bot ID和Secret配置是否正确
"""

import os
import sys
import requests
from dotenv import load_dotenv

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def test_wecom_bot_config():
    """测试企业微信应用机器人配置"""

    bot_id = os.getenv("WECOM_BOT_ID")
    bot_secret = os.getenv("WECOM_BOT_SECRET")
    webhook = os.getenv("WECOM_WEBHOOK")

    print("=" * 60)
    print("企业微信机器人配置检查")
    print("=" * 60)

    # 检查配置类型
    if webhook:
        print("[OK] 检测到Webhook配置(群机器人)")
        print(f"   Webhook: {webhook}")
        return "webhook"
    elif bot_id and bot_secret:
        print("[OK] 检测到应用机器人配置")
        print(f"   Bot ID: {bot_id}")
        print(f"   Secret: {bot_secret[:10]}...")  # 只显示前10位
        return "app"
    else:
        print("[ERROR] 未检测到任何企业微信机器人配置")
        print("\n请在 .env 文件中配置以下之一:")
        print("方式1(群机器人): WECOM_WEBHOOK='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx'")
        print("方式2(应用机器人): WECOM_BOT_ID='xxx' 和 WECOM_BOT_SECRET='xxx'")
        return None

def test_simple_push():
    """测试简单推送方式(直接使用Bot ID作为key)"""
    bot_id = os.getenv("WECOM_BOT_ID")

    print("\n" + "=" * 60)
    print("方式1: 简单推送(直接使用Bot ID)")
    print("=" * 60)

    if not bot_id:
        print("[ERROR] 未配置Bot ID")
        return False

    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_id}"
    print(f"推送URL: {url}")

    payload = {
        "msgtype": "text",
        "text": {
            "content": "测试消息(简单方式)\n\n这是使用Bot ID直接推送的测试消息。"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get("errcode") == 0:
                print("[SUCCESS] 简单推送成功!")
                print("   请检查企业微信是否收到消息")
                return True
            else:
                print(f"[ERROR] 简单推送失败: {result.get('errmsg')}")
                print(f"   错误码: {result.get('errcode')}")
                return False
        else:
            print(f"[ERROR] HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 推送异常: {str(e)}")
        return False

def test_token_push():
    """测试获取token后推送"""
    from tools import get_wecom_token

    print("\n" + "=" * 60)
    print("方式2: Token方式推送")
    print("=" * 60)

    print("正在获取access_token...")
    token = get_wecom_token()

    if not token:
        print("[ERROR] 无法获取access_token")
        print("   可能原因:")
        print("   1. Bot ID或Secret配置错误")
        print("   2. 网络连接问题")
        print("   3. 企业微信API不支持该机器人类型")
        return False

    print(f"[OK] 成功获取token: {token[:20]}...")

    bot_id = os.getenv("WECOM_BOT_ID")
    url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={bot_id}&access_token={token}"

    payload = {
        "msgtype": "text",
        "text": {
            "content": "测试消息(Token方式)\n\n这是通过获取access_token后推送的测试消息。"
        }
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get("errcode") == 0:
                print("[SUCCESS] Token推送成功!")
                print("   请检查企业微信是否收到消息")
                return True
            else:
                print(f"[ERROR] Token推送失败: {result.get('errmsg')}")
                return False
        else:
            print(f"[ERROR] HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] 推送异常: {str(e)}")
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
    print("   如果推送失败,控制台会显示错误信息")

if __name__ == "__main__":
    # 步骤1: 检查配置
    config_type = test_wecom_bot_config()

    if config_type == "webhook":
        print("\n提示: 你配置的是群机器人(Webhook方式)")
        print("      请运行前端测试验证推送功能")
    elif config_type == "app":
        # 步骤2: 测试简单推送
        simple_success = test_simple_push()

        # 步骤3: 如果简单推送失败,尝试token方式
        if not simple_success:
            print("\n简单推送失败,尝试Token方式...")
            token_success = test_token_push()

            if not token_success:
                print("\n" + "=" * 60)
                print("[ERROR] 所有推送方式均失败")
                print("=" * 60)
                print("\n可能的原因:")
                print("1. Bot ID或Secret配置错误")
                print("2. 该机器人不支持外部推送")
                print("3. 需要在企业微信管理后台启用机器人推送功能")
                print("\n建议:")
                print("- 使用群机器人(Webhook方式)更简单可靠")
                print("- 联系企业微信管理员确认机器人配置")
        else:
            # 步骤4: 测试库存预警
            test_stock_alert()
    else:
        print("\n请先配置企业微信机器人信息")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)