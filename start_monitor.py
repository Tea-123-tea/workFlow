"""
库存监控启动脚本
"""

import subprocess
import sys
import os

def start_monitor():
    """启动库存监控服务"""
    print("=" * 60)
    print("库存监控服务启动器")
    print("=" * 60)
    print("\n启动中...")
    print("提示: 按 Ctrl+C 可停止服务")
    print("\n")

    try:
        # 启动监控脚本
        subprocess.run([sys.executable, "stock_monitor.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n服务已停止")
    except Exception as e:
        print(f"\n启动失败: {str(e)}")

if __name__ == "__main__":
    start_monitor()