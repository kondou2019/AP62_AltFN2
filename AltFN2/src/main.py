"""!
@file main.py
"""

import argparse
import dataclasses
from datetime import datetime
from datetime import timedelta
import json
import os
import re
import subprocess
import tkinter
from dataclasses import dataclass, field
from tkinter import messagebox, ttk
from typing import List, Optional, Union
import keyboard

import win32con
import win32gui
from dacite import from_dict

# グローバル変数
__version__ = "0.4.255"
g_args = argparse.Namespace()  # コマンド引数。ダミー初期化

#


@dataclass(kw_only=True)
class WindowGeometry:
    width: int = 0
    height: int = 0
    x: int = 0
    y: int = 0


@dataclass(kw_only=True)
class Launch:
    title: str = ""
    program_path: str  # プログラムパス
    args: Optional[list[str]]  # コマンドオプション
    work_dir: Optional[str]  # 作業ディレクトリ
    shell: Optional[bool]  # アプリケーションをシェルによって起動する


@dataclass(kw_only=True)
class Variable:
    name: str = ""
    value: str = ""


@dataclass(kw_only=True)
class Config:
    version: str = ""
    main_window_geometry: WindowGeometry = field(default_factory=WindowGeometry)
    actions_after_launch: Optional[str] = None  # アプリケーションを起動したあとの処理
    # "minimize":最小化,"exit":プログラム終了,"none":何もしない
    active_key_interval: int = 300  # ウィンドウがアクティブになってから一定時間キー入力を無視する
    font_name: str = "ＭＳ ゴシック"
    font_size: int = 12
    hotkey: str ="" # ショートカットキー
    variable_list: list[Variable] = field(default_factory=list)
    launch_dict: dict[str, Launch] = field(default_factory=dict)


class MainWindow(tkinter.Tk):
    """!
    @brief メインウィンド
    """

    def __init__(self, *, config_path: str = ""):
        super().__init__()
        #
        self.config_path = config_path
        self.config_data = Config()
        self.launch_key: str = ""
        #
        self.key_event_modifier_last_time: int = 0  # 修飾キーの最終入力時刻
        self.key_event_character_last_time: int = 0  # 文字キーの最終入力時刻
        self.key_event_last_char: str = ""  # キー入力の最終文字
        self.visiblility_time: datetime = datetime.now() # ウィンドウの表示時刻
        #
        self.config_read()
        self.MainWindow_load()
        # ショートカットキーを登録
        if self.config_data.hotkey != "":
            keyboard.add_hotkey(self.config_data.hotkey, self.show_window)

    # ====================#
    # 外部インタフェース #
    # ====================#

    # ==========#
    # 内部処理 #
    # ==========#

    def config_read(self):
        config_path = self.config_path
        # 設定ファイルの読み込み
        if os.path.isfile(config_path) == False:
            messagebox.showerror("エラー", f"設定ファイルが見つかりません。\nconfig={config_path}")
            return 1
        with open(config_path, mode="r", encoding="utf-8") as f:
            try:
                json_dic = json.load(f)
            except Exception as e:
                messagebox.showinfo("エラー", f"設定ファイルの読み込みに失敗しました。\nconfig:{config_path}\n詳細:{e}")
                return 1
        config = from_dict(data_class=Config, data=json_dic)
        self.config_data = config

    def config_write(self):
        self.config_data.version = __version__
        # ウィンド位置の更新
        x = self.winfo_x()
        y = self.winfo_y()
        width = self.winfo_width()
        height = self.winfo_height()
        self.config_data.main_window_geometry.width = width
        self.config_data.main_window_geometry.height = height
        self.config_data.main_window_geometry.x = x
        self.config_data.main_window_geometry.y = y
        # 設定ファイル更新
        json_dic = dataclasses.asdict(self.config_data)
        remove_none_keys(json_dic)  # Noneのキーを削除
        json_data = json.dumps(json_dic, indent=4, sort_keys=True, ensure_ascii=False)
        with open(self.config_path, mode="w", encoding="utf-8") as f:
            f.write(json_data)

    def exec_program(self, launch: Launch) -> bool:
        cmd: list[str] = []
        #
        program_path = self.replace_variable(launch.program_path)
        if os.path.isfile(program_path) == False:
            messagebox.showerror("エラー", f"ファイルが見つかりません。\nprogram_path={program_path}")
            return False
        cmd.append(program_path)
        if launch.args is not None:
            for arg in launch.args:
                cmd.append(self.replace_variable(arg))
        #
        if launch.work_dir is not None:
            work_dir = self.replace_variable(launch.work_dir)
            if os.path.isdir(work_dir) == False:
                messagebox.showerror("エラー", f"ディレクトリが見つかりません。\nwork_dir={work_dir}")
                return False
            cwd = work_dir
        else:
            cwd = os.path.dirname(program_path)
        #
        if launch.shell is not None and launch.shell == True:
            bShell = True
        else:
            bShell = False
        try:
            # rc = subprocess.call(cmd, shell=True)
            _process = subprocess.Popen(cmd, cwd=cwd, shell=bShell)
        # except NotADirectoryError as e: # 実行パスが間違っている
        #    messagebox.showerror("エラー", f"パスが無効\nprogram_path={program_path}")
        except Exception as e:
            messagebox.showerror("エラー", f"その他エラー。\n詳細:{e}")
            return False
        # 画面クリア
        self.launch_key = ""
        self.key_label["text"] = ""
        self.title_label["text"] = ""
        self.update_launch_table()
        # アプリケーションの起動後
        if self.config_data.actions_after_launch is None or self.config_data.actions_after_launch == "minimize":
            self.iconify()  # 最小化
        elif self.config_data.actions_after_launch == "none":
            pass
        elif self.config_data.actions_after_launch == "exit":
            self.destroy()
        return True

    def replace_variable(self, s: str) -> str:
        """!
        @brief 変数を置換する。設定変数と環境変数
        @param[in] s 置換元文字列
        @return 置換後文字列
        @detail 置換対象は%ENV%形式。環境変数が存在しない場合は置換しない。
        """
        matches = re.findall(r"%([^%]+)%", s)
        for match in matches:
            value = next((x.value for x in self.config_data.variable_list if x.name == match), None)
            if value is None:# 環境変数なし?
                value = os.environ.get(match)  # 環境変数
            if value is not None:
                s = s.replace(f"%{match}%", value)
        return s

    def show_window(self):
        check_duplicate_process()

    def update_launch_table(self, matching_keys: Optional[list[str]] = None):
        self.launch_table.delete(*self.launch_table.get_children())  # 全削除
        if matching_keys is None:  # 全表示
            matching_keys = self.config_data.launch_dict.keys()
        elif len(matching_keys) == 0:
            return
        for key in matching_keys:
            launch = self.config_data.launch_dict[key]
            self.launch_table.insert(parent="", index="end", values=(key, launch.title))

    # ===================#
    # GUIイベント,Window #
    # ===================#
    def MainWindow_load(self):
        # self.title("(無題) - AltFN2")
        self.title(f"{self.config_path} - AltFN2")
        if self.config_data.main_window_geometry.width == 0 and self.config_data.main_window_geometry.height == 0:
            self.geometry("512x512")
        else:
            self.geometry(
                f"{self.config_data.main_window_geometry.width}x{self.config_data.main_window_geometry.height}+{self.config_data.main_window_geometry.x}+{self.config_data.main_window_geometry.y}"
            )
        # メニュー
        menu = tkinter.Menu(self)

        menu_file = tkinter.Menu(menu, tearoff=0)
        menu_file.add_command(label="終了", command=self.on_menu_file_exit_click)
        menu.add_cascade(label="ファイル", menu=menu_file)

        menu_tool = tkinter.Menu(menu, tearoff=0)
        menu_tool.add_command(
            label="クリップボードの文字列をJSON文字列に更新", command=self.on_menu_tool_clipboard_json_click
        )
        menu_tool.add_command(
            label="クリップボードの文字列のパス区切り文字を'/'に置換", command=self.on_menu_tool_clipboard_path_separate_click
        )
        menu_tool.add_separator()
        menu_tool.add_command(label="ウィンドサイズと位置を保存", command=self.on_menu_tool_save_windows_click)
        menu_tool.add_separator()
        menu_tool.add_command(label="設定ファイルを開く", command=self.on_menu_tool_open_config_click)
        menu_tool.add_command(label="設定ファイルの再読み込み", command=self.on_menu_tool_reload_config_click)
        menu.add_cascade(label="ツール", menu=menu_tool)

        menu_help = tkinter.Menu(menu, tearoff=0)
        menu_help.add_command(label="バージョン情報...", command=self.on_menu_help_about_click)
        menu.add_cascade(label="ヘルプ", menu=menu_help)

        self.config(menu=menu)
        # メインフレーム
        main_frm = ttk.Frame(self)
        # コントロール
        frame1 = ttk.Frame(self)

        font = (self.config_data.font_name, self.config_data.font_size)
        label0 = ttk.Label(frame1, text="key:", font=font)
        self.key_label = ttk.Label(frame1, text="", font=(self.config_data.font_name, self.config_data.font_size, "bold"))
        label1 = ttk.Label(frame1, text="title:", font=font)
        self.title_label = ttk.Label(frame1, text="", font=font)

        label0.grid(column=0, row=0, sticky=tkinter.E)
        self.key_label.grid(column=1, row=0, sticky=tkinter.W)
        label1.grid(column=0, row=1, sticky=tkinter.E)
        self.title_label.grid(column=1, row=1, sticky=tkinter.W)

        #self.key_label.pack(expand=True, fill=tkinter.X)
        #self.title_label.pack(expand=True, fill=tkinter.X)
        frame1.pack(fill=tkinter.X)  # フレームそのものを拡張
        #
        frame2 = ttk.Frame(self)
        table_column = ("key", "title")
        self.launch_table = ttk.Treeview(frame2, columns=table_column)
        # self.launch_table.grid(column=0, row=2, sticky=tkinter.NSEW)
        self.launch_table.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        frame2.pack(expand=True, fill=tkinter.BOTH)
        # 列の設定
        self.launch_table.column("#0", width=0, stretch="no")
        self.launch_table.column("key", anchor=tkinter.W, width=100)
        self.launch_table.column("title", anchor=tkinter.W, width=400)
        # 列の見出し設定
        self.launch_table.heading("#0", text="")
        self.launch_table.heading("key", text="key", anchor=tkinter.CENTER)
        self.launch_table.heading("title", text="title", anchor=tkinter.CENTER)
        # スクロールバー
        self.scrollbar_launch_table = ttk.Scrollbar(frame2, orient=tkinter.VERTICAL, command=self.launch_table.yview)
        self.launch_table.configure(yscroll=self.scrollbar_launch_table.set)
        self.scrollbar_launch_table.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        # イベント
        self.launch_table.bind("<Double 1>", self.on_launch_table_double_click)  # マウスを左クリックしたときの動作
        self.bind('<Visibility>', self.on_visibility)
        # 初期描画
        self.update_launch_table()
        self.bind("<KeyRelease>", self.key_event)
        # self.bind("<KeyRelease>", self.key_event_debug)
        # self.bind("<KeyPress>", self.key_event_debug)
        # self.bind("<Key>", self.key_event_debug)

    # ===================#
    # GUIイベント(menu) #
    # ===================#
    def on_menu_file_exit_click(self) -> None:
        self.destroy()

    def on_menu_help_about_click(self) -> None:
        messagebox.showinfo("バージョン情報", f"AltFN2 {__version__}")

    def on_menu_tool_clipboard_json_click(self) -> None:
        s = self.clipboard_get()
        escaped_string = json.dumps(s, ensure_ascii=False)
        self.clipboard_clear()
        self.clipboard_append(escaped_string)

    def on_menu_tool_clipboard_path_separate_click(self) -> None:
        s = self.clipboard_get()
        slashed_string = s.replace("\\", "/")
        self.clipboard_clear()
        self.clipboard_append(slashed_string)

    def on_menu_tool_open_config_click(self) -> None:
        subprocess.Popen(["notepad", self.config_path])

    def on_menu_tool_reload_config_click(self) -> None:
        self.config_read()
        self.update_launch_table()

    def on_menu_tool_save_windows_click(self) -> None:
        self.config_write()

    # ==========================#
    # GUIイベント,ウィジェット #
    # ==========================#
    def on_launch_table_double_click(self, e) -> None:
        print(e)
        record_id = self.launch_table.focus()
        record_values = self.launch_table.item(record_id, "values")
        #
        self.launch_key = record_values[0]
        launch = self.config_data.launch_dict[self.launch_key]
        self.exec_program(launch)

    def on_visibility(self, e) -> None:
        if e.widget == self: # メインウィンド?
            self.visiblility_time: datetime = datetime.now()

    def key_event_debug(self, e) -> None:
        with open("debug.log", mode="a", encoding="utf-8") as f:
            f.write(f"keysym={e.keysym},char={e.char},delta={e.delta},time={e.time}")
            # f.write(str(e))
            f.write("\n")
        # self.key_event(e)

    def key_event(self, e) -> None:
        keysym = e.keysym
        # ショートカットキーの入力による誤入力を防ぐ
        # ウィンドウが表示されてから一定時間が経過していない場合は無視
        if (datetime.now() - self.visiblility_time) < timedelta(milliseconds=self.config_data.active_key_interval):
            return
        # キー入力
        if keysym == "BackSpace":
            self.key_label["text"] = self.key_label["text"][:-1]
        elif keysym == "Escape":
            # elif e.keysym in ["Escape", "Alt_L", "Control_L", "Shift_L"]: # ショートカットキーの場合にクリアする
            self.key_label["text"] = ""
        elif keysym == "Return":
            if self.launch_key != "":
                launch = self.config_data.launch_dict[self.launch_key]
                self.exec_program(launch)
            elif self.key_label["text"] != "": # 途中まで入力している場合
                pass
            else: # キーが無い場合。
                self.iconify()  # 最小化
        elif e.char != "":  # 文字キーの入力
            self.key_label["text"] += e.char
        else:  # 文字キー以外の入力は無視
            return
        #
        self.title_label["text"] = ""
        self.launch_key = ""
        prefix = self.key_label["text"]
        self.key_label.config(foreground="black")
        #
        matching_keys = [key for key in self.config_data.launch_dict.keys() if key.startswith(prefix)]
        self.update_launch_table(matching_keys)
        if prefix in self.config_data.launch_dict:  # 完全一致
            self.launch_key = prefix
        elif len(matching_keys) == 1:  # 完全前方一致
            self.launch_key = matching_keys[0]
        else:
            self.key_label.config(foreground="red")
        #
        if self.launch_key != "":
            launch = self.config_data.launch_dict[self.launch_key]
            self.title_label["text"] = launch.title


def analyze_option(argv: List[str]) -> argparse.Namespace:
    """!
    @brief コマンドラインオプションの解析
    @param[in] argv コマンドラインオプション
    @return argparse.namespace コマンドラインオプション解析結果
    """
    parser = argparse.ArgumentParser(
        prog="AltFN2",
        usage="アプリケーションランチャ",
        epilog="end",
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--disable_duplicate_process_check",
        action="store_true",
        help="2重起動防止チェックの無効化",
    )
    parser.add_argument(
        "--config",
        action="store",
        type=str,
        default="config.json",
        help=r"設定ファイル",
    )
    # if len(argv) == 1: # オプション無し実行
    #    parser.print_help()
    #    sys.exit(1)
    args = parser.parse_args(argv[1:])
    return args


def remove_none_keys(d: Union[dict, list[dict]]):
    """!
    @brief 辞書からNoneの値をもつキーを取り除く
    @param[in] d 辞書または辞書のリスト
    """
    if isinstance(d, dict):
        for k, v in list(d.items()):  # 削除するのでlistに変換してからループする
            if v is None:
                del d[k]
            elif isinstance(v, dict):
                remove_none_keys(v)
    elif isinstance(d, list):
        for item in d:
            remove_none_keys(item)
    else:
        raise TypeError("引数:d")
    return d


def replace_env(s: str) -> str:
    """!
    @brief 環境変数を置換する
    @param[in] s 置換元文字列
    @return 置換後文字列
    @detail 置換対象は%ENV%形式。環境変数が存在しない場合は置換しない。
    """
    matches = re.findall(r"%([^%]+)%", s)
    for match in matches:
        value = os.environ.get(match)
        if value is not None:
            s = s.replace(f"%{match}%", value)
    return s



find_hwnd: int = 0


def callback_EnumWindows_window_text_suffix(hwnd, title_suffix) -> bool:
    """!
    @brief ウィンドハンドルを探す。テキストのサフィックス
    @detail win32gui.EnumWindows()のコールバック関数。一致したhwndをfind_hwndにセット。
    @param hwnd コマンドラインオプション
    @param title_suffix 検索対象のサフィックス
    @retval True 継続
    @retval False 中断
    """
    global find_hwnd
    if find_hwnd != 0:
        return True  # 中断したいが落ちるので継続
    name = win32gui.GetWindowText(hwnd)
    if name.endswith(title_suffix):
        # print(f"{hwnd}:{name}")
        find_hwnd = hwnd
        # return False # 列挙終了。なんか落ちる
    return True  #  継続


def check_duplicate_process() -> int:
    """!
    @brief 2重起動防止
    @retval 0 2重起動していない
    @retval 1 既に起動している
    """
    # キャッシュファイルから探す
    exec_dir = os.path.dirname(os.path.abspath(__file__))
    hwnd_path = os.path.join(exec_dir, "AltFN2.hwnd")
    if os.path.isfile(hwnd_path):
        with open(hwnd_path, mode="r", encoding="utf-8") as f:
            hwnd = int(f.read())
        window_title = win32gui.GetWindowText(hwnd)
        if window_title.endswith(" - AltFN2"):
            win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)
            win32gui.SetForegroundWindow(hwnd)
            return 1
    # ウィンドウを探す
    win32gui.EnumWindows(callback_EnumWindows_window_text_suffix, " - AltFN2")
    if find_hwnd != 0:
        # キャッシュファイルに保存
        with open(hwnd_path, mode="w", encoding="utf-8") as f:
            f.write(str(find_hwnd))
        # ウィンドウをアクティブにする
        win32gui.ShowWindow(find_hwnd, win32con.SW_NORMAL)
        win32gui.SetForegroundWindow(find_hwnd)
        return 1
    return 0


def main(argv: List[str]) -> int:
    """!
    @brief 主入口点
    @param argv コマンドラインオプション
    @retval 0 成功
    @retval 1 失敗
    """
    # 2重起動防止
    if len(argv) >= 2 and argv[1] != "--disable_duplicate_process_check":
        rc = check_duplicate_process()
        if rc != 0:
            return 0
    # オプション解析
    args = analyze_option(argv)
    global g_args
    g_args = args
    # ウィンドの表示
    win = MainWindow(config_path=args.config)
    win.mainloop()
    return 0
