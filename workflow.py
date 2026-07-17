from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents import AGENT_MAP

class EcomState(TypedDict):
    task_type: str
    input_params: dict
    agent_output: dict
    need_human: bool
    final_msg: str

# 路由节点：根据 task_type 决定走哪个 Agent
def router(state: EcomState):
    task = state["task_type"]
    if task not in AGENT_MAP:
        state["final_msg"] = f"不支持的任务类型：{task}"
        state["need_human"] = False
        return state
    # 直接调用对应的 agent 函数（也可以放在子节点，这里为简化直接调用）
    agent_func = AGENT_MAP[task]
    result = agent_func(state["input_params"])
    state["agent_output"] = result
    state["need_human"] = result.get("need_human", False)
    state["final_msg"] = "处理完成"
    return state

# 结束节点：汇总信息
def finish(state: EcomState):
    if state["need_human"]:
        state["final_msg"] = "⏸️ 任务已暂停，等待人工审核"
    else:
        state["final_msg"] = "✅ 任务自动完成，结果已生成"
    return state

# 构建图
workflow = StateGraph(EcomState)
workflow.add_node("router", router)
workflow.add_node("finish", finish)

workflow.set_entry_point("router")
workflow.add_edge("router", "finish")
workflow.add_edge("finish", END)

ecom_app = workflow.compile()