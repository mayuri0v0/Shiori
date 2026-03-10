import os

from langchain.tools import tool


@tool
def list_directory(path: str) -> str:
    """列出某个目录下的文件和子目录。

    参数:
        path: 要查看的目录绝对路径（建议由前端或用户明确指定）。
    返回:
        一个可直接展示的文本列表，包含 [DIR]/[FILE] 标记及文件大小。
    """

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
    """读取指定文本文件内容，用于分析和总结。

    注意事项：
    - 仅按 UTF-8 尝试解码（errors="ignore"），二进制文件会被自动“过滤”掉
    - 默认最多读取 max_chars 个字符，避免一次性加载超大文件
    """

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
                            matches.append(f"{full_path} (L{line_no}): {snippet[:200]}")
                            break
            except Exception:
                continue

    if not matches:
        return f"在目录 {root} 下未找到包含“{keyword}”的文本文件。"

    header = f"在目录 {root} 下找到包含“{keyword}”的文件（最多 {max_results} 条）："
    return header + "\n" + "\n".join(matches)

