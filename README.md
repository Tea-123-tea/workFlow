# 电商多智能体自动化工作流系统

基于LangGraph 构建的电商运营多智能体系统，实现商品创作、投放优化、售后工单、差评处理、库存管理五类 Agent 的自主决策与协作。通过工具调用与状态管理机制，使 Agent 能够感知环境、调用外部 API、执行数据库操作，自动化完成复杂业务流程。

## 功能特性

### 五大核心 Agent

- **商品创作 Agent**：爬取竞品信息，调用 LLM 生成商品标题与详情
- **投放优化 Agent**：分析广告数据，根据 ROI 规则给出出价建议
- **售后工单 Agent**：查询订单信息，按规则处理售后申请，高金额需人工审核
- **差评处理 Agent**：分析差评情绪，生成安抚话术，严重投诉转人工
- **库存管理 Agent**：监控库存状态，低于阈值自动推送企业微信预警

### 自动化库存监控

- 后台轮询服务，每 1 分钟扫描全量商品库存
- 降频推送策略：首次预警后 2 小时内不重复提醒
- 企业微信 Webhook 集成，实时推送预警消息
- 守护线程管理，随主服务启停

### LangGraph 工作流编排

- 状态图工作流设计，支持条件边路由
- 意图识别自动分发任务至对应 Agent
- 跨节点状态传递，确保多 Agent 间信息一致性

## 技术栈

- **框架**：LangGraph、LangChain
- **LLM**：通义千问（DashScope API）
- **后端**：FastAPI、Uvicorn
- **数据库**：SQLite
- **推送**：企业微信 Webhook
- **前端**：原生 HTML/CSS/JS

## 项目结构

```
WorkFlow/
├── main.py              # FastAPI 应用入口，启动服务和库存监控
├── workflow.py          # LangGraph 状态图工作流定义
├── agents.py            # 5 个 Agent 实现（商品、投放、售后、差评、库存）
├── tools.py             # 外部工具封装（数据库查询、企业微信推送等）
├── rules.py             # 业务规则配置
├── stock_monitor.py     # 库存监控定时任务
├── init_db.py           # 数据库初始化脚本
├── test_ui.html         # 前端测试界面
├── ecom_shop.db         # SQLite 数据库
├── .env                 # 环境变量配置
└── requirements.txt     # Python 依赖
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# 通义千问 API 配置
OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_API_KEY="your_api_key_here"

# 企业微信 Webhook
WECOM_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key_here"
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 启动服务

```bash
python main.py
```

服务启动后：
- API 服务：http://127.0.0.1:8000
- API 文档：http://127.0.0.1:8000/docs
- 前端界面：直接打开 `test_ui.html`

## 核心模块说明

### LangGraph 工作流（workflow.py）

```python
# 状态定义
class EcomState(TypedDict):
    task_type: str        # 任务类型
    input_params: dict    # 输入参数
    agent_output: dict    # Agent 输出
    need_human: bool      # 是否需人工审核
    final_msg: str        # 最终消息

# 图结构
Entry → router → finish → END
```

### Agent 执行流程

```python
def xxx_agent(params: dict) -> dict:
    # 1. 获取参数
    param = params.get("xxx")

    # 2. 调用工具
    data = tool_xxx(param)

    # 3. 获取规则
    rule = get_rules("xxx")

    # 4. 调用 LLM
    messages = [SystemMessage(...), HumanMessage(...)]
    response = llm.invoke(messages)

    # 5. 返回结果
    return {"result": response.content, "need_human": False/True}
```

### 库存监控机制

```python
# 降频推送策略
ALERT_INTERVAL = 2 * 60 * 60  # 2小时
last_alert_time = {}  # 记录上次推送时间

# 扫描逻辑
if stock < 50:
    if time_since_last >= ALERT_INTERVAL:
        send_wecom_msg(message)
        last_alert_time[product_id] = current_time
```

## API 文档

### POST /run

提交任务给 Agent 执行

**请求体**：
```json
{
  "task_type": "stock",      // product | ad | service | comment | stock
  "input_params": {
    "product_id": "P001"     // 根据任务类型不同参数不同
  }
}
```

**响应**：
```json
{
  "task_type": "stock",
  "agent_output": {
    "stock": 42,
    "suggestion": "库存仅剩42件，建议立即补货。"
  },
  "need_human": false,
  "final_msg": "✅ 任务自动完成，结果已生成"
}
```

### GET /monitor/status

查询库存监控服务状态

**响应**：
```json
{
  "monitor_running": true,
  "monitor_thread_alive": true,
  "status": "running"
}
```

## 测试说明

### 测试数据

| 商品 ID | 名称 | 库存 |
|--------|------|------|
| P001 | 纯棉短袖T恤 | 42（低于50，触发预警） |
| P002 | 冰丝牛仔裤 | 12（低于50，触发预警） |

| 订单 ID | 商品 | 金额 | 问题 |
|--------|------|------|------|
| OD2026001 | P001 | 269元 | 衣服有破损 |
| OD2026002 | P002 | 99元 | 尺码偏小 |

### 测试用例

```bash
# 1. 查询库存
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task_type": "stock", "input_params": {"product_id": "P001"}}'

# 2. 处理售后
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task_type": "service", "input_params": {"order_id": "OD2026001"}}'

# 3. 商品创作
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"task_type": "product", "input_params": {"keyword": "夏季短袖"}}'
```

## 配置参数

### 库存监控参数（stock_monitor.py）

```python
LOW_STOCK_THRESHOLD = 50      # 库存预警阈值
SCAN_INTERVAL = 60            # 扫描间隔（秒）
ALERT_INTERVAL = 2 * 60 * 60  # 预警推送间隔（秒）
```

### 业务规则（rules.py）

```python
SHOP_RULES = {
    "标题": "禁止使用极限词（最、第一、顶级、全网最低）",
    "售后": "签收7天内可退换，质量问题包邮，个人原因买家自理运费",
    "投放": "ROI低于2.5时降低出价10%，ROI高于4时可加价扩量",
    "库存": "单品库存低于50件自动触发采购提醒",
}
```

## 扩展指南

### 添加新 Agent

1. 在 `agents.py` 中实现新 Agent 函数
2. 在 `AGENT_MAP` 中添加映射
3. 在 `rules.py` 中添加对应规则（可选）
4. 工作流自动支持新 Agent

### 添加新工具

1. 在 `tools.py` 中实现工具函数
2. 在对应 Agent 中调用
3. LLM 可通过 Function Calling 自主调用

## 许可证

MIT License