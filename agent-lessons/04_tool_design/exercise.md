# L04 练习

> 改 `code.py` 里的代码，运行 `python agent-lessons/04_tool_design/code.py` 观察变化。

---

## 练习 1：改造一个差 description，看效果差异
在 `TOOLS_SPEC_BAD` 里，挑一个工具（比如 `unit_convert`），把它的 description 从"转换工具"改成清晰版：

```python
"description": "单位换算。支持米↔千米、摄氏度↔华氏度。当用户问'XX米等于多少千米'时使用。",
```

重跑实验 2，对比改造前后，模型选这个工具的准确率有没有提升。

**思考**：这印证了"description 是 function calling 的灵魂"。一个 description 的改动，就能显著影响 Agent 表现。

---

## 练习 2：加一个"万能工具"，观察工具选择灾难
故意加一个职责不清的万能工具到 `TOOLS_SPEC_GOOD`：

```python
{"type": "function", "function": {
    "name": "do_anything",
    "description": "处理各种任务。当你不确定用哪个工具时，可以用这个。",
    "parameters": {"type": "object", "properties": {
        "task": {"type": "string"}
    }, "required": ["task"]},
}}
```

（别忘了在 TOOL_REGISTRY 注册一个返回"我不会"的实现）

跑实验 1 的任务，看 Agent 会不会偷懒选这个万能工具。

**思考**：这模拟了真实场景里的反模式——"万能工具"听起来强大，实际上会让模型丧失选择能力。这就是为什么单一职责如此重要。

---

## 练习 3：设计一个新工具，从零开始
自己设计一个有用的工具，完整地加进来（函数实现 + 注册 + TOOLS_SPEC）。建议从这几个里挑：

- `count_words`：统计字符串里某个词出现的次数
- `is_palindrome`：判断字符串是不是回文（正读反读一样）
- `temperature_compare`：比较两个城市温度谁高

**关键**：description 要认真写——写明"做什么 + 什么时候用 + 参数例子"。然后问 Agent 相关问题，看它能不能选对你设计的工具。

**思考**：把你写的 description 拿给别人看（或自己隔天看），问"如果只看这句话，你知道什么时候用这个工具吗？"如果犹豫，说明 description 还要改。

---

## 练习 4：动态工具加载（进阶）
真实场景工具很多时，不会一次性全给模型。试着实现"按场景加载工具子集"：

```python
def select_relevant_tools(question: str) -> list:
    """根据问题简单判断该加载哪类工具。"""
    if any(k in question for k in ["天气", "气温", "下雨"]):
        return [t for t in TOOLS_SPEC_GOOD if t["function"]["name"] == "get_weather"]
    if any(k in question for k in ["计算", "加", "减", "乘", "除"]):
        return [t for t in TOOLS_SPEC_GOOD if t["function"]["name"] == "calculator"]
    return TOOLS_SPEC_GOOD  # 默认全给
```

在 run_agent 前调用它，只传相关工具。

**思考**：动态加载是应对"工具太多"的工业界方案。虽然这里的规则判断很粗糙，但思路是真实的——先粗筛，再让模型在子集里选，准确率更高。

---

## ✅ 完成本课后，你应该能回答
1. 好工具的四个特征是什么？
2. 为什么"工具越多越好"是误区？工具过多会带来什么问题？
3. description 该怎么写？三个技巧是什么？
4. 功能重叠的工具会带来什么困扰？怎么解决？
5. 为什么说"description 是写给模型的广告语"？
