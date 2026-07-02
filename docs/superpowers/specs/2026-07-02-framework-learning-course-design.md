# 框架进阶课程设计（LangChain + LangGraph）

## 背景

学习者画像（已更新）：
- **已完成**：RAG 9 课（手写 embedding→检索→切块→prompt→混合检索→改写→评估→工程化）、Agent 9 课（手写 Function Calling→ReAct→工具设计→记忆→规划→Agentic RAG→多智能体→毕业项目）
- **独特优势**：已经手写过 RAG 和 Agent 的**每一个环节**，知道框架底层在干什么——这是绝大多数候选人没有的认知深度
- **学习目标**：求职/转岗 AI 应用开发（后端岗）。把已有手写能力"翻译"成工业界主流框架（LangChain/LangGraph，JD 高频词），并理解框架的**价值边界**（什么该用框架、什么手写更清楚）
- **技术选型**：继续智谱 GLM-4 + embedding-3，复用已有向量库与样例文档
- **学习形式**：沿用渐进式课程，每课三件套（README 原理 + code.py 可运行 + exercise.md 练习）

本课程的**核心定位**：不是从零学框架，而是「**原理已懂，框架是杠杆**」。每课都把"你手写过的版本"和"框架版本"并排对比，让学习者看清：框架替你解决了哪些痛点、抽象掉了哪些细节、又在哪些地方需要你绕回手写。

## 设计原则

1. **映射对比优先**：每课开篇先回顾"你在 RAG/Agent 第 X 课手写过什么"，再用框架重写，并明确指出框架省了哪些代码、隐藏了哪些细节。这是本课程区别于市面所有框架教程的杀手锏。
2. **原理已学，聚焦取舍**：不重复讲 RAG/Agent 原理（README 里用一句话带过原理 + 链回前序课程），把篇幅集中在"框架抽象的设计意图"和"何时该用/不该用"。
3. **L01 就出成果**：第一课就用 LCEL 重写你的第一个 RAG，让学习者立刻感受到"框架真省事"。
4. **两段式结构**：LangChain 段（L01-L05）解决 RAG 工程化；LangGraph 段（L06-L09）解决 Agent 工程化——对应你已经学过的两块。
5. **毕业项目即简历作品**：L09 用 LangGraph 重写你的研究助手，做成可部署、可演示的图结构 Agent。

## 技术选型

| 组件 | 选择 | 理由 |
|------|------|------|
| 框架（RAG） | LangChain + LCEL | 业界主流，LCEL 管道语法是工程化 RAG 的事实标准 |
| 框架（Agent） | LangGraph | LangChain 官方推荐的 Agent 编排框架，图结构、状态化、可持久化，是 2024+ 生产级 Agent 首选 |
| 核心包 | langchain-core | 抽象层，Runnable 接口、LCEL 的根基 |
| 模型集成 | ChatZhipuAI（langchain-community） | 智谱 GLM-4 的官方 LangChain 封装，复用已有 API Key |
| 向量库 | Chroma（langchain-chroma） | 复用已有 Chroma 数据，对比手写 Chroma 调用 |
| 评估/可观测 | LangSmith（演示）+ 复用 L08 的 RAGAS | 让学习者看到工业级 trace/调试 |
| 部署 | LangGraph Studio（演示） | 图可视化 + 本地调试，简历加分 |

> 包路径说明：`ChatZhipuAI`、`RecursiveCharacterTextSplitter` 等的精确导入路径随版本变动，每课 code.py 顶部会注明当时验证过的版本与导入方式。

## 目录结构

```
RAG-test/
├── framework-lessons/            # 框架进阶课程（本课程）
│   ├── 01_lcel_overview/
│   ├── 02_models_prompts_parsers/
│   ├── 03_documents_splitter_vectorstore/
│   ├── 04_retrievers_rag_chain/
│   ├── 05_advanced_retrieval/
│   ├── 06_langgraph_basics/
│   ├── 07_tools_and_agents/
│   ├── 08_state_memory_hitl/
│   └── 09_capstone/
├── lessons/                      # （已完成）RAG 手写课程
├── agent-lessons/                # （已完成）Agent 手写课程
├── data/sample_docs/             # 复用已有样例文档
└── ...
```

每个课时目录统一包含三个文件（与前两门课一致）：
- `README.md` — 原理 + 映射对比（"手写版 vs 框架版"）
- `code.py` — 可运行代码，带详细中文注释
- `exercise.md` — 小练习 + 思考题

## 课时设计（共 9 节）

### 第一部分：LangChain —— RAG 工程化（L01-L05）

---

### Lesson 01 — LCEL 与框架全景：从手写拼装到管道
**目标**：建立 LangChain 生态全景认知，用 LCEL 管道语法重写你手写的 RAG，立刻体会到"省事"。

**原理 README**：
- 生态全景图：langchain-core（抽象）/ langchain（社区）/ langgraph（Agent）三者关系
- 为什么需要框架（回顾你手写 RAG 时的重复劳动：拼 prompt、串调用、处理流式）
- LCEL（LangChain Expression Language）核心：`|` 管道 + Runnable 协议
- "组件即积木"思想：每个组件都实现了 `.invoke()/.stream()/.batch()`

**code.py**：
- 用 LCEL 重写 RAG L01 的第一个 RAG（retriever | prompt | model | parser 管道）
- 对比行数：手写版 N 行 vs LCEL 版几行
- 演示 `.invoke()` / `.stream()` / `.batch()` 一键切换

**练习**：把管道里某个组件换掉，观察整体行为。

**映射**：RAG L01（第一个 RAG）。

---

### Lesson 02 — 三件套：Models + Prompts + Output Parsers
**目标**：掌握 LangChain 最核心的三个抽象，理解它们如何把"调模型"标准化。

**原理 README**：
- ChatModel 抽象：为什么 `ChatZhipuAI` 和 `ChatOpenAI` 可以互换
- PromptTemplate / ChatPromptTemplate：把你手写的 f-string 模板变成可校验、可复用、可组合的对象
- Output Parser：从手写正则提取 → `PydanticOutputParser` 结构化输出（Function Calling 另一种解法）

**code.py**：
- 对比「RAG L05 手写 messages 拼装」vs `ChatPromptTemplate`
- 用 `PydanticOutputParser` 把 GLM 的自由文本回答解析成结构化对象（对比 Agent L02 里手解 tool_calls）
- 演示 `.with_structured_output()` 一行搞定结构化

**练习**：定义一个 Pydantic 模型，让 GLM 返回结构化的"员工信息卡"。

**映射**：RAG L05（Prompt 工程）、Agent L02（Function Calling）。

---

### Lesson 03 — 文档处理：Loaders + Splitters + VectorStores
**目标**：把 RAG 的"数据进入"环节工程化，理解 LangChain 的 Document 抽象。

**原理 README**：
- `Document` 对象：`page_content` + `metadata` 的统一载体（回顾你手写的 dict + metadata）
- Document Loaders：从 Markdown/PDF/网页一键加载（对比你手写的 `open().read()`）
- Text Splitters：`RecursiveCharacterTextSplitter` 你在 RAG L04 **已经用过**！这里讲它为什么这样设计、还有哪些 Splitter
- VectorStore 抽象：`Chroma` / `FAISS` / 远程库可互换（对比你手写的 chromadb 原生调用）

**code.py**：
- 用 `TextLoader` + `RecursiveCharacterTextSplitter` + `Chroma` 重写 RAG L04 的切块入库
- 对比「手写 chromadb」vs「langchain-chroma」的 API 差异
- 演示 `from_documents()` 一行入库 + `as_retriever()` 一行变检索器

**练习**：换一个不同 chunk_size 重跑，对比入库后的检索结果。

**映射**：RAG L04（切块）、RAG L03（向量库）。

---

### Lesson 04 — Retrievers + RAG Chain
**目标**：理解 Retriever 抽象的"统一接口"价值，用 LCEL 组装完整 RAG 链。

**原理 README**：
- Retriever 抽象：`.get_relevant_documents()` 统一了所有检索方式（向量/BM25/混合/改写）
- 为什么 Retriever 比直接调 VectorStore 更"工程化"（解耦、可替换、可组合）
- 用 LCEL 组装 RAG Chain：`retriever | prompt | model | parser`
- `.with_config()` 与 RunnableConfig：可观测性的入口

**code.py**：
- 把 L03 的 Chroma 变成 Retriever
- 用 LCEL 组装完整 RAG Chain（对应 RAG L01 + L05 的全部逻辑，但代码量大幅缩减）
- 加上来源元数据透传，实现带引用的回答

**练习**：把 VectorStore 换成另一种（如 FAISS），观察 Chain 代码几乎不用改。

**映射**：RAG L01、L03、L05。

---

### Lesson 05 — 高级检索工程化：Ensemble + Rerank + Query 改写
**目标**：用框架组件把你在 RAG L06/L07 手写的高级检索"组件化"，体验框架真正省力的地方。

**原理 README**：
- `EnsembleRetriever`：向量 + BM25 混合检索（对比你手写的 RRF 融合）
- `ContextualCompressionRetriever` + `LLMChainExtractor`：LLM 二次筛选
- `MultiQueryRetriever`：多查询展开（对比你 RAG L07 手写的多查询）
- 框架做对了什么 / 没做什么（如 reranker 仍需自行接入）

**code.py**：
- 用 `EnsembleRetriever` 重写 RAG L06 的 BM25+向量混合检索
- 用 `MultiQueryRetriever` 重写 RAG L07 的多查询展开
- 对比代码量与可读性

**练习**：把 Ensemble 的权重调成你 RAG L06 练习里验证过的最优值。

**映射**：RAG L06（混合检索）、RAG L07（Query 改写）。

---

### 第二部分：LangGraph —— Agent 工程化（L06-L09）

---

### Lesson 06 — LangGraph 基础：StateGraph 重写 ReAct
**目标**：理解"图 = 状态机"的思想，用 StateGraph 重写你 Agent L03 手写的 ReAct while 循环。

**原理 README**：
- 为什么 Agent 适合用"图"建模（状态、转移、条件分支、终止）
- StateGraph 三要素：State（TypedDict）、Node（函数）、Edge（含条件边）
- 对比你 Agent L03 的 `while` 循环 vs LangGraph 的显式图——图让流程**可视化、可持久化、可恢复**
- `START` / `END`、`add_conditional_edges` 的路由

**code.py**：
- 定义 State（messages + 工具结果）
- 写 agent 节点（调模型）和 tools 节点（执行工具）
- 用条件边实现"模型要不要继续调工具"的路由
- 对比行数和可读性，体会图的"声明式"优势

**练习**：在图里加一个新节点（如"自我反思"），观察流程变化。

**映射**：Agent L03（ReAct 循环）。

---

### Lesson 07 — 框架级 Agent：Tools + prebuilt Agents
**目标**：掌握 LangChain 的工具定义方式和框架预置 Agent，对比你手写的 TOOL_REGISTRY。

**原理 README**：
- `@tool` 装饰器 / `StructuredTool`：从手写工具 schema → 自动从 docstring/类型注解生成 schema
- `create_react_agent`（LangGraph 预置）：一行创建标准 ReAct Agent
- `create_tool_calling_agent` + `AgentExecutor`（LangChain 经典）：另一种风格
- 何时用预置 / 何时自建图（呼应 Agent L04 工具设计的取舍）

**code.py**：
- 用 `@tool` 把你 Agent L04 的几个工具重新定义，对比手写 TOOLS_SPEC
- 用 `create_react_agent` 一行创建 Agent
- 对比你 Agent L03 手写循环 vs 框架预置的代码量

**练习**：把毕业项目（Agent L09）的 web_search 工具用 `@tool` 重写，接到 prebuilt Agent。

**映射**：Agent L02（Function Calling）、Agent L04（工具设计）。

---

### Lesson 08 — 状态、记忆与人机协作
**目标**：掌握 LangGraph 的状态持久化与人机协作，这是它相比手写循环的杀手锏。

**原理 README**：
- Checkpointer（`MemorySaver` / `SqliteSaver`）：状态持久化，断点恢复（对比你 Agent L05 手写的 messages 管理）
- 短期记忆（thread 内）vs 长期记忆（跨 thread / Store）
- Human-in-the-loop：`interrupt()` 让 Agent 在关键动作前等人审批（手写很难优雅实现）
- 时间旅行：回到图的某个历史节点重新执行

**code.py**：
- 给 L06 的 Agent 加 Checkpointer，实现"同一 thread 记住上下文"
- 用 `interrupt()` 实现"执行工具前先问用户确认"
- 演示跨 thread 失忆 vs 同 thread 记忆

**练习**：让 Agent 在花钱类工具调用前必须经过人工确认。

**映射**：Agent L05（记忆）。

---

### Lesson 09 — 毕业项目：LangGraph 重做研究助手 + 部署
**目标**：综合 L06-L08，用 LangGraph 把你 Agent L09 的研究助手重做成生产级图结构，并演示部署。

**原理 README**：
- 复杂图设计：多节点、并行（`Send` API）、子图（subgraph）组合
- 把你的研究助手拆成图：检索节点 → 分析节点 → 补充检索（条件回路）→ 报告生成节点
- 可观测性：LangSmith trace（演示，看每步耗时/Token/输入输出）
- 部署：LangGraph Studio 可视化调试 + 本地运行

**code.py**：
- 用 LangGraph 重写 Agent L09 的研究助手（web_search + 多轮检索 + 报告）
- 加入 L08 的记忆与中断审批（如"是否执行联网搜索"先问用户）
- 打印图结构（Mermaid），演示 Studio 可视化
- 对比手写版 vs LangGraph 版的工程化差距

**练习**：把 RAG 能力（lessons 里的知识库）作为一个工具/子图接进研究助手，形成"会查内部知识 + 会联网"的混合 Agent。

**映射**：Agent L09（毕业项目）+ Agent L07（Agentic RAG）。

## 实施说明

- **沿用前两门课的节奏**：不一次性写完 9 课。先完成 L01，让学习者跑通、确认"框架真省事"的体验 OK，再逐课推进。
- **复用资源**：`data/sample_docs/`、`.env`、智谱 API Key、已建好的 Chroma 数据全部复用，新课程不重复造数据。
- **依赖更新**：在 `requirements.txt` 末尾新增「框架进阶」分组（langchain / langchain-community / langchain-core / langgraph / langchain-chroma / pydantic 等）。
- **顶层 README**：L01 交付时更新顶层 README，加入第三门「框架进阶」课程入口。
- **不做的事**：不深入 LangChain 的每个 Loader/Retriever（够用即可）；不引入云部署（聚焦原理与本地可运行）；微调/训练不在本课程范围。

## 求职落地

学完本课程后，学习者应能在简历/面试中：
- 说清 LangChain 与 LangGraph 的分工与取舍（区分度极高的认知）
- 用 LCEL 快速组装 RAG Chain，用 LangGraph 设计状态化 Agent
- 回答"框架替你做了什么、隐藏了什么、什么时候该绕回手写"——这是高级候选人才能答的题
- 拥有一个用 LangGraph 写的、图结构、可部署的研究助手作品
