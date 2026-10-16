import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import platform
import time
import ctypes
import ctypes.wintypes
import webbrowser
import json

def get_app_data_dir():
    """获取用户数据目录：打包后存系统AppData，不污染程序目录"""
    app_folder_name = "FolderSizeScanner"  # 自定义目录名，可改成你的软件名
    if getattr(sys, 'frozen', False):
        # 打包后：取系统 %APPDATA% 路径
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        # 开发环境：放脚本目录，方便调试
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    data_dir = os.path.join(base_dir, app_folder_name)
    os.makedirs(data_dir, exist_ok=True)  # 自动创建目录，不存在不报错
    return data_dir

# 程序数据目录（缓存、配置永久存放）
APP_DATA_DIR = get_app_data_dir()
# 扫描缓存文件
CACHE_FILE = os.path.join(APP_DATA_DIR, "wx_scan_cache.json")
# 用户配置文件（保存默认微信路径等设置）
USER_CONFIG_FILE = os.path.join(APP_DATA_DIR, "wx_user_config.json")
def load_user_config():
    """加载用户配置"""
    try:
        if os.path.exists(USER_CONFIG_FILE):
            with open(USER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_user_config(data):
    """保存用户配置"""
    try:
        with open(USER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存用户配置失败: {e}")
def save_scan_cache(data):
    """保存扫描结果到本地缓存"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存缓存失败: {e}")

def load_scan_cache():
    """从本地缓存加载扫描结果"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载缓存失败: {e}")
    return {}
# ========== 资源路径适配函数 ==========
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# ========== 配置项 ==========
ICON_PATH = resource_path("icon.ico")
GEEK_PATH = resource_path("geek.exe")
# 全盘扫描默认跳过的目录名（可在界面中自定义添加/删除）
SKIP_DIRS = {'$Recycle.Bin', 'System Volume Information', 'Windows'}
# 微信目录用途标注字典（一级目录+二级子目录）
WX_DIR_USAGE = {
    # 一级目录
    "apm_record": "性能监控日志（运行埋点、崩溃记录，可删）",
    "business": "业务数据缓存（公众号/小程序相关，可删）",
    "cache": "通用缓存文件（临时数据，可安全清理）",
    "config": "账号配置文件（删除会重置设置，不建议删）",
    "db_storage": "业务数据库（非核心聊天库，清理不影响聊天）",
    "msg": "聊天记录核心数据库（严禁删除，丢失无法恢复）",
    "resource": "资源缓存（内置表情、头像、界面资源，可删）",
    "temp": "临时文件（可安全删除，不影响功能）",
    "backup": "聊天记录备份文件（删除会丢失备份）",
    "filestorage": "文件存储区（聊天收发的图片/视频/文件）",
    # Msg 二级子目录
    "msg/file": "聊天收发的文档文件（Word/Excel/PDF等）",
    "msg/video": "聊天收发的视频文件",
    "msg/image": "聊天收发的图片与表情包",
    "msg/voice": "聊天语音消息文件",
    "msg/msgattach": "消息内嵌附件缓存",
    # FileStorage 二级子目录
    "filestorage/file": "接收的文档文件归档",
    "filestorage/image": "聊天图片原图缓存",
    "filestorage/video": "聊天视频文件缓存",
    "filestorage/cache": "文件缩略图缓存",
    "filestorage/customemotion": "自定义表情包存储",
    "filestorage/temp": "文件临时下载目录",
}

# 疑似账号体积阈值（小于1MB的归为疑似折叠）
SUSPECT_SIZE_THRESHOLD = 1024 * 1024  # 1MB

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ---------- Win32 常量 ----------
GWL_STYLE = -16
GWL_EXSTYLE = -20
GWLP_HWNDPARENT = -8
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_FRAMECHANGED = 0x0020
WM_NCLBUTTONDOWN = 0x00A1
HTCAPTION = 0x0002
WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG = 1
IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
SM_CXSCREEN = 0
SM_CYSCREEN = 1

GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
SetWindowLongPtrW = ctypes.windll.user32.SetWindowLongPtrW
ReleaseCapture = ctypes.windll.user32.ReleaseCapture
SendMessageW = ctypes.windll.user32.SendMessageW
LoadImageW = ctypes.windll.user32.LoadImageW
GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics
GetLogicalDrives = ctypes.windll.kernel32.GetLogicalDrives

# ---------- 内存信息结构体 ----------
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def get_total_memory_gb():
    try:
        ms = MEMORYSTATUSEX()
        ms.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
        return ms.ullTotalPhys / (1024**3)
    except:
        return "未知"

def get_real_hwnd(tk_root):
    tk_root.update_idletasks()
    return GetWindowLongPtrW(tk_root.winfo_id(), GWLP_HWNDPARENT)

def set_system_icon(hwnd, icon_path):
    if not os.path.exists(icon_path):
        return False
    try:
        hicon_big = LoadImageW(None, icon_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
        hicon_small = LoadImageW(None, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
        if hicon_big:
            SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)
        if hicon_small:
            SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
        return True
    except Exception as e:
        return False

def remove_titlebar_keep_taskbar(tk_root):
    hwnd = get_real_hwnd(tk_root)
    if not hwnd:
        return False
    style = GetWindowLongPtrW(hwnd, GWL_STYLE)
    style &= ~(WS_CAPTION | WS_THICKFRAME)
    SetWindowLongPtrW(hwnd, GWL_STYLE, style)
    ex_style = GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    ex_style |= WS_EX_APPWINDOW
    ex_style &= ~WS_EX_TOOLWINDOW
    SetWindowLongPtrW(hwnd, GWL_EXSTYLE, ex_style)
    ctypes.windll.user32.SetWindowPos(
        hwnd, 0, 0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED
    )
    return True

# ---------- 通用工具函数 ----------
def human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def format_gb(bytes_val):
    return f"{bytes_val / (1024**3):.2f}"

def get_system_info():
    uname = platform.uname()
    mem_gb = get_total_memory_gb()
    mem_str = f"{mem_gb:.1f} GB" if isinstance(mem_gb, float) else mem_gb
    cpu_count = os.cpu_count() or "未知"
    screen_w = GetSystemMetrics(SM_CXSCREEN)
    screen_h = GetSystemMetrics(SM_CYSCREEN)
    return (
        f"操作系统: {uname.system} {uname.release} (版本 {uname.version})\n"
        f"系统位数: {uname.machine}\n"
        f"处理器: {uname.processor}\n"
        f"CPU核心: {cpu_count} 逻辑核心\n"
        f"总内存: {mem_str}\n"
        f"屏幕分辨率: {screen_w} × {screen_h}\n"
        f"主机名: {uname.node}\n"
        f"当前用户: {os.getlogin()}\n"
        f"Python版本: {platform.python_version()}"
    )

def get_dir_size(dir_path):
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try: total += os.path.getsize(fp)
                except: pass
    except:
        pass
    return total

# ---------- 微信扫描核心增强逻辑 ----------
def get_local_drives():
    drives = []
    bitmask = GetLogicalDrives()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if bitmask & 1:
            drive_path = f"{letter}:\\"
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
            if drive_type != 5: # 排除光驱
                drives.append(drive_path)
        bitmask >>= 1
    return drives

def detect_default_wechat_path():
    """检测微信默认存储路径，优先读取用户自定义配置"""
    user_config = load_user_config()
    custom_path = user_config.get("wechat_root_path", "")
    if custom_path and os.path.exists(custom_path):
        return custom_path
    # 无自定义配置则检测系统默认路径
    try:
        default_path = os.path.join(os.path.expanduser("~"), "Documents", "WeChat Files")
        if os.path.exists(default_path):
            return default_path
    except:
        pass
    return None

def find_wxid_folders_bruteforce(root_path, stop_event, result_callback):
    """全盘扫描wxid目录，遇到SKIP_DIRS中的目录名则跳过不递归"""
    stack = [root_path]
    while stack:
        if stop_event.is_set(): return
        current_path = stack.pop()
        try:
            with os.scandir(current_path) as entries:
                for entry in entries:
                    if stop_event.is_set(): return
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            # 命中跳过列表的目录直接跳过，不进入递归
                            if entry.name in SKIP_DIRS:
                                continue
                            if entry.name.lower().startswith("wxid_"):
                                result_callback(entry.path)
                                # 找到账号目录后不再向内深挖
                            else:
                                stack.append(entry.path)
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            continue

def scan_all_drives_for_wxid(stop_event, result_callback, status_callback):
    drives = get_local_drives()
    total_drives = len(drives)
    for i, drive in enumerate(drives):
        if stop_event.is_set(): break
        status_callback(f"正在全盘爆破扫描 {drive} 盘 ({i+1}/{total_drives})...")
        find_wxid_folders_bruteforce(drive, stop_event, result_callback)
    status_callback("全盘扫描阶段完成，正在等待深度分析...")

def get_wechat_accounts(root_path):
    accounts = []
    if not root_path or not os.path.exists(root_path): return accounts
    try:
        for name in os.listdir(root_path):
            full_path = os.path.join(root_path, name)
            if os.path.isdir(full_path) and name.startswith("wxid_"):
                accounts.append((name, full_path))
    except: pass
    return accounts

def analyze_wechat_account_detailed(account_path):
    """带用途标注的深度递归分析，返回统计结果+嵌套目录树节点"""
    stats = {
        "total": 0, "msg": 0, "image": 0, "video": 0,
        "file": 0, "cache": 0, "backup": 0, "other": 0
    }
    
    if not os.path.exists(account_path):
        return stats, []

    def get_usage(dir_name, parent_name=""):
        """获取目录用途描述，支持二级路径匹配"""
        dir_lower = dir_name.lower()
        if parent_name:
            rel_path = f"{parent_name.lower()}/{dir_lower}"
            if rel_path in WX_DIR_USAGE:
                return WX_DIR_USAGE[rel_path]
        return WX_DIR_USAGE.get(dir_lower, "子目录数据")

    def build_tree(current_path, parent_name="", depth=0, max_depth=5):
        """递归构建目录树，默认最多5层防止过深"""
        nodes = []
        if depth >= max_depth:
            return nodes
        try:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                if not os.path.isdir(item_path):
                    continue
                size = get_dir_size(item_path)
                usage = get_usage(item, parent_name)
                
                # 一级目录分类统计
                if depth == 0:
                    item_lower = item.lower()
                    if item_lower == "msg":
                        stats["msg"] = size
                    elif item_lower == "backup":
                        stats["backup"] = size
                    elif item_lower in ["temp", "cache", "apm_record", "business"]:
                        stats["cache"] += size
                    elif item_lower == "filestorage":
                        try:
                            for sub in os.listdir(item_path):
                                sub_path = os.path.join(item_path, sub)
                                if os.path.isdir(sub_path):
                                    sub_sz = get_dir_size(sub_path)
                                    sub_lower = sub.lower()
                                    if sub_lower in ["image", "customemotion"]:
                                        stats["image"] += sub_sz
                                    elif sub_lower == "video":
                                        stats["video"] += sub_sz
                                    elif sub_lower == "file":
                                        stats["file"] += sub_sz
                                    elif sub_lower in ["temp", "cache"]:
                                        stats["cache"] += sub_sz
                        except: pass
                    else:
                        stats["other"] += size
                
                # 递归生成子节点
                children = build_tree(item_path, item if depth == 0 else f"{parent_name}/{item}", depth + 1, max_depth)
                nodes.append({
                    "name": item,
                    "path": item_path,
                    "usage": usage,
                    "size": size,
                    "children": children
                })
        except (PermissionError, OSError):
            pass
        nodes.sort(key=lambda x: x["size"], reverse=True)
        return nodes

    root_children = build_tree(account_path, "", 0, max_depth=5)
    stats["total"] = get_dir_size(account_path)
    
    return stats, root_children
# ---------- 高速扫描器（主界面） ----------
class FastScanner:
    def __init__(self, root_path, progress_callback=None):
        self.root_path = os.path.abspath(root_path)
        self.progress_callback = progress_callback
        self.dir_sizes = {}
        self.scanned_files = 0
        self.scanned_bytes = 0
        self.total_files = 0
        self.is_running = True
        self._update_step = 100

    def stop(self): self.is_running = False

    def prescan_count(self):
        count = 0
        try:
            for dirpath, _, filenames in os.walk(self.root_path): count += len(filenames)
        except: pass
        self.total_files = count
        return count

    def scan(self):
        if not os.path.isdir(self.root_path): return
        stack = [(self.root_path, False)]
        dir_file_size = {}
        while stack and self.is_running:
            current_path, visited = stack.pop()
            if not visited:
                stack.append((current_path, True))
                dir_file_size[current_path] = 0
                try: entries = list(os.scandir(current_path))
                except:
                    self.dir_sizes[current_path] = 0
                    stack.pop()
                    continue
                for entry in reversed(entries):
                    if not self.is_running: break
                    try:
                        if entry.is_symlink(): continue
                        if entry.is_dir(follow_symlinks=False): stack.append((entry.path, False))
                        else:
                            sz = entry.stat(follow_symlinks=False).st_size
                            self.dir_sizes[entry.path] = sz
                            dir_file_size[current_path] += sz
                            self.scanned_files += 1
                            self.scanned_bytes += sz
                            if self.progress_callback and self.scanned_files % self._update_step == 0:
                                self.progress_callback(self.scanned_files, self.scanned_bytes, current_path)
                    except: continue
            else:
                total = dir_file_size.get(current_path, 0)
                try:
                    with os.scandir(current_path) as entries:
                        for entry in entries:
                            try:
                                if entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
                                    total += self.dir_sizes.get(entry.path, 0)
                            except: continue
                except: pass
                self.dir_sizes[current_path] = total
        if self.progress_callback and self.is_running:
            self.progress_callback(self.scanned_files, self.scanned_bytes, self.root_path)

    def get_size(self, path): return self.dir_sizes.get(path, 0)

# ---------- 跳过目录管理窗口 ----------
class SkipDirManagerWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("管理扫描跳过目录")
        self.geometry("380x420")
        self.resizable(True, True)
        self.configure(bg='#B19CD9')
        
        # 居中显示在父窗口上
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - 190
        y = master.winfo_y() + (master.winfo_height() // 2) - 210
        self.geometry(f"+{x}+{y}")
        
        self.setup_ui()

    def setup_ui(self):
        # 顶部说明
        tip = tk.Label(self, text="以下名称的文件夹将被全盘扫描跳过：",
                       bg='#B19CD9', fg='black', font=('微软雅黑', 9))
        tip.pack(pady=(10,5), padx=10, anchor='w')
        
        # 目录列表区
        list_frame = tk.Frame(self, bg='#B19CD9')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(list_frame, bd=1, relief='solid',
                                  font=('微软雅黑', 10), yscrollcommand=scroll.set)
        scroll.config(command=self.listbox.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        
        # 加载当前跳过列表
        self.refresh_list()
        
        # 底部按钮区
        btn_frame = tk.Frame(self, bg='#B19CD9')
        btn_frame.pack(fill=tk.X, padx=10, pady=8)
        
        btn_add = tk.Button(btn_frame, text="添加目录名", command=self.add_item,
                            bg='white', fg='black', bd=1, relief='solid',
                            font=('微软雅黑', 9), padx=10, pady=2)
        btn_add.pack(side=tk.LEFT, padx=5)
        
        btn_del = tk.Button(btn_frame, text="删除选中", command=self.del_item,
                            bg='white', fg='black', bd=1, relief='solid',
                            font=('微软雅黑', 9), padx=10, pady=2)
        btn_del.pack(side=tk.LEFT, padx=5)
        
        btn_reset = tk.Button(btn_frame, text="恢复默认", command=self.reset_default,
                              bg='white', fg='black', bd=1, relief='solid',
                              font=('微软雅黑', 9), padx=10, pady=2)
        btn_reset.pack(side=tk.RIGHT, padx=5)

    def refresh_list(self):
        """刷新列表显示"""
        self.listbox.delete(0, tk.END)
        for item in sorted(SKIP_DIRS):
            self.listbox.insert(tk.END, item)

    def add_item(self):
        """添加新的跳过目录名"""
        top = tk.Toplevel(self)
        top.title("添加跳过目录")
        top.geometry("280x120")
        top.configure(bg='#B19CD9')
        top.resizable(False, False)
        top.transient(self)
        top.grab_set()
        
        tk.Label(top, text="请输入要跳过的文件夹名称：",
                 bg='#B19CD9', font=('微软雅黑', 9)).pack(pady=(15,5))
        
        entry = tk.Entry(top, font=('微软雅黑', 10), width=25)
        entry.pack(pady=5)
        entry.focus()
        
        def confirm():
            name = entry.get().strip()
            if name and name not in SKIP_DIRS:
                SKIP_DIRS.add(name)
                self.refresh_list()
            top.destroy()
        
        tk.Button(top, text="确定", command=confirm,
                  bg='white', bd=1, relief='solid',
                  font=('微软雅黑', 9), padx=15, pady=2).pack(pady=8)
        
        # 窗口居中
        top.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - top.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - top.winfo_height()) // 2
        top.geometry(f"+{x}+{y}")

    def del_item(self):
        """删除选中的跳过目录"""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选中要删除的目录名", parent=self)
            return
        name = self.listbox.get(sel[0])
        if messagebox.askyesno("确认", f"确定要从跳过列表中移除「{name}」吗？", parent=self):
            SKIP_DIRS.discard(name)
            self.refresh_list()

    def reset_default(self):
        """恢复默认跳过列表"""
        if messagebox.askyesno("确认", "确定恢复为默认跳过列表吗？", parent=self):
            global SKIP_DIRS
            SKIP_DIRS = {'$Recycle.Bin', 'System Volume Information', 'Windows'}
            self.refresh_list()
# ---------- 选择默认微信根目录弹窗 ----------
# ---------- 选择默认微信根目录弹窗 ----------
class ChooseWechatRootWindow(tk.Toplevel):
    def __init__(self, master, wxid_paths, on_confirm):
        super().__init__(master)
        self.title("设置默认微信数据文件夹")
        self.geometry("560x420")
        self.resizable(True, True)  # 支持自由调整大小
        self.configure(bg='#B19CD9')
        self.on_confirm = on_confirm
        self.wxid_paths = wxid_paths

        # 窗口居中
        self.update_idletasks()
        sw = GetSystemMetrics(SM_CXSCREEN)
        sh = GetSystemMetrics(SM_CYSCREEN)
        w, h = 560, 420
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # 按父目录自动分组
        self.group_data = {}
        for path in wxid_paths:
            parent = os.path.dirname(path)
            wxid_name = os.path.basename(path)
            if parent not in self.group_data:
                self.group_data[parent] = []
            self.group_data[parent].append(wxid_name)

        self.setup_ui()
        self.transient(master)
        self.grab_set()

    def setup_ui(self):
        # 顶部说明
        tip = tk.Label(self, text="请选择一个文件夹作为默认微信数据根目录（相同目录已自动合并）：",
                       bg='#B19CD9', fg='black', font=('微软雅黑', 10))
        tip.pack(pady=(15, 10), padx=15, anchor='w')

        # 目录列表区（自适应窗口大小）
        list_frame = tk.Frame(self, bg='#B19CD9')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        scroll = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(list_frame, bd=1, relief='solid',
                                  font=('微软雅黑', 9), yscrollcommand=scroll.set,
                                  activestyle='dotbox', selectbackground='#7B68EE', selectforeground='white')
        scroll.config(command=self.listbox.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # 填充分组后的列表
        self.parent_list = list(self.group_data.keys())
        for parent in self.parent_list:
            accounts = self.group_data[parent]
            self.listbox.insert(tk.END, f"📂 根目录：{parent}")
            self.listbox.insert(tk.END, f"    包含账号：{'、'.join(accounts)}")
            self.listbox.insert(tk.END, "")

        # 底部按钮区
        btn_frame = tk.Frame(self, bg='#B19CD9')
        btn_frame.pack(fill=tk.X, padx=15, pady=15)

        btn_cancel = tk.Button(btn_frame, text="取消", command=self.destroy,
                               bg='white', fg='black', bd=1, relief='solid',
                               font=('微软雅黑', 9), padx=20, pady=3)
        btn_cancel.pack(side=tk.RIGHT, padx=5)

        btn_confirm = tk.Button(btn_frame, text="设为默认并永久记住", command=self.confirm,
                                bg='#2e7d32', fg='white', bd=1, relief='solid',
                                font=('微软雅黑', 9, 'bold'), padx=20, pady=3)
        btn_confirm.pack(side=tk.RIGHT, padx=5)

    def confirm(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择一个根目录", parent=self)
            return
        # 计算选中的分组索引
        group_idx = sel[0] // 3
        if group_idx >= len(self.parent_list):
            group_idx = len(self.parent_list) - 1
        root_path = self.parent_list[group_idx]
        
        # 永久保存用户配置
        config = load_user_config()
        config["wechat_root_path"] = root_path
        save_user_config(config)
        self.on_confirm(root_path)
        self.destroy()
# ---------- 微信扫描独立窗口 ----------
class WechatScannerWindow(tk.Toplevel):
    def open_skip_manager(self):
        """打开跳过目录管理窗口"""
        if hasattr(self, 'skip_manager_win') and self.skip_manager_win.winfo_exists():
            self.skip_manager_win.lift()
        else:
            self.skip_manager_win = SkipDirManagerWindow(self)
    

    def open_choose_root_dialog(self):
        """手动打开默认目录选择弹窗"""
        wxid_paths = list(self.root_node_ids.keys())
        if len(wxid_paths) == 0:
            messagebox.showinfo("提示", "请先扫描找到微信账号后再设置默认目录")
            return
        def on_confirm(root_path):
            self.wechat_root_path = root_path
            self.wechat_path_var.set(f"✅ 已设为默认路径：{root_path}")
            self.status_bar.config(text="已记住默认路径，下次启动自动加载")
        ChooseWechatRootWindow(self, wxid_paths, on_confirm)    
    def __init__(self, master):
        super().__init__(master)
        self.title("💬 微信存储分析专清")
        self.resizable(True, True)
        
        self.LIGHT_PURPLE = '#B19CD9'
        self.EXTRA_LIGHT_PURPLE = '#F0EBF8'
        self.configure(bg=self.LIGHT_PURPLE)
        
        # 窗口初始尺寸 + 屏幕绝对居中
        w, h = 650, 700
        sw = GetSystemMetrics(SM_CXSCREEN)
        sh = GetSystemMetrics(SM_CYSCREEN)
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # 设置窗口与任务栏图标（复用主程序图标）
        if os.path.exists(ICON_PATH):
            try:
                self.iconbitmap(default=ICON_PATH)
            except Exception as e:
                print(f"设置微信窗口图标失败: {e}")
        
        self.scan_stop_event = threading.Event()
        self.wechat_root_path = None
        self.current_wechat_account = None
        
        # 数据缓存映射
        self.accounts_data = {}
        self.wechat_node_map = {}
        self.root_node_ids = {}
        self.selected_node = None
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.setup_ui()

        # 加载历史缓存（必须在 setup_ui 之后）
        self.cache_data = load_scan_cache()
        self.after(100, self._load_from_cache)
        
        # 自动检测默认路径（放在缓存之后，避免重复添加）
        self.after(300, self.auto_detect_wechat)
    def on_close(self):
        self.scan_stop_event.set()
        # 关闭窗口时兜底保存缓存
        try:
            self._save_current_cache()
        except:
            pass
        self.destroy()
    def _show_choose_root_dialog(self, wxid_paths):
        def on_confirm(root_path):
            self.wechat_root_path = root_path
            self.wechat_path_var.set(f"✅ 已设为默认路径：{root_path}")
            self.status_bar.config(text="已记住默认路径，下次启动自动加载")
        
        ChooseWechatRootWindow(self, wxid_paths, on_confirm)
    def setup_ui(self):
        # ===== 顶部控制区 =====
        wechat_header = tk.LabelFrame(self, text="💬 微信存储扫描", 
                                      bg=self.LIGHT_PURPLE, fg='black',
                                      font=('黑体', 12, 'bold'), padx=8, pady=5)
        wechat_header.pack(fill=tk.X, padx=10, pady=(10,5))

        self.wechat_path_var = tk.StringVar(value="正在检测默认路径...")
        path_label = tk.Label(wechat_header, textvariable=self.wechat_path_var, 
                              bg=self.LIGHT_PURPLE, fg='#333',
                              font=('微软雅黑', 9), wraplength=500, justify='left')
        path_label.pack(anchor='w', pady=(0,5))

        btn_row = tk.Frame(wechat_header, bg=self.LIGHT_PURPLE)
        btn_row.pack(fill=tk.X)
        
        btn_open_root = tk.Button(btn_row, text="打开根目录", command=self.open_wechat_root,
                                  bg='white', fg='black', bd=1, relief='solid', font=('微软雅黑', 9), padx=6, pady=2)
        btn_open_root.pack(side=tk.LEFT, padx=(0,5))
        
        btn_choose = tk.Button(btn_row, text="手动选择", command=self.choose_wechat_path,
                               bg='white', fg='black', bd=1, relief='solid', font=('微软雅黑', 9), padx=6, pady=2)
        btn_choose.pack(side=tk.LEFT)
        btn_skip_dirs = tk.Button(btn_row, text="管理跳过目录", command=self.open_skip_manager,
                                  bg='white', fg='black', bd=1, relief='solid', 
                                  font=('微软雅黑', 9), padx=6, pady=2)
        btn_skip_dirs.pack(side=tk.LEFT, padx=(5,0))
        btn_set_default = tk.Button(btn_row, text="设置默认目录", command=self.open_choose_root_dialog,
                                    bg='white', fg='black', bd=1, relief='solid',
                                    font=('微软雅黑', 9), padx=6, pady=2)
        btn_set_default.pack(side=tk.LEFT, padx=(5,0))
        
        self.btn_full_scan = tk.Button(wechat_header, text="🔍 全盘暴力扫描微信账号", 
                                       command=self.start_full_scan,
                                       bg='#e8f5e9', fg='#2e7d32', bd=1, relief='solid',
                                       font=('微软雅黑', 9, 'bold'), padx=8, pady=3)
        self.btn_full_scan.pack(anchor='w', pady=(8,0))

        # ===== 中间树形目录区 =====
        tree_frame = tk.LabelFrame(self, text="找到的微信账号及文件分类", 
                                   bg=self.LIGHT_PURPLE, fg='black',
                                   font=('黑体', 11, 'bold'), padx=8, pady=5)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        vsb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        self.wechat_tree = ttk.Treeview(tree_frame,
                                        columns=("type", "size"),
                                        show="tree headings",
                                        yscrollcommand=vsb.set,
                                        xscrollcommand=hsb.set)
        self.wechat_tree.heading("#0", text="账号/目录名称")
        self.wechat_tree.heading("type", text="文件类型")
        self.wechat_tree.heading("size", text="大小")

        self.wechat_tree.column("#0", width=250, minwidth=150)
        self.wechat_tree.column("type", width=120, anchor="w")
        self.wechat_tree.column("size", width=100, anchor="e")

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.wechat_tree.pack(fill=tk.BOTH, expand=True)

        self.wechat_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.wechat_tree.bind("<Button-3>", self.show_context_menu)

        # 右键菜单构建
        self.context_menu = tk.Menu(self, tearoff=0, bg=self.LIGHT_PURPLE, fg='black')
        self.context_menu.add_command(label="📋 复制当前路径及ai提示词", command=self.copy_info)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🤖 复制路径并提问【豆包】", 
                                      command=lambda: self.copy_and_open_ai("https://www.doubao.com/chat/"))
        self.context_menu.add_command(label="🤖 复制路径并提问【元宝】", 
                                      command=lambda: self.copy_and_open_ai("https://yuanbao.tencent.com/chat/"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📂 打开所选目录", command=self.open_selected_directory)

        # ===== 底部统计栏区 =====
        stats_frame = tk.LabelFrame(self, text="账号综合占用统计", 
                                    bg=self.LIGHT_PURPLE, fg='black',
                                    font=('黑体', 11, 'bold'), padx=8, pady=5)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_vars = {}
        stats_items = [
            ("总占用", "total", "#333", "聊天记录数据库", "msg", "#d32f2f"),
            ("图片与表情", "image", "#1976d2", "视频文件", "video", "#388e3c"),
            ("接收文件", "file", "#f57c00", "缓存与临时文件", "cache", "#7b1fa2"),
            ("备份文件", "backup", "#e64a19", "其他配置", "other", "#666")
        ]

        for L1, k1, c1, L2, k2, c2 in stats_items:
            row = tk.Frame(stats_frame, bg=self.LIGHT_PURPLE)
            row.pack(fill=tk.X, pady=2)
            
            # 左侧
            tk.Label(row, text=L1, bg=self.LIGHT_PURPLE, fg=c1, font=('微软雅黑', 9), width=12, anchor='w').pack(side=tk.LEFT)
            var1 = tk.StringVar(value="--")
            tk.Label(row, textvariable=var1, bg=self.LIGHT_PURPLE, fg=c1, font=('微软雅黑', 9, 'bold'), width=10, anchor='w').pack(side=tk.LEFT)
            self.stats_vars[k1] = var1
            
            # 占位
            tk.Label(row, text="", bg=self.LIGHT_PURPLE, width=4).pack(side=tk.LEFT)
            
            # 右侧
            tk.Label(row, text=L2, bg=self.LIGHT_PURPLE, fg=c2, font=('微软雅黑', 9), width=12, anchor='w').pack(side=tk.LEFT)
            var2 = tk.StringVar(value="--")
            tk.Label(row, textvariable=var2, bg=self.LIGHT_PURPLE, fg=c2, font=('微软雅黑', 9, 'bold'), anchor='w').pack(side=tk.LEFT)
            self.stats_vars[k2] = var2
        # 悬浮提示初始化
        self.tooltip_label = None
        self.wechat_tree.bind("<Motion>", self._on_tree_mouse_move)
        self.wechat_tree.bind("<Leave>", self._hide_tooltip)

        # 状态栏
        self.status_bar = tk.Label(self, text="准备就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg=self.LIGHT_PURPLE, fg='black', font=('黑体', 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))
        # 状态栏
        self.status_bar = tk.Label(self, text="准备就绪", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   bg=self.LIGHT_PURPLE, fg='black', font=('黑体', 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5,0))
    def _on_tree_mouse_move(self, event):
        """鼠标在树形控件上移动时，检测是否悬浮在文件类型列"""
        region = self.wechat_tree.identify_region(event.x, event.y)
        if region != "cell":
            self._hide_tooltip()
            return
        
        col_id = self.wechat_tree.identify_column(event.x)
        # #1 对应第一列数据「文件类型」，#0是名称列，#2是大小列
        if col_id != "#1":
            self._hide_tooltip()
            return
        
        item_id = self.wechat_tree.identify_row(event.y)
        if not item_id:
            self._hide_tooltip()
            return
        
        full_text = self.wechat_tree.set(item_id, "type")
        # 文字较短时不需要提示
        if len(full_text) <= 10:
            self._hide_tooltip()
            return

        # 创建/更新悬浮提示
        max_wrap = 350  # 提示框最大宽度
        if not self.tooltip_label:
            self.tooltip_label = tk.Label(self, text=full_text, 
                                          bg="#FFFACD", fg="black", 
                                          font=('微软雅黑', 9),
                                          bd=1, relief='solid',
                                          justify='left', wraplength=max_wrap)
        else:
            self.tooltip_label.config(text=full_text)
        
        # 强制更新布局，获取提示框实际尺寸
        self.update_idletasks()
        tip_w = self.tooltip_label.winfo_reqwidth()
        tip_h = self.tooltip_label.winfo_reqheight()
        win_w = self.winfo_width()

        # 计算位置：鼠标右下角偏移
        x = event.x_root - self.winfo_rootx() + 15
        y = event.y_root - self.winfo_rooty() + 15

        # 右边界限制：提示框右端不超出窗口
        if x + tip_w > win_w - 5:
            x = win_w - tip_w - 5
        # 左边界限制
        if x < 5:
            x = 5
        # 下边界限制
        if y + tip_h > self.winfo_height() - 5:
            y = event.y_root - self.winfo_rooty() - tip_h - 10

        self.tooltip_label.place(x=x, y=y)
    def _hide_tooltip(self, event=None):
        """隐藏悬浮提示"""
        if self.tooltip_label:
            self.tooltip_label.place_forget()
    # ========== 核心逻辑 ==========
    def clear_tree(self):
        for item in self.wechat_tree.get_children():
            self.wechat_tree.delete(item)
        self.wechat_node_map.clear()
        self.root_node_ids.clear()
        self.accounts_data.clear()

    def auto_detect_wechat(self):
        try:
            path = detect_default_wechat_path()
            if path:
                self.wechat_root_path = path
                self.wechat_path_var.set(f"检测到默认路径：{path}")
                # 增量添加账号，不清空缓存数据
                accounts = get_wechat_accounts(path)
                for name, full_path in accounts:
                    if full_path not in self.root_node_ids:
                        self._add_wxid_to_tree_and_analyze(full_path, "默认目录")
            else:
                self.wechat_path_var.set("未检测到默认路径，可点击全盘扫描查找")
        except Exception as e:
            self.wechat_path_var.set("路径检测失败，请手动选择")
            print(f"自动检测微信路径异常: {e}")

    def choose_wechat_path(self):
        path = filedialog.askdirectory(title="选择微信WeChat Files文件夹", parent=self)
        if path:
            self.wechat_root_path = path
            self.wechat_path_var.set(f"当前路径：{path}")
            self.load_accounts_from_path(path, "自定义目录")

    def load_accounts_from_path(self, path, source_desc):
        self.clear_tree()
        accounts = get_wechat_accounts(path)
        for name, full_path in accounts:
            self._add_wxid_to_tree_and_analyze(full_path, source_desc)

    def start_full_scan(self):
        if messagebox.askyesno("确认", 
                               "全盘无白名单暴力扫描会遍历所有本地磁盘，可能需要较长时间。期间将一边发现一边分析，是否开始？",
                               parent=self):
            self.scan_stop_event.clear()
            self.btn_full_scan.config(state=tk.DISABLED, text="暴力扫街中...")
            self.clear_tree()
            threading.Thread(target=self._full_scan_thread, daemon=True).start()

    def _full_scan_thread(self):
        def on_found(path):
            drive = os.path.splitdrive(path)[0]
            self.after(0, lambda: self._add_wxid_to_tree_and_analyze(path, f"{drive}盘"))
            
        def on_status(text):
            self.after(0, lambda: self.status_bar.config(text=text))
            
        scan_all_drives_for_wxid(self.scan_stop_event, on_found, on_status)
        self.after(0, self._check_all_threads_completed)

    def _add_wxid_to_tree_and_analyze(self, path, source_desc):
        if path in self.root_node_ids: return
        dir_name = os.path.basename(path)
        
        # 先计算总大小，判断是否疑似
        total_size = get_dir_size(path)
        is_suspect = total_size < SUSPECT_SIZE_THRESHOLD
        
        if is_suspect:
            # 归到疑似分类节点下
            if not hasattr(self, 'suspect_node_id'):
                self.suspect_node_id = self.wechat_tree.insert(
                    '', tk.END, text="📂 疑似小体积账号（<1MB）", 
                    values=("折叠展示", "点击展开"), open=False
                )
            parent_id = self.suspect_node_id
        else:
            parent_id = ''
        
        # 建立根节点
        root_id = self.wechat_tree.insert(parent_id, tk.END, text=f"📁 {dir_name}", 
                                          values=(f"微信账号 ({source_desc})", "[分析中...]"))
        self.wechat_node_map[root_id] = path
        self.root_node_ids[path] = root_id
        
        # 后台深度分析
        threading.Thread(target=self._analyze_account_deep, args=(path, root_id), daemon=True).start()

    def _analyze_account_deep(self, path, root_id):
        stats, sub_nodes = analyze_wechat_account_detailed(path)
        self.accounts_data[path] = stats
        self.after(0, lambda: self._update_tree_with_details(path, root_id, stats, sub_nodes))

    def _update_tree_with_details(self, account_path, root_id, stats, sub_nodes):
        if not self.wechat_tree.exists(root_id): return
        
        total_size_str = human_readable_size(stats['total'])
        current_vals = self.wechat_tree.item(root_id, 'values')
        self.wechat_tree.item(root_id, values=(current_vals[0], total_size_str))
        
        # 递归插入所有层级子节点
        def insert_children(parent_id, children):
            for node in children:
                if node["size"] <= 0:
                    continue
                child_id = self.wechat_tree.insert(
                    parent_id, tk.END,
                    text=f"📁 {node['name']}",
                    values=(node["usage"], human_readable_size(node["size"]))
                )
                self.wechat_node_map[child_id] = node["path"]
                # 继续递归子目录
                if node["children"]:
                    insert_children(child_id, node["children"])
        
        insert_children(root_id, sub_nodes)

        if self.current_wechat_account == account_path:
            self._update_wechat_stats(stats)
    
    
    
    def _check_all_threads_completed(self):
        self.btn_full_scan.config(state=tk.NORMAL, text="🔍 重新暴力扫描")
        self.status_bar.config(text=f"全盘搜寻完成，共找到 {len(self.root_node_ids)} 个微信账号。")
        # 扫描完成立即保存缓存
        self._save_current_cache()

        # 找到多个账号且用户未设置过默认路径时，弹出选择窗口
        if len(self.root_node_ids) > 1:
            user_config = load_user_config()
            if not user_config.get("wechat_root_path"):
                wxid_paths = list(self.root_node_ids.keys())
                self.after(600, lambda: self._show_choose_root_dialog(wxid_paths))

    # ========== UI 交互逻辑 ==========
    def on_tree_select(self, event):
        sel = self.wechat_tree.selection()
        if not sel:
            self.selected_node = None
            return
        
        self.selected_node = sel[0]
        selected_path = self.wechat_node_map.get(self.selected_node)
        
        # 寻找当前选中节点属于哪个账号(Root)
        current = self.selected_node
        while self.wechat_tree.parent(current) != '':
            current = self.wechat_tree.parent(current)
            
        root_path = self.wechat_node_map.get(current)
        if root_path and root_path != self.current_wechat_account:
            self.current_wechat_account = root_path
            stats = self.accounts_data.get(root_path)
            if stats:
                self._update_wechat_stats(stats)

    def _update_wechat_stats(self, result):
        for key, var in self.stats_vars.items():
            size = result.get(key, 0)
            var.set(human_readable_size(size))

    def show_context_menu(self, event):
        item = self.wechat_tree.identify_row(event.y)
        if item:
            self.wechat_tree.selection_set(item)
            self.selected_node = item
            self.context_menu.post(event.x_root, event.y_root)

    def copy_info(self):
        if not self.selected_node: return
        path = self.wechat_node_map.get(self.selected_node)
        if not path: return
        
        type_word = "文件夹" if os.path.isdir(path) else "文件"
        sys_info = get_system_info()
        text = f"{sys_info}\n\n文件夹路径: {path}\n\n这是什么{type_word}，我可以删掉它吗？"
        
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_bar.config(text="✅ 已复制到剪贴板，可直接粘贴给AI")

    def copy_and_open_ai(self, url):
        if not self.selected_node: return
        self.copy_info()
        try:
            webbrowser.open(url)
            self.status_bar.config(text="✅ 已复制，正在打开AI页面...")
        except Exception as e:
            messagebox.showerror("错误", f"打开浏览器失败: {e}")

    def open_selected_directory(self):
        if not self.selected_node: return
        path = self.wechat_node_map.get(self.selected_node)
        if not path: return
        
        target = path if os.path.isdir(path) else os.path.dirname(path)
        try:
            os.startfile(target)
        except AttributeError:
            import subprocess
            if platform.system() == 'Darwin':
                subprocess.Popen(['open', target])
            else:
                subprocess.Popen(['xdg-open', target])

    def open_wechat_root(self):
        if self.wechat_root_path and os.path.exists(self.wechat_root_path):
            os.startfile(self.wechat_root_path)
        else:
            messagebox.showinfo("提示", "未找到微信存储路径")

    def _load_from_cache(self):
        """从缓存直接加载历史数据，无需重新扫描"""
        if not self.cache_data:
            return
        
        loaded_count = 0
        for path, info in self.cache_data.items():
            # 路径不存在的过期缓存自动跳过
            if not os.path.exists(path):
                continue
            
            dir_name = os.path.basename(path)
            source_desc = info.get("source", "历史缓存")
            total_size = info.get("total_size", 0)
            stats = info.get("stats", {})
            children = info.get("children", [])
            
            # 判断是否归为疑似小体积账号
            is_suspect = total_size < SUSPECT_SIZE_THRESHOLD
            if is_suspect:
                if not hasattr(self, 'suspect_node_id'):
                    self.suspect_node_id = self.wechat_tree.insert(
                        '', tk.END, text="📂 疑似小体积账号（<1MB）", 
                        values=("折叠展示", "点击展开"), open=False
                    )
                parent_id = self.suspect_node_id
            else:
                parent_id = ''
            
            # 直接插入树节点，不启动扫描线程
            root_id = self.wechat_tree.insert(
                parent_id, tk.END, 
                text=f"📁 {dir_name}", 
                values=(f"微信账号 ({source_desc})", human_readable_size(total_size))
            )
            self.wechat_node_map[root_id] = path
            self.root_node_ids[path] = root_id
            self.accounts_data[path] = stats
            
            # 递归还原所有层级子目录
            def insert_cached_children(parent_id, children):
                for child in children:
                    child_id = self.wechat_tree.insert(
                        parent_id, tk.END,
                        text=f"📁 {child['name']}",
                        values=(child['usage'], child['size'])
                    )
                    self.wechat_node_map[child_id] = child["path"]
                    if child.get("children"):
                        insert_cached_children(child_id, child["children"])
            
            insert_cached_children(root_id, children)
            loaded_count += 1
        
        if loaded_count > 0:
            self.status_bar.config(text=f"已从缓存加载 {loaded_count} 个微信账号")
    def _save_current_cache(self):
        """保存当前所有扫描结果到缓存文件（含完整嵌套目录树）"""
        cache_data = {}

        def collect_children(parent_id):
            """递归收集所有层级子节点信息"""
            children_info = []
            for child_id in self.wechat_tree.get_children(parent_id):
                item_vals = self.wechat_tree.item(child_id, 'values')
                item_text = self.wechat_tree.item(child_id, 'text').replace("📁 ", "").replace("📄 ", "")
                child_path = self.wechat_node_map.get(child_id, "")
                sub_children = collect_children(child_id)
                children_info.append({
                    "name": item_text,
                    "path": child_path,
                    "usage": item_vals[0],
                    "size": item_vals[1],
                    "children": sub_children
                })
            return children_info

        for path, root_id in self.root_node_ids.items():
            if path in self.accounts_data:
                children_info = collect_children(root_id)
                cache_data[path] = {
                    "source": self.wechat_tree.item(root_id, 'values')[0],
                    "stats": self.accounts_data[path],
                    "children": children_info,
                    "total_size": self.accounts_data[path]["total"]
                }
        save_scan_cache(cache_data)

# ---------- GUI 主应用 (未变更逻辑) ----------
class FolderSizeApp:
    def __init__(self, master):
        self.master = master
        master.title("文件夹大小分析器")
        master.resizable(True, True)

        self.LIGHT_PURPLE = '#B19CD9'
        self.EXTRA_LIGHT_PURPLE = '#F0EBF8'
        self.BTN_BG = 'white'
        self.BTN_FG = 'black'
        self.BTN_HIGHLIGHT = 'black'
        self.TREE_FG = 'black'
        self.CHINESE_FONT = ('黑体', 13)
        self.ENGLISH_FONT = ('Times New Roman', 10)

        title_bar = tk.Frame(master, bg=self.LIGHT_PURPLE, relief='flat', bd=0, height=32)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        title_bar.pack_propagate(False)

        self.title_icon = None
        if PIL_AVAILABLE and os.path.exists(ICON_PATH):
            try:
                img = Image.open(ICON_PATH)
                img = img.resize((20, 20), Image.Resampling.LANCZOS)
                self.title_icon = ImageTk.PhotoImage(img)
                icon_label = tk.Label(title_bar, image=self.title_icon, bg=self.LIGHT_PURPLE)
                icon_label.pack(side=tk.LEFT, padx=(10, 5), pady=2)
                icon_label.bind("<Button-1>", self._start_system_drag)
                icon_label.bind("<Double-Button-1>", self._toggle_max_dblclick)
            except: pass

        title_label = tk.Label(title_bar, text="文件夹大小分析器（极速版）", bg=self.LIGHT_PURPLE, fg='black', font=('黑体', 11, 'bold'))
        title_label.pack(side=tk.LEFT, padx=5, pady=2)

        close_btn = tk.Button(title_bar, text="✕", command=master.destroy, bg=self.LIGHT_PURPLE, fg='black', bd=0, font=('Arial', 12), padx=8, activebackground='#ff6666')
        close_btn.pack(side=tk.RIGHT, padx=5)

        self.max_btn = tk.Button(title_bar, text="□", command=self.toggle_maximize, bg=self.LIGHT_PURPLE, fg='black', bd=0, font=('Arial', 12), padx=8, activebackground='#cccccc')
        self.max_btn.pack(side=tk.RIGHT, padx=2)

        min_btn = tk.Button(title_bar, text="─", command=master.iconify, bg=self.LIGHT_PURPLE, fg='black', bd=0, font=('Arial', 12), padx=8, activebackground='#cccccc')
        min_btn.pack(side=tk.RIGHT, padx=2)

        title_bar.bind("<Button-1>", self._start_system_drag)
        title_bar.bind("<Double-Button-1>", self._toggle_max_dblclick)
        title_label.bind("<Button-1>", self._start_system_drag)
        title_label.bind("<Double-Button-1>", self._toggle_max_dblclick)

        main_frame = tk.Frame(master, bg=self.LIGHT_PURPLE)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.scanner = None
        self.node_path_map = {}
        self.selected_node = None
        self.root_size = 0
        self.current_folder = None
        self.total_files = 0
        self._last_progress_time = 0

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', foreground=self.TREE_FG, background=self.EXTRA_LIGHT_PURPLE, fieldbackground=self.EXTRA_LIGHT_PURPLE, font=('Consolas', 13), rowheight=26)
        style.configure('Treeview.Heading', font=('黑体', 10, 'bold'), foreground='black')

        toolbar = tk.Frame(main_frame, bg=self.LIGHT_PURPLE)
        toolbar.pack(pady=5, fill=tk.X)

        def create_styled_button(parent, text, command):
            font = self.CHINESE_FONT if any('\u4e00' <= c <= '\u9fff' for c in text) else self.ENGLISH_FONT
            return tk.Button(parent, text=text, command=command, font=font, bg=self.BTN_BG, fg=self.BTN_FG, highlightbackground=self.BTN_HIGHLIGHT, highlightcolor=self.BTN_HIGHLIGHT, highlightthickness=2, bd=2, relief='solid', activebackground='#f0f0f0', padx=8, pady=2)

        btn_select = create_styled_button(toolbar, "📁 选择文件夹", self.select_folder)
        btn_select.pack(side=tk.LEFT, padx=5)

        self.btn_scan = create_styled_button(toolbar, "📡 扫描", self.start_scan)
        self.btn_scan.config(state=tk.DISABLED)
        self.btn_scan.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(toolbar, text="就绪", font=self.CHINESE_FONT, fg="green", bg=self.LIGHT_PURPLE)
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.btn_copy = create_styled_button(toolbar, "📋 复制路径+系统信息", self.copy_info)
        self.btn_copy.config(state=tk.DISABLED)
        self.btn_copy.pack(side=tk.LEFT, padx=5)

        btn_geek = create_styled_button(toolbar, "🗑️ 打开geek(卸载)", self.open_geek_uninstaller)
        btn_geek.pack(side=tk.LEFT, padx=5)

        btn_wechat = create_styled_button(toolbar, "💬 微信扫描清理", self.open_wechat_window)
        btn_wechat.pack(side=tk.LEFT, padx=5)

        progress_frame = tk.Frame(main_frame, bg=self.LIGHT_PURPLE)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        self.canvas = tk.Canvas(progress_frame, height=28, bg='white', highlightthickness=1, highlightbackground='gray')
        self.canvas.pack(fill=tk.X)
        self.progress_rect = self.canvas.create_rectangle(0, 0, 0, 28, fill='#4CAF50', outline='')
        self.progress_text = self.canvas.create_text(10, 14, anchor='w', text="准备就绪", font=self.CHINESE_FONT, fill='black')

        tree_frame = tk.Frame(main_frame, bg=self.LIGHT_PURPLE)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        vsb = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        hsb = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(tree_frame, columns=("size", "global_pct", "local_pct"), show="tree headings", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.heading("#0", text="名称")
        self.tree.heading("size", text="大小")
        self.tree.heading("global_pct", text="占根目录%")
        self.tree.heading("local_pct", text="占父目录%")

        self.tree.column("#0", width=480, minwidth=200)
        self.tree.column("size", width=110, anchor="e")
        self.tree.column("global_pct", width=220, anchor="w")
        self.tree.column("local_pct", width=220, anchor="w")

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.context_menu = tk.Menu(main_frame, tearoff=0, bg=self.LIGHT_PURPLE, fg='black')
        self.context_menu.add_command(label="📋 复制当前路径并提问AI", command=self.copy_info)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🤖 复制路径并提问【豆包】", command=lambda: self.copy_and_open_ai("https://www.doubao.com/chat/"))
        self.context_menu.add_command(label="🤖 复制路径并提问【元宝】", command=lambda: self.copy_and_open_ai("https://yuanbao.tencent.com/chat/"))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📂 打开所选目录", command=self.open_selected_directory)

        self.status_bar = tk.Label(main_frame, text="点击「选择文件夹」→ 再点「扫描」", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg=self.LIGHT_PURPLE, fg='black', font=self.CHINESE_FONT)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_wechat_window(self):
        if hasattr(self, 'wechat_window') and self.wechat_window.winfo_exists():
            self.wechat_window.lift()
        else:
            self.wechat_window = WechatScannerWindow(self.master)

    def open_geek_uninstaller(self):
        if not os.path.exists(GEEK_PATH):
            messagebox.showerror("错误", f"未找到 geek.exe\n请将 geek.exe 放在程序同目录下")
            return
        try:
            os.startfile(GEEK_PATH)
            self.status_bar.config(text="✅ 已启动 Geek 卸载工具")
        except Exception as e:
            messagebox.showerror("错误", f"启动失败: {e}")

    def copy_and_open_ai(self, url):
        if not self.selected_node:
            messagebox.showinfo("提示", "请先在树中选择一个文件夹或文件")
            return
        self.copy_info()
        try:
            webbrowser.open(url)
            self.status_bar.config(text="✅ 已复制信息，正在打开AI页面...")
        except Exception as e:
            messagebox.showerror("错误", f"打开浏览器失败: {e}")

    def _start_system_drag(self, event):
        if isinstance(event.widget, tk.Button): return
        if event.num != 1: return
        hwnd = get_real_hwnd(self.master)
        if hwnd:
            ReleaseCapture()
            SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0)

    def _toggle_max_dblclick(self, event):
        if isinstance(event.widget, tk.Button): return
        self.toggle_maximize()

    def toggle_maximize(self):
        if self.master.state() == 'zoomed':
            self.master.state('normal')
            self.max_btn.config(text="□")
        else:
            self.master.state('zoomed')
            self.max_btn.config(text="❐")

    def select_folder(self):
        folder = filedialog.askdirectory(title="选择要扫描的文件夹")
        if not folder: return
        self.current_folder = folder
        self.btn_scan.config(state=tk.NORMAL)
        self.status_label.config(text="已选择文件夹", fg="blue")
        self.status_bar.config(text=f"已选择：{folder}")
        for item in self.tree.get_children(): self.tree.delete(item)
        self.node_path_map.clear()
        self.canvas.coords(self.progress_rect, 0, 0, 0, 28)
        self.canvas.itemconfig(self.progress_text, text="点击「扫描」开始分析")

    def start_scan(self):
        if not self.current_folder: return
        self.btn_scan.config(state=tk.DISABLED)
        self.status_label.config(text="正在扫描...", fg="blue")
        self.status_bar.config(text="扫描中，请勿关闭程序...")
        self.btn_copy.config(state=tk.DISABLED)
        for item in self.tree.get_children(): self.tree.delete(item)
        self.node_path_map.clear()
        threading.Thread(target=self._run_scan, args=(self.current_folder,), daemon=True).start()

    def _update_progress(self, scanned_files, scanned_bytes, current_path):
        now = time.time()
        if now - self._last_progress_time < 0.05: return
        self._last_progress_time = now
        self.master.after(0, self._render_progress, scanned_files, scanned_bytes, current_path)

    def _render_progress(self, scanned_files, scanned_bytes, current_path):
        canvas_width = self.canvas.winfo_width()
        if canvas_width <= 1: canvas_width = 500
        percent = scanned_files / max(self.total_files, 1)
        rect_width = int(canvas_width * percent)
        display_gb = format_gb(scanned_bytes)
        display_path = current_path if len(current_path) < 78 else "..." + current_path[-75:]
        text = f"已扫描 {scanned_files}/{self.total_files} 个文件 · 总计 {display_gb} GB · 当前：{display_path}"
        self.canvas.coords(self.progress_rect, 0, 0, rect_width, 28)
        self.canvas.itemconfig(self.progress_text, text=text)

    def _run_scan(self, folder):
        start_time = time.time()
        try:
            self.scanner = FastScanner(folder, progress_callback=self._update_progress)
            self.total_files = self.scanner.prescan_count()
            self.master.after(0, lambda: self.canvas.itemconfig(self.progress_text, text=f"共计 {self.total_files} 个文件，正在扫描..."))
            self.scanner.scan()
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("错误", f"扫描失败: {e}"))
            self.master.after(0, lambda: self.status_label.config(text="失败", fg="red"))
            self.master.after(0, lambda: self.btn_scan.config(state=tk.NORMAL))
            return
        elapsed = time.time() - start_time
        self.master.after(0, self._fill_root_tree, folder, elapsed)

    def _fill_root_tree(self, folder, elapsed):
        root_path = os.path.abspath(folder)
        root_name = os.path.basename(root_path) + "/"
        self.root_size = self.scanner.get_size(root_path)
        root_size_str = human_readable_size(self.root_size)
        root_id = self.tree.insert('', 'end', text="📁 " + root_name, values=(root_size_str, " 100.0%", "—"), open=True)
        self.node_path_map[root_id] = root_path
        self._load_children(root_id, root_path, self.root_size)
        self.status_label.config(text=f"完成 ({elapsed:.1f}s)", fg="green")
        self.status_bar.config(text=f"共扫描 {self.scanner.scanned_files} 个文件")
        self.btn_scan.config(state=tk.NORMAL)
        canvas_width = self.canvas.winfo_width()
        self.canvas.coords(self.progress_rect, 0, 0, canvas_width, 28)
        self.canvas.itemconfig(self.progress_text, text=f"扫描完成 ✓ 共 {self.scanner.scanned_files} 个文件，{format_gb(self.scanner.scanned_bytes)} GB")

    def _load_children(self, parent_id, parent_path, parent_size):
        for child in self.tree.get_children(parent_id): self.tree.delete(child)
        try: entries = list(os.scandir(parent_path))
        except PermissionError:
            self.tree.insert(parent_id, 'end', text="[权限不足]", values=("", "", ""))
            return
        items = []
        for entry in entries:
            try:
                if entry.is_symlink(): continue
                full_path = entry.path
                sz = self.scanner.get_size(full_path)
                is_dir = entry.is_dir(follow_symlinks=False)
                items.append((entry.name, sz, is_dir, full_path))
            except: continue
        items.sort(key=lambda x: x[1], reverse=True)
        for name, sz, is_dir, full_path in items:
            global_pct = (sz / self.root_size * 100) if self.root_size > 0 else 0
            local_pct = (sz / parent_size * 100) if parent_size > 0 else 0
            size_str = human_readable_size(sz)
            global_bar = self._char_bar(global_pct)
            local_bar = self._char_bar(local_pct)
            icon = "📁 " if is_dir else "📄 "
            node_id = self.tree.insert(parent_id, 'end', text=icon + name + ("/" if is_dir else ""), values=(size_str, global_bar, local_bar), open=False)
            self.node_path_map[node_id] = full_path
            if is_dir: self.tree.insert(node_id, 'end', text="加载中...")

    def on_open_node(self, event):
        node_id = self.tree.focus()
        if not node_id: return
        children = self.tree.get_children(node_id)
        if len(children) == 1 and self.tree.item(children[0], 'text') == "加载中...":
            path = self.node_path_map.get(node_id)
            if path and os.path.isdir(path):
                self._load_children(node_id, path, self.scanner.get_size(path))

    def _char_bar(self, percent, bar_length=15):
        filled = int(percent / 100 * bar_length)
        return '▓' * filled + '░' * (bar_length - filled) + f" {percent:6.1f}%"

    def on_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_node = sel[0]
            self.btn_copy.config(state=tk.NORMAL)
        else:
            self.selected_node = None
            self.btn_copy.config(state=tk.DISABLED)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.selected_node = item
            self.btn_copy.config(state=tk.NORMAL)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_info(self):
        if not self.selected_node: return
        path = self.node_path_map.get(self.selected_node)
        if not path: return
        type_word = "文件夹" if os.path.isdir(path) else "文件"
        text = f"{get_system_info()}\n\n文件夹路径: {path}\n\n这是什么{type_word}，我可以删掉它吗？"
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        self.status_bar.config(text="✅ 已复制到剪贴板，可直接粘贴给AI")

    def open_selected_directory(self):
        if not self.selected_node: return
        path = self.node_path_map.get(self.selected_node)
        if not path: return
        target = path if os.path.isdir(path) else os.path.dirname(path)
        try: os.startfile(target)
        except AttributeError:
            import subprocess
            subprocess.Popen(['open' if platform.system() == 'Darwin' else 'xdg-open', target])


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = FolderSizeApp(root)
    root.update_idletasks()
    
    w, h = 1150, 780
    sw, sh = GetSystemMetrics(SM_CXSCREEN), GetSystemMetrics(SM_CYSCREEN)
    root.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 2)}")
    root.deiconify()
    root.lift()

    def init_window_style():
        remove_titlebar_keep_taskbar(root)
        hwnd = get_real_hwnd(root)
        set_system_icon(hwnd, ICON_PATH)

    root.after(10, init_window_style)

    try: root.mainloop()
    except KeyboardInterrupt: root.quit()