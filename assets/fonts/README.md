## 字体内置说明（PyQt5）

这个项目支持把字体文件“随程序分发”，并在启动时由 Qt 注册后使用。

### 1) 把字体文件放到这里

将你要内置的字体文件（`.ttf` / `.otf`）放到本目录 `assets/fonts/` 下。

当前代码（`gui.py` 的 `load_embedded_fonts()`）默认会尝试加载以下文件名（不存在就跳过）：

- `Inter-Regular.ttf`
- `Inter-SemiBold.ttf`
- `Inter-Bold.ttf`
- `HarmonyOS_Sans_SC_Regular.ttf`
- `HarmonyOS_Sans_SC_Medium.ttf`
- `HarmonyOS_Sans_SC_Bold.ttf`

你也可以改成你自己实际的文件名，只要在 `candidates = [...]` 里同步即可。

### 2) 字体 family 名称

成功加载后，Qt 会把字体注册成一个或多个 **family**（比如 `Inter`、`HarmonyOS Sans SC`）。
界面样式使用的字体链是：

```
QWidget {
    font-family: "Inter", "HarmonyOS Sans SC", "Segoe UI", "Microsoft YaHei", sans-serif;
}
```

也就是说：只要注册成功，就会优先用 Inter / HarmonyOS；否则会回退到系统字体。

### 3) PyInstaller 打包时把字体一起带上（Windows）

如果你用 PyInstaller 打包，需要把 `assets/fonts` 作为数据文件带上，例如：

```bash
pyinstaller -F gui.py --add-data "assets/fonts;assets/fonts"
```

注意：Windows 下 `--add-data` 的源/目标分隔符是 `;`（Linux/macOS 是 `:`）。

