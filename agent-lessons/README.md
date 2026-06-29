# Agent 渐进式学习课程 🤖

这是一套**从零开始、系统理解 AI Agent 原理**的实战课程。
面向已学完 RAG 课程、会 Python 的开发者，用**原理优先**的方式带你从"大模型只会聊天"走到"Agent 自主完成任务"。

> 技术栈：智谱 GLM-4（原生 function calling）· 纯 Python 手写 Agent loop · 与 RAG 课程共用环境
> **原理优先**：关键环节先手写一遍（如 ReAct 循环），再看框架——这是求职面试的核心卖点。

---

## 🗺️ 学习路径（共 9 节课）

按 Agent 能力进阶排列：单工具调用 → ReAct 循环 → 多工具 → 记忆 → 规划 → Agentic RAG → 多 Agent → 毕业项目。

| # | 课程 | 你会学到 |
|---|------|----------|
| 01 | [认识 Agent：从问答到行动](01_what_is_agent/) | Agent 三要素、跑通最小 Agent |
| 02 | [Function Calling 深入](02_function_calling/) | 工具定义、参数解析、工具调度器 |
| 03 | [ReAct 循环（面试核心）](03_react_loop/) | 手写 Thought→Action→Observation 循环 |
| 04 | [多工具与工具设计](04_tool_design/) | 好工具的特征、工具选择难题 |
| 05 | [记忆：记住上下文](05_memory/) | 短期/长期记忆、窗口管理 |
| 06 | [规划与任务分解](06_planning/) | CoT、Plan-and-Execute |
| 07 | [Agentic RAG](07_agentic_rag/) | 把 RAG 包装成工具（衔接 RAG 课程）|
| 08 | [多智能体协作](08_multi_agent/) | 角色分工、Agent 间通信 |
| 09 | [毕业项目：智能研究助手](09_capstone/) | 综合应用，简历级项目 |

---

## 🚀 快速开始

本课程与 RAG 课程共用环境，如果你已经跑通过 RAG 课程，直接开始：

```bash
# 1. 激活环境（RAG 课程已配好）
conda activate rag-learn
# 或直接用项目 venv：& "D:\workspace\RAG-test\.venv\Scripts\python.exe"

# 2. 确认 .env 里有智谱 API Key（RAG 课程已配）

# 3. 跑第一课
python agent-lessons/01_what_is_agent/code.py
```

> 💰 **省钱**：把代码里 `CHAT_MODEL = "glm-4"` 改成 `"glm-4-flash"`（免费，且支持 function calling）。

---

## 📁 目录结构

```
RAG-test/
├── lessons/           ← RAG 课程（已完成）
├── agent-lessons/     ← Agent 课程（你在这里）
│   ├── README.md      ← 课程总览
│   └── 01_what_is_agent/
│       ├── README.md  ← 原理讲解
│       ├── code.py    ← 可运行代码
│       └── exercise.md ← 练习
├── data/ .env requirements.txt  ← 与 RAG 课程共用
└── docs/              ← 设计文档
```

---

## 💡 学习建议

- **按顺序学**，每课建立在前一课之上（尤其 L03 ReAct 是后面所有课的基础）
- **原理优先**：手写 Agent loop 的过程比直接用框架学到的多得多，面试也更有底气
- 跑完每课的代码后，一定要做练习——改工具、调参数，看 Agent 怎么变
- **求职重点**：L03（ReAct）、L07（Agentic RAG）、L09（毕业项目）是面试和简历的核心
