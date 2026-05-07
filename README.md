# Shiori（栞）

基于 LangChain Agent 的本地文件智能助手桌面应用。通过 GUI 与 LLM 对话，让 AI 帮助浏览、读取和搜索本地文件。

## 功能

- **文件浏览**：列出目录结构
- **文件阅读**：读取文本文件内容（支持分片长文件）
- **全文搜索**：递归搜索目录中包含关键字的文件
- **多 LLM 后端**：支持 OpenAI / DeepSeek / Anthropic 等兼容接口
- **会话管理**：新建、切换、删除、清空历史会话
- **流式输出**：逐 token 显示 LLM 回复
- **运行日志**：实时查看工具调用轨迹与耗时
- **亮/暗主题**：极简黑白双主题切换

## 快速开始

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
python gui.py
```

## 使用说明

1. 启动后点击右上角 **设置**，填写 API Key、Base URL、Model
2. 在输入框中描述需求，例如："列出 D:/projects 目录"、"搜索 D:/docs 下包含 TODO 的文件"
3. 左侧 **会话** 面板可管理历史对话，右侧 **运行详情** 面板查看工具调用日志

## 项目结构

```
Shiori/
├── main.py          # Agent 工厂、模型初始化、会话 CRUD
├── gui.py           # PyQt5 图形界面
├── tools.py         # Agent 工具：list_directory / read_file / search_in_files
├── assets/
│   ├── fonts/       # 内置字体（HarmonyOS Sans SC）
│   └── icon/        # 应用图标
└── requirements.txt
```

## 技术栈

- **Python 3.10+**
- **PyQt5** — 桌面 GUI
- **LangChain / LangGraph** — AI Agent 框架
- **SQLite** — 会话历史持久化

## 许可

MIT
