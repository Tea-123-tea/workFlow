from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from workflow import ecom_app
import traceback
import logging
import threading
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 库存监控控制标志
monitor_thread = None
monitor_running = False

app = FastAPI(title="电商多智能体工作流")

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源，生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],   # 允许所有 HTTP 方法
    allow_headers=["*"],   # 允许所有请求头
)

class TaskRequest(BaseModel):
    task_type: str
    input_params: dict

# 库存监控相关函数
def run_stock_monitor():
    """库存监控线程函数"""
    global monitor_running

    # 导入监控函数
    from stock_monitor import scan_stock, LOW_STOCK_THRESHOLD, SCAN_INTERVAL

    logger.info("📦 库存监控线程已启动")

    while monitor_running:
        try:
            scan_stock()
            time.sleep(SCAN_INTERVAL)
        except Exception as e:
            logger.error(f"库存监控异常: {str(e)}")
            time.sleep(60)  # 发生错误时等待1分钟后继续

    logger.info("📦 库存监控线程已停止")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    global monitor_thread, monitor_running

    logger.info("🚀 应用启动中...")

    # 启动库存监控线程
    monitor_running = True
    monitor_thread = threading.Thread(target=run_stock_monitor, daemon=True)
    monitor_thread.start()

    logger.info("✅ 库存监控服务已自动启动")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    global monitor_running

    logger.info("🛑 应用关闭中...")

    # 停止库存监控线程
    monitor_running = False

    logger.info("✅ 库存监控服务已停止")

@app.post("/run")
def run_task(req: TaskRequest):
    logger.info(f"📥 收到请求: task_type={req.task_type}, params={req.input_params}")
    
    try:
        initial_state = {
            "task_type": req.task_type,
            "input_params": req.input_params,
            "agent_output": {},
            "need_human": False,
            "final_msg": ""
        }
        
        logger.info("🚀 开始执行工作流...")
        result = ecom_app.invoke(initial_state)
        logger.info(f"✅ 工作流完成")
        
        return result
        
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.error(f"❌ 任务失败: {str(e)}")
        logger.error(f"📄 详细堆栈:\n{error_detail}")
        
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "detail": error_detail
            }
        )

@app.get("/")
def root():
    return {
        "message": "电商多智能体工作流 API",
        "docs": "http://127.0.0.1:8000/docs",
        "status": "running"
    }

@app.get("/monitor/status")
def get_monitor_status():
    """获取库存监控状态"""
    return {
        "monitor_running": monitor_running,
        "monitor_thread_alive": monitor_thread.is_alive() if monitor_thread else False,
        "status": "running" if monitor_running else "stopped"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)