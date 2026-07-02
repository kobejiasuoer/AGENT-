# Lesson 01 — LCEL 与框架全景：从手写拼装到管道

> **本课定位**：你已经手写过完整 RAG（`lessons/01_getting_started`）。现在用 LangChain 的 LCEL 管道语法**重写同一个 RAG**，亲眼看见「框架替你做了什么、省了多少代码」。

---

## 一、先回顾：你手写 RAG 时做了什么？

打开 `lessons/01_getting_started/code.py`，你的主流程是：

```
问题 → embed_texts() → collection.query() → 自己拼 f-string prompt → client.chat.completions.create()
```

为了把这条链跑通，你**手动**做了 5 件事：

| 步骤 | 手写代码 | 痛点 |
|------|----------|------|
| 1. 算 embedding | `client.embeddings.create()` | 每次都要手写、手排序 |
| 2. 检索 | `collection.query(query_embeddings=...)` | 返回结构要手动剥层（`results["documents"][0]`） |
| 3. 拼 prompt | f-string 拼接 | 改格式要重写字符串，没法复用 |
| 4. 调模型 | `client.chat.completions.create(messages=[...])` | messages 结构要手维护 |
| 5. 提取答案 | `response.choices[0].message.content` | 不同 SDK 字段名不同 |

**核心痛点**：每一步都靠你手写"胶水代码"把上一步的输出"塞"进下一步。如果中间想插入一步（比如加个重排序），就得重写整个串联逻辑。

**框架要解决的就是这件事。**

---

## 二、LangChain 生态全景（2025 重构后）

LangChain 在 2024-2025 经历了一次大重构（1.x 时代）。先看清它的包结构：

```
langchain-core      ← 所有抽象的根基（Runnable 接口、Prompt、Message）
       ↑
langchain           ← 主包，提供 chain、agent 等编排能力
langgraph           ← Agent 专用，用"图"建模（L06 起会用）
       ↑
langchain-community ← 各家模型/向量库的集成（⚠️ 正在被 sunset，见下文）
langchain-chroma    ← Chroma 的独立集成包（新写法）
```

### ⚠️ 一个关键背景：`langchain-community` 正在 sunset

你运行本课代码时会看到一个 `DeprecationWarning`：

```
`langchain-community` is being sunset and is no longer actively maintained.
```

**这不是 bug，是真实的行业变迁**：LangChain 官方正在把原来塞在一个大包里的几百个集成，拆成独立的、各家自己维护的小包（`langchain-chroma`、`langchain-openai`、未来的 `langchain-zhipuai`……）。

我们这门课的策略：
- **当前能跑通的方式**：智谱的 `ChatZhipuAI` 目前仍主要在 `langchain-community` 里，本课先用它（注释里会标注迁移方向）。
- **已经迁移的部分**：Chroma 已经有独立包 `langchain-chroma`，我们直接用新的。
- **教学价值**：理解"框架的集成层在不断迁移"这件事本身，就是工程师必备的认知。

> 面试加分点：能说清 `langchain-core` / `langchain` / `langgraph` / 各 `langchain-xxx` 独立包的分工，比只会 `import langchain` 的候选人强一截。

---

## 三、LCEL（LangChain Expression Language）核心

LCEL 是 LangChain 的管道语法。**一句话理解**：用 `|` 把组件串起来，就像 Unix 管道 `cat file | grep x | sort`。

### 1. Runnable 协议 —— 一切皆可管道

LCEL 的根基是 `Runnable` 接口。**每个组件都实现了这套方法**：

| 方法 | 作用 | 你手写时对应的操作 |
|------|------|-------------------|
| `.invoke(x)` | 跑一次，返回完整结果 | 函数调用 `f(x)` |
| `.stream(x)` | 流式返回（一个 token 一个 token） | 手写 yield / SSE |
| `.batch([x1,x2])` | 批量并发跑 | 手写线程池/asyncio |

**这就是 LCEL 最妙的地方**：你用 `|` 串好的链，自动就拥有了 `invoke/stream/batch` 三种能力，不用为流式重写一遍代码。

回顾你 RAG L05 手写流式输出时，专门写了 `stream=True` 的循环 + 逐 chunk 拼接——在 LCEL 里，`.stream()` 直接就能用。

### 2. 管道语法 `|`

```python
chain = prompt | model | parser
result = chain.invoke({"question": "..."})
```

`|` 做的事：把左边组件的输出，作为右边组件的输入。等价于手写：

```python
# 手写等价物
step1 = prompt.format(question="...")      # → 一段 prompt 文本
step2 = model.invoke(step1)                 # → 一个 message 对象
step3 = parser.invoke(step2)                # → 一段纯文本
```

`|` 帮你省掉的就是这三步之间的"手动塞"。

### 3. 数据在管道里怎么流动？

关键规则：**前一个组件的输出类型 = 后一个组件期望的输入类型**。

| 组件 | 输入 | 输出 |
|------|------|------|
| `ChatPromptTemplate` | dict `{"question": ...}` | `ChatPromptValue`（一组 message） |
| `ChatModel` | `ChatPromptValue` / message 列表 | `AIMessage` |
| `StrOutputParser` | `AIMessage` | `str`（纯文本） |

类型对得上就能串。这也是为什么 LCEL 既能跑通也能帮你发现错误——类型不对，立刻报错。

---

## 四、本课代码：用 LCEL 重写你的第一个 RAG

`code.py` 做的事和你 RAG L01 **完全相同**，但用 LCEL 重写：

```
retriever | prompt | model | parser
```

对比代码量（运行 `code.py` 会看到具体行数对比）：

| | 手写版（RAG L01） | LCEL 版（本课） |
|---|---|---|
| 总行数 | ~200 行 | ~80 行 |
| 检索 | `embed_texts()` + `collection.query()` 两函数 | `Chroma.as_retriever()` 一行 |
| 拼接 prompt | f-string 手拼 | `ChatPromptTemplate.from_template()` |
| 调模型 + 提取 | 两步手动 | `model | StrOutputParser()` |
| 想加流式 | 要重写一个 `stream=True` 循环 | 把 `.invoke()` 换成 `.stream()` 即可 |

**这就是框架的价值**：不是原理更复杂了，而是把原理封装成可复用、可组合、可替换的积木。

---

## 五、一个必须清醒的认知：框架 ≠ 银弹

| 框架做得好的 | 框架没解决/要小心的 |
|-------------|---------------------|
| 标准化接口，组件可替换 | 检索质量仍取决于 embedding/切块（原理没变） |
| 自动获得 stream/batch | prompt 的"防幻觉"设计仍要你自己想 |
| 可观测性（L05 接 LangSmith） | 黑盒化：报错时栈深，需要懂内部 |
| 减少胶水代码 | 版本迁移成本（如 community sunset） |

**结论**：原理你已经懂了（前两门课），现在学框架是「**把同样的原理，用更省力的方式落地**」。知道框架在哪一层帮你做事，比盲目调包重要得多。

---

## 六、运行本课

```bash
# 确保已配置 .env（和前两门课共用同一个）
python framework-lessons/01_lcel_overview/code.py
```

你会看到：
1. 手写版 RAG 的关键步骤回顾（行数统计）
2. LCEL 版重写（同一问题，代码量对比）
3. `.invoke()` vs `.stream()` 同一条链的两种调用
4. `.batch()` 批量问答

---

## 七、小结 & 下节预告

✅ 现在你应该明白：
- LangChain 1.x 的包结构与 `langchain-community` sunset 的背景
- LCEL = `|` 管道 + Runnable 协议（invoke/stream/batch）
- 框架如何把你的手写 RAG 压缩到几行

🔜 **L02** 会深入 LCEL 三个核心积木：**Models + Prompts + Output Parsers**，把你手写 `messages` 拼装和 `tool_calls` 解析的活儿，全交给框架。对应你 RAG L05 和 Agent L02 的内容。
