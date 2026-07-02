"""
Lesson 01 — LCEL 与框架全景：从手写拼装到管道
================================================
本课用 LangChain 的 LCEL（管道语法）重写你 RAG L01 的第一个 RAG。

你会看到：
  1. 同一个 RAG，手写要 ~200 行，LCEL 只要 ~80 行
  2. 同一条 LCEL 链，.invoke() / .stream() / .batch() 一键切换
  3. 框架替你封装了哪些"胶水代码"

运行方式：
  python framework-lessons/01_lcel_overview/code.py

前置：已配置 .env（ZHIPUAI_API_KEY），和前两门课共用同一个。
"""
# 消除 langchain-community 的 sunset 警告，教学时会单独讲这个背景
import warnings
warnings.filterwarnings("ignore", message=".*langchain-community.*is being sunset.*")

import os

# ──────────────────────────────────────────────────────────────
# 兼容旧 Python 的 sqlite3（和 RAG L01 一样，3.9+ 可忽略）
# ──────────────────────────────────────────────────────────────
try:
    import pysqlite3
    import sys
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

from dotenv import load_dotenv

# === LangChain 核心导入（当前验证可用的版本与路径） ===
# 版本基准：langchain 1.3.x / langchain-community 0.4.x / langchain-chroma 1.1.x
#
# ⚠️ 背景提示：langchain-community 正在被 sunset，未来智谱会有独立包
#    langchain-zhipuai。届时把下面的 import 改成新路径即可。
from langchain_community.chat_models import ChatZhipuAI          # 智谱 GLM 的 LangChain 封装
from langchain_community.embeddings import ZhipuAIEmbeddings     # 智谱 embedding-3 的封装
from langchain_chroma import Chroma                              # Chroma 向量库（已独立成包）
from langchain_core.prompts import ChatPromptTemplate            # 提示词模板（替代手写 f-string）
from langchain_core.output_parsers import StrOutputParser        # 把 AIMessage 转成纯字符串
from langchain_core.runnables import RunnablePassthrough         # 透传组件（管道里"原样传下去"）

# ──────────────────────────────────────────────────────────────
# 常量配置（和 RAG L01 保持一致，方便对比）
# ──────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "embedding-3"
CHAT_MODEL = "glm-4"          # 想免费可换 "glm-4-flash"
TOP_K = 5
COLLECTION_NAME = "acme_handbook_lcel"   # 换个名字，避免和手写版的 Chroma 集合冲突
CHROMA_PATH = "./chroma_db_lcel"         # 同理，独立目录

# 复用 RAG L01 的硬编码知识（同一份数据，方便对比效果）
KNOWLEDGE = [
    "ACME 公司实行弹性工作制，标准工作时间为周一至周五 9:00-18:00，午休 12:00-13:00，每天累计工作满 8 小时。每月最后一个周六为全员培训日，需正常出勤。",
    "年假制度：入职满 1 年享有 5 天带薪年假，满 3 年享有 10 天，满 5 年及以上享有 15 天。",
    "病假需提供三甲医院病假条，期间发放基本工资的 60%；事假为无薪假，需提前 1 个工作日 OA 申请并经直属上级审批。",
    "餐饮报销每人每餐不超过 80 元，差旅住宿一线城市不超过 500 元每晚；报销单需在费用发生后 30 个自然日内提交。",
    "经直属上级批准，员工每周可远程办公最多 2 个工作日；试用期员工不适用远程办公政策。",
    "ACME 公司茶水间位于 3 楼东侧，提供免费咖啡和零食，每天 15:00 供应下午茶。",
]

# 要问的问题（和 RAG L01 一样的问题，方便对比答案质量）
QUESTIONS = [
    "我在公司干了 4 年，能休几天年假？",
    "试用期员工能远程办公吗？",
]


# ════════════════════════════════════════════════════════════
# 第 1 步：创建组件（这就是手写版里要写 5 个函数才能干的事）
# ════════════════════════════════════════════════════════════
def build_components():
    """创建 LCEL 链需要的所有组件。

    对照手写版（RAG L01）：
      - 手写：ZhipuAI() 一个客户端，embedding/chat 全靠它 + 自己调方法
      - LCEL：ChatZhipuAI / ZhipuAIEmbeddings 各一个对象，已是 Runnable
    """
    load_dotenv()
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key or api_key.startswith("xxxx"):
        raise RuntimeError(
            "还没配置 API Key！请把 .env.example 复制成 .env，填入真实的 ZHIPUAI_API_KEY。"
        )

    # ① Embedding 模型 —— 对应手写版 embed_texts() 里调的 client.embeddings.create()
    embeddings = ZhipuAIEmbeddings(model=EMBEDDING_MODEL, api_key=api_key)

    # ② Chroma 向量库 —— 对应手写版的 chromadb.PersistentClient + collection.add()
    #    langchain-chroma 把"建库 + 入库"压缩成 Chroma.from_texts() 一行
    vectorstore = Chroma.from_texts(
        texts=KNOWLEDGE,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
    )

    # ③ Retriever（检索器）—— 对应手写版的 retrieve() 函数
    #    as_retriever() 把向量库变成一个标准 Runnable，统一了所有检索方式的接口
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    # ④ Prompt 模板 —— 对应手写版的 f-string 拼接
    #    用占位符 {context} {question}，运行时自动填充
    prompt = ChatPromptTemplate.from_template(
        "你是一个严谨的问答助手。请只根据下面提供的材料回答用户问题。"
        "如果材料里没有相关信息，请直接回答“我不知道”，不要编造。\n\n"
        "【材料】\n{context}\n\n"
        "【用户问题】{question}"
    )

    # ⑤ 模型 —— 对应手写版的 client.chat.completions.create()
    llm = ChatZhipuAI(model=CHAT_MODEL, api_key=api_key)

    # ⑥ 输出解析器 —— 对应手写版的 response.choices[0].message.content
    #    把 AIMessage 对象转成纯字符串
    parser = StrOutputParser()

    return retriever, prompt, llm, parser


# ════════════════════════════════════════════════════════════
# 第 2 步：组装 LCEL 链（这是本课的高潮）
# ════════════════════════════════════════════════════════════
def format_docs(docs):
    """把检索到的 Document 列表拼成一段文本。

    Retriever 返回的是 List[Document]，prompt 模板要的是一段字符串，
    中间需要这个"适配器"。用 RunnableLambda 也可以，这里用普通函数 + LCEL 的 map 配合。
    """
    return "\n\n".join(f"【材料{i+1}】{d.page_content}" for i, d in enumerate(docs))


def build_rag_chain(retriever, prompt, llm, parser):
    """用 | 把组件串成一条 RAG 链。

    这条链做的事，和手写版 main() 里的第 3、4 步完全一样：
        检索 → 拼材料 → 拼 prompt → 调模型 → 提取答案

    ⭐ 重点理解数据流（从右往左看每一步输入输出）：
        输入: {"question": "..."}
        ↓ retriever 收到 question，检索出 List[Document]
        ↓ format_docs 把 Document 列表拼成一段字符串 context
        ↓ prompt 用 {context} 和 {question} 模板渲染出完整提示
        ↓ llm 生成 AIMessage
        ↓ parser 提取纯文本答案
    """
    # RunnablePassthrough：把原始输入的 question 原样透传给 prompt 的 {question}
    # （因为 retriever 只消费 question，但 prompt 还需要原 question）
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )
    return chain


# ════════════════════════════════════════════════════════════
# 第 3 步：演示同一条链的三种调用方式
# ════════════════════════════════════════════════════════════
def demo_invoke(chain, question):
    """方式 1：invoke —— 最常用，一次性返回完整结果。

    对应手写版的 generate_answer()：等模型全部生成完才返回。
    """
    print(f"\n🔎 问题：{question}")
    print("🤖 回答（invoke，一次性）：")
    answer = chain.invoke(question)
    print(answer)
    return answer


def demo_stream(chain, question):
    """方式 2：stream —— 流式，一个 token 一个 token 吐出。

    ⭐ LCEL 的杀手锏：同一条链，换个方法就是流式输出。
    回顾 RAG L05 手写流式时，你专门写了 stream=True 的循环 + chunk 拼接——
    这里 chain.stream() 直接给，0 改动。
    """
    print(f"\n🔎 问题：{question}")
    print("🤖 回答（stream，逐字）：", end="", flush=True)
    full = ""
    for chunk in chain.stream(question):
        # chunk 是已经解析过的字符串片段
        print(chunk, end="", flush=True)
        full += chunk
    print()  # 换行
    return full


def demo_batch(chain, questions):
    """方式 3：batch —— 批量并发跑多个问题。

    手写版要并发跑多个问题，得自己写线程池或 asyncio。
    LCEL 的 .batch() 内部帮你处理了并发。
    """
    print(f"\n📦 批量提问 {len(questions)} 个问题：")
    answers = chain.batch(questions)
    for q, a in zip(questions, answers):
        print(f"  Q: {q}")
        print(f"  A: {a[:80]}{'...' if len(a) > 80 else ''}\n")


# ════════════════════════════════════════════════════════════
# 主流程
# ════════════════════════════════════════════════════════════
def main():
    print("=" * 64)
    print("Lesson 01 — LCEL 与框架全景：从手写拼装到管道")
    print("=" * 64)

    print("\n📐 本课对比：手写 RAG L01（~200 行）vs LCEL 版（本文件）")
    print("   手写版需要 5 个函数：create_zhipu_client / embed_texts /")
    print("   build_knowledge_base / retrieve / generate_answer")
    print("   LCEL 版只需：build_components + build_rag_chain（组件已是积木）\n")

    # 1. 建组件
    print("🔧 第 1 步：创建组件（embedding / vectorstore / retriever / prompt / llm / parser）")
    retriever, prompt, llm, parser = build_components()
    print(f"   ✅ Chroma 已入库 {len(KNOWLEDGE)} 条知识")
    print(f"   ✅ retriever={type(retriever).__name__}, llm={type(llm).__name__}")

    # 2. 组装链
    print("\n🔗 第 2 步：用 | 组装 LCEL 链  retriever | prompt | llm | parser")
    chain = build_rag_chain(retriever, prompt, llm, parser)

    # 3. 演示三种调用（同一问题，三种方式）
    print("\n" + "─" * 64)
    print("【演示 1】invoke —— 一次性返回（对比手写版最接近）")
    demo_invoke(chain, QUESTIONS[0])

    print("\n" + "─" * 64)
    print("【演示 2】stream —— 流式（同一条链，换个方法即可）")
    demo_stream(chain, QUESTIONS[0])

    print("\n" + "─" * 64)
    print("【演示 3】batch —— 批量并发")
    demo_batch(chain, QUESTIONS)

    print("=" * 64)
    print("✅ 对比要点：")
    print("   - 手写版要 200 行 + 5 个函数；LCEL 版核心链只有 1 个 build_rag_chain")
    print("   - 同一条 chain，invoke/stream/batch 三种能力自动具备")
    print("   - 这就是框架：把原理封装成可复用、可组合、可替换的积木")
    print("=" * 64)


if __name__ == "__main__":
    main()
