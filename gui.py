
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
)

from main import create_file_agent


class FileAgentWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("本地文件智能助手（LangChain + PyQt）")
        self.resize(900, 600)

        self.agent, self.config = create_file_agent(thread_id="file-agent-gui")

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # 顶部提示
        self.info_label = QLabel(
            "示例指令：\n"
            " - “帮我列出 D:/software 目录下的内容”\n"
            " - “读取并总结 D:/README.md 的内容”\n"
            " - “在 D:/project 目录下搜索包含 `TODO` 的文件”"
        )
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # 对话区域
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        layout.addWidget(self.chat_view, stretch=1)

        # 输入区域
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("输入你想对文件做的操作，比如：列出某个目录、分析某个文件……")
        self.input_edit.returnPressed.connect(self._on_send_clicked)

        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self._on_send_clicked)

        input_layout.addWidget(self.input_edit, stretch=1)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

    def append_message(self, speaker: str, text: str) -> None:
        self.chat_view.append(f"<b>{speaker}：</b> {text}")
        self.chat_view.verticalScrollBar().setValue(
            self.chat_view.verticalScrollBar().maximum()
        )

    def _on_send_clicked(self) -> None:
        user_text = self.input_edit.text().strip()
        if not user_text:
            return

        self.append_message("你", user_text)
        self.input_edit.clear()
        self.input_edit.setDisabled(True)
        self.send_button.setDisabled(True)

        QApplication.processEvents()

        try:
            resp = self.agent.invoke(
                {"messages": [{"role": "user", "content": user_text}]},
                config=self.config,
            )
            structured = resp.get("structured_response")
            if structured is not None:
                answer = getattr(structured, "answer", str(structured))
            else:
                # 兜底：直接把整个响应对象转成字符串
                answer = str(resp)
        except Exception as e:
            answer = f"调用代理失败：{e}"

        self.append_message("助手", answer)

        self.input_edit.setDisabled(False)
        self.send_button.setDisabled(False)
        self.input_edit.setFocus(Qt.FocusReason.OtherFocusReason)


def main() -> None:
    app = QApplication(sys.argv)
    window = FileAgentWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

