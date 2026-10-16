# Folder Scanner for Windows

一个面向 Windows 的文件夹占用分析工具，帮助你快速找出占用空间较大的目录，并提供微信数据目录的体积分析。

> **项目声明：本项目仅用于个人学习、研究和技术交流，不构成商业软件或数据清理服务。**

## 功能

- 选择任意文件夹，扫描文件和子目录大小
- 按目录占用排序，懒加载目录树
- 显示根目录占比和父目录占比
- 复制路径与系统信息，方便向 AI 或技术支持提问
- 分析微信账号目录中的聊天数据库、图片、视频、文件、缓存和备份
- 可选的全盘微信账号发现
- 通过本地缓存保留最近一次微信分析结果

## 下载使用

在 GitHub Releases 下载运行 `scaner_with_wechat.exe`。

程序不会上传文件内容。微信分析功能会读取目录名称、目录路径和文件大小；这些信息仅用于本地显示和缓存。

首次使用全盘微信扫描前，请确认你理解它会遍历本机可访问的磁盘，并可能耗费较长时间。权限不足的目录会被跳过。

## 从源码运行

需要 Windows Python 3.10 或更高版本，并在安装 Python 时勾选 Tkinter。

```powershell
python scaner_with_wechat.py
```

Pillow 不是必需依赖；未安装时程序仍可运行，但标题栏图标的缩放显示可能不可用。

## 构建 Windows 可执行文件

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --noconfirm scaner_with_wechat.spec
```

构建结果位于 `dist/`。`geek.exe` 是可选的第三方卸载工具：如果它存在，构建程序会将其打包；如果不存在，主程序仍可正常构建和运行，但对应按钮不可用。

## 数据位置

打包运行时，配置和微信扫描缓存保存在：

```text
%APPDATA%\FolderSizeScanner\
```

开发环境会将它们写入源码目录。缓存可能包含本机目录路径，不应提交到 Git 或公开发布。

## 已知限制

- 当前仅支持 Windows；程序依赖 Win32 API 和 Tkinter。
- 某些系统目录需要管理员权限才能读取。
- 文件在扫描过程中发生变化时，统计结果可能与最终磁盘状态略有差异。
- 微信目录结构可能随微信版本变化，分类说明仅供参考。
- 程序不会自动删除文件，清理前请自行确认路径和内容。

## 许可证与第三方组件

本项目代码采用 MIT 许可证。`geek.exe` 不属于本项目代码，是可选的第三方组件。请以 Geek Uninstaller 官方页面的当前条款为准：

- 官方网站：[geekuninstaller.com](https://geekuninstaller.com/)
- 官方许可页面：[Geek Uninstaller License](https://geekuninstaller.com/license)

仓库可以包含 `geek.exe`，但这不会自动授权或保证其再分发。只有在确认官方许可允许的情况下，才应将它提交并放入发布包。项目界面和功能曾参考 Pinkbin，未包含其代码或资源。

## 反馈

提交 Issue 时请不要上传微信缓存、账号目录、个人文件路径或其他隐私数据。请附上 Windows 版本、Python/PyInstaller 版本和可复现步骤。
