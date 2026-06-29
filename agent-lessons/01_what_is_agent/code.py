"""
L01 — 认识 Agent：从问答到行动
================================
本脚本跑通一个最小 Agent，让你看清 Agent 的工作过程：
    用户提问 → LLM 决定调用工具 → 执行工具 → 结果喂回 LLM → 最终回答

给 Agent 配两个工具：
    - get_current_time：获取当前时间（LLM 自己不知道"现在"）
    - calculator：做数学计算（LLM 自己算不准）

运行：python agent-lessons/01_what_is_agent/code.py
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from dotenv import load_dotenv
from zhipuai import ZhipuAI

CHAT_MODEL = "glm-4"  # 想免费可换 "glm-4-flash"


def create_client() -> ZhipuAI:
    """从 .env 读 Key，创建智谱客户端。"""
    load_dotenv()
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key or api_key.startswith("xxxx"):
        raise RuntimeError(
            "还没配置 API Key！请把 .env.example 复制成 .env，填入真实 ZHIPUAI_API_KEY。"
        )
    return ZhipuAI(api_key=api_key)


# ════════════════════════════════════════════════════════════
# 第 1 步：定义工具（真正的 Python 函数）
# ════════════════════════════════════════════════════════════
# 这些是 Agent 的"手脚"——LLM 自己做不到的事，靠这些函数完成。


def get_current_time() -> str:
    """获取当前时间。"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def calculator(expression: str) -> str:
    """计算数学表达式。

    ⚠️ 生产环境绝不能用 eval 直接算用户输入（有安全风险）！
    这里为了教学简洁用 eval，真实项目用 ast.literal_eval 或专门的计算库。
    """
    try:
        # 只允许数字和基本运算符，做最基础的安全过滤
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "错误：表达式包含非法字符"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"


# ════════════════════════════════════════════════════════════
# 第 2 步：把工具"告诉"大模型（tools 定义）
# ════════════════════════════════════════════════════════════
# tools 是一个列表，每个工具用 JSON Schema 描述：
#   - name：函数名（LLM 用这个名字调用）
#   - description：干什么用的（LLM 靠这个判断"该不该用这个工具"）
#   - parameters：需要什么参数（类型、说明）
# 💡 description 非常关键！写得越清楚，LLM 选工具越准（L04 会专门讲）

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间。当用户问'现在几点''今天日期'等需要实时时间的问题时使用。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式。当需要精确计算加减乘除时使用。expression 是数学表达式字符串，如 '12 * 34'。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，如 '3 * (4 + 5)'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
]


# ════════════════════════════════════════════════════════════
# 第 3 步：工具调度器（根据 LLM 的决策，执行真正的函数）
# ════════════════════════════════════════════════════════════
def execute_function(name: str, arguments: dict) -> str:
    """根据函数名和参数，执行对应的 Python 函数，返回结果字符串。"""
    if name == "get_current_time":
        return get_current_time()
    elif name == "calculator":
        return calculator(arguments.get("expression", ""))
    else:
        return f"未知函数：{name}"


# ════════════════════════════════════════════════════════════
# 第 4 步：Agent 的核心——决策循环
# ════════════════════════════════════════════════════════════
def run_agent(client: ZhipuAI, user_question: str, max_steps: int = 5):
    """运行 Agent：处理用户问题，自主调用工具直到给出最终答案。

    这就是一个最简的 Agent 循环（L03 会把它抽象成完整的 ReAct loop）：
        1. 把用户问题发给 LLM（附带可用工具）
        2. 如果 LLM 要调用工具 → 执行工具 → 把结果喂回去 → 回到 1
        3. 如果 LLM 直接给答案 → 结束
    """
    # messages 记录整个对话历史（包括工具调用和结果）
    messages = [{"role": "user", "content": user_question}]

    for step in range(1, max_steps + 1):
        print(f"\n{'─' * 50}")
        print(f"🔄 Agent 第 {step} 步")

        # 调 LLM，告诉它有哪些工具可用
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",  # auto = 让 LLM 自己决定要不要用工具
        )
        msg = response.choices[0].message

        # 情况 A：LLM 决定调用工具
        if msg.tool_calls:
            # 先把 LLM 的这一轮回复（含工具调用请求）记进历史
            messages.append(msg.model_dump())
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                print(f"🤔 Agent 决定调用工具：{func_name}({func_args})")

                # 执行真正的函数
                result = execute_function(func_name, func_args)
                print(f"🔧 工具返回：{result}")

                # 把工具结果喂回给 LLM（role="tool"）
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )
            # 继续下一轮循环（LLM 会看到工具结果，再决定下一步）

        # 情况 B：LLM 直接给答案（不调用工具）
        else:
            print(f"💬 Agent 最终回答：\n{msg.content}")
            return msg.content

    print("⚠️ 达到最大步数，Agent 被迫停止。")
    return None


# ════════════════════════════════════════════════════════════
# 主流程：跑两个问题看 Agent 怎么"行动"
# ════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("L01 — 认识 Agent：从问答到行动")
    print("=" * 60)

    client = create_client()

    # 问题 1：只需一个工具（查时间）
    print("\n\n" + "═" * 60)
    print("问题 1：现在几点了？")
    print("═" * 60)
    run_agent(client, "现在几点了？")

    # 问题 2：需要两个工具配合（先查时间，再算差值）
    print("\n\n" + "═" * 60)
    print("问题 2：现在是几点？距离今天 18:00 还有多少分钟？")
    print("═" * 60)
    run_agent(client, "现在是几点？距离今天 18:00 还有多少分钟？（请用计算器算）")

    # 问题 3：不需要工具（看 Agent 会不会跳过工具）
    print("\n\n" + "═" * 60)
    print("问题 3：请用一句话介绍你自己（不需要工具）")
    print("═" * 60)
    run_agent(client, "请用一句话介绍你自己。")

    print("\n" + "=" * 60)
    print("完成！你刚刚看到了一个 Agent 的工作过程。")
    print("核心：LLM 负责'决定'，代码负责'执行'，两者循环协作。")
    print("=" * 60)


if __name__ == "__main__":
    main()
