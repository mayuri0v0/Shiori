import os
from dataclasses import dataclass
from typing import Any, List, Optional

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

# =========================
# 系统提示 & 响应结构
# =========================

SYSTEM_PROMPT = """你是一个专业的本地文件智能助手，擅长：
- 浏览和管理计算机上的文件与文件夹（列目录、查看文件内容、关键字搜索等）
- 对文本类文件进行分析、总结、比较和重写建议

使用工具时注意：
- 优先使用工具获取真实文件信息，不要凭空捏造文件内容
- 对删除、覆盖等破坏性操作务必先向用户确认（目前工具中未直接提供删除功能）
- 如果路径不确定，请先向用户确认或建议用户提供绝对路径

回答时请使用简体中文，说明你做了哪些操作，并给出清晰的下一步建议。"""


@dataclass
class ResponseFormat:
    """代理响应结构。"""

    # 给用户的自然语言回答
    answer: str
    # （可选）本轮中重点涉及的文件路径
    related_files: Optional[List[str]] = None


# =========================
# 工具定义
# =========================

@tool
def list_directory(path: str) -> str:
    """列出某个目录下的文件和子目录。参数为要查看的目录绝对路径。"""
    if not os.path.exists(path):
        return f"目录不存在：{path}"
    if not os.path.isdir(path):
        return f"给定路径不是目录：{path}"

    try:
        entries = os.listdir(path)
    except Exception as e:
        return f"读取目录失败：{e}"

    if not entries:
        return f"目录为空：{path}"

    lines: list[str] = []
    for name in entries:
        full = os.path.join(path, name)
        if os.path.isdir(full):
            lines.append(f"[DIR]  {name}")
        else:
            try:
                size = os.path.getsize(full)
                lines.append(f"[FILE] {name}  ({size} bytes)")
            except OSError:
                lines.append(f"[FILE] {name}")

    return "目录内容：\n" + "\n".join(sorted(lines))


@tool
def read_file(path: str, max_chars: int = 4000) -> str:
    """读取指定文本文件内容，用于分析和总结。path 为绝对路径。"""
    if not os.path.exists(path):
        return f"文件不存在：{path}"
    if not os.path.isfile(path):
        return f"给定路径不是文件：{path}"

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
    except Exception as e:
        return f"读取文件失败：{e}"

    suffix = ""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_content = f.read()
        if len(all_content) > len(content):
            suffix = "\n\n[内容已截断，仅显示前部分。]"
    except Exception:
        # 如果重新读取失败，就忽略截断提示
        pass

    return f"文件路径：{path}\n=== 内容开始 ===\n{content}{suffix}"


@tool
def search_in_files(root: str, keyword: str, max_results: int = 20) -> str:
    """在某个目录（包含子目录）下搜索包含指定关键字的文本文件。

    参数：
    - root: 起始搜索目录绝对路径
    - keyword: 要搜索的字符串
    - max_results: 最多返回多少条匹配结果
    """
    if not os.path.exists(root):
        return f"目录不存在：{root}"
    if not os.path.isdir(root):
        return f"给定路径不是目录：{root}"

    matches: list[str] = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if len(matches) >= max_results:
                break
            full_path = os.path.join(dirpath, filename)
            # 只尝试按文本方式打开，二进制大文件会被自动跳过
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_no, line in enumerate(f, start=1):
                        if keyword in line:
                            snippet = line.strip()
                            matches.append(
                                f"{full_path} (L{line_no}): {snippet[:200]}"
                            )
                            break
            except Exception:
                continue

    if not matches:
        return f"在目录 {root} 下未找到包含“{keyword}”的文本文件。"

    header = f"在目录 {root} 下找到包含“{keyword}”的文件（最多 {max_results} 条）："
    return header + "\n" + "\n".join(matches)


# =========================
# 模型 & 代理工厂
# =========================

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL")
llm_model = os.getenv("LLM_MODEL")

model = init_chat_model(
    model=llm_model,
    api_key=api_key,
    temperature=0,
    base_url=base_url,
)


def create_file_agent(thread_id: str = "file-agent-default") -> tuple[Any, dict]:
    """创建一个用于本地文件管理/分析的 LangChain 代理及其配置。"""
    checkpointer = InMemorySaver()

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[list_directory, read_file, search_in_files],
        response_format=ResponseFormat,
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": thread_id}}
    return agent, config


if __name__ == "__main__":
    # 简单命令行测试：可直接运行 main.py 进行对话
    agent, config = create_file_agent()
    print("本地文件智能助手已启动，可以用自然语言提问。输入 'exit' 退出。")

    while True:
        user_input = input("你：").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        try:
            resp = agent.invoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
            structured = resp.get("structured_response")
            if structured:
                # dataclass -> 有属性 answer
                answer = getattr(structured, "answer", str(structured))
            else:
                answer = str(resp)
        except Exception as e:
            answer = f"调用代理出错：{e}"

        print(f"助手：{answer}")
