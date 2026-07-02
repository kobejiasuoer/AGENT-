# Lesson 01 练习 — LCEL 与框架全景

> 动手做才能真懂。以下练习围绕本课代码，建议每题都跑一遍验证。

---

## 练习 1：换问题，对比手写版答案（10 分钟）

把 `code.py` 里 `QUESTIONS` 换成 3 个新问题，至少包含：
- 一个文档里**有明确答案**的（如"加班工资怎么算？"——注意：当前 KNOWLEDGE 里没有加班相关，应该回答"我不知道"）
- 一个需要**综合多条**的（如"年假和病假各有什么要求？"）

跑 `code.py`，再跑一遍 `lessons/01_getting_started/code.py`（改同样的问题）。

**观察**：
- 两个版本答案是否一致？（应该接近，因为用的是同一份知识 + 同样的防幻觉 prompt）
- 哪个版本你改起来更快？

---

## 练习 2：理解数据流（关键概念）

在 `build_rag_chain` 里，链是：

```python
{"context": retriever | format_docs, "question": RunnablePassthrough()}
| prompt | llm | parser
```

回答以下问题（这是面试常考的 LCEL 理解）：

1. `retriever` 的输入是什么类型？输出是什么类型？
2. `format_docs` 收到的是什么？返回什么？
3. 如果把 `RunnablePassthrough()` 换成 `"固定问题"`（一个字符串常量），会发生什么？
4. 为什么需要 `RunnablePassthrough()`？删掉它会怎样？（提示：prompt 的 `{question}` 从哪来？）

> 把答案写在你的笔记里。理解这条链的数据流 = 理解 LCEL 的 80%。

---

## 练习 3：观察 stream vs invoke 的差别（5 分钟）

在 `demo_stream` 里加一行，统计流式输出从开始到收到第一个 chunk 的耗时，和总耗时。

提示（用 `time` 模块）：
```python
import time
t0 = time.time()
first_chunk_time = None
for chunk in chain.stream(question):
    if first_chunk_time is None:
        first_chunk_time = time.time() - t0
        print(f"\n[首字耗时 {first_chunk_time:.2f}s]")
    ...
print(f"[总耗时 {time.time()-t0:.2f}s]")
```

**思考**：为什么"首字耗时"对用户体验很重要？这就是为什么很多产品坚持用流式。

---

## 练习 4：把 TOP_K 从 5 改成 2（5 分钟）

在 `build_components` 里把 `search_kwargs={"k": TOP_K}` 的 k 改成 2，重跑。

**观察**：
- 答案质量有变化吗？
- 对比你在 RAG L03 学的"Top-K 的 K 怎么选"，框架有没有改变这个原理？

> 答案应该是：原理没变，框架只是让调参数更方便了。这正是本课的核心认知。

---

## 思考题（不写代码）

1. **为什么要 `langchain-core` 单独抽出来？** 提示：想象一下，如果 LangChain 要支持别的语言/生态，接口抽象层需不需要独立。

2. **`langchain-community` 被 sunset 这件事，对你选框架有什么启示？** 提示：依赖一个快速变动的框架，意味着什么成本？

3. **什么时候你会选择手写而不是用 LCEL？** 想一个具体场景。

---

## 完成标志

- [ ] 能口述 LCEL 链的数据流（练习 2 的 4 个问题）
- [ ] 能说出 `langchain-core / langchain / langchain-community` 的分工
- [ ] 跑通了 invoke / stream / batch 三种调用
- [ ] 理解"框架封装原理但不改变原理"这句话

下一课 [L02](../02_models_prompts_parsers/) 我们深入三件套：Models + Prompts + Output Parsers。
