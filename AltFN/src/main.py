#!/usr/bin/env python
"""!
@file main.py
@brie アプリケーションランチャ
@retval 0 - 成功
@retval 1 - 失敗
"""
import argparse
import dataclasses
import json
import os
import subprocess
import sys
import tkinter
from dataclasses import dataclass, field
from tkinter import messagebox, ttk
from typing import List, Optional

from dacite import from_dict


@dataclass(kw_only=True)
class WindowGeometry:
    width: int = 0
    height: int = 0
    x: int = 0
    y: int = 0


@dataclass(kw_only=True)
class Launch:
    # key: str = "" # ショートカット
    title: str = ""
    program_path: str  # プログラムパス
    args: Optional[list[str]]  # オプション
    work_dir: Optional[str]  # 作業ディレクトリ


@dataclass(kw_only=True)
class Config:
    version: str = ""
    main_window_geometry: WindowGeometry = field(default_factory=WindowGeometry)
    launch_exit: bool = False  # プログラムを起動したあとに終了する
    launch_dict: dict[str, Launch] = field(default_factory=dict)


# グローバル変数
__version__ = "0.1.0.0"
g_args = argparse.Namespace()  # コマンド引数。ダミー初期化


class MainWindow(tkinter.Tk):
    """!
    @brie メインウィンド
    """

    def __init__(self, *, config_path: str = ""):
        super().__init__()
        #
        self.config_path = config_path
        self.config_data = Config()
        self.launch_key: str = ""
        #
        self.config_read()
        self.MainWindow_load()

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
        x = self.winfo_x()
        y = self.winfo_y()
        width = self.winfo_width()
        height = self.winfo_height()
        #
        self.config_data.main_window_geometry.width = width
        self.config_data.main_window_geometry.height = height
        self.config_data.main_window_geometry.x = x
        self.config_data.main_window_geometry.y = y
        # 設定ファイル更新
        json_dic = dataclasses.asdict(self.config_data)
        json_data = json.dumps(json_dic, indent=4, sort_keys=True, ensure_ascii=False)
        with open(self.config_path, mode="w", encoding="utf-8") as f:
            f.write(json_data)

    def exec_program(self, launch: Launch) -> bool:
        cmd: list[str] = []
        #
        if os.path.isfile(launch.program_path) == False:
            messagebox.showerror("エラー", f"ファイルが見つかりません。\nprogram_path={launch.program_path}")
            return False
        cmd.append(launch.program_path)
        if launch.args is not None:
            cmd.extend(launch.args)
        #
        # cwd = os.path.basename(launch.program_path)
        if launch.work_dir is not None:
            if os.path.isdir(launch.work_dir) == False:
                messagebox.showerror("エラー", f"ディレクトリが見つかりません。\nwork_dir={launch.work_dir}")
                return False
            cwd = launch.work_dir
        else:
            cwd = os.path.dirname(launch.program_path)
        # rc = subprocess.call(cmd, shell=True)
        try:
            # _process = subprocess.Popen(cmd, cwd=cwd, shell=True)
            _process = subprocess.Popen(cmd, cwd=cwd)
        # except NotADirectoryError as e: # 実行パスが間違っている
        #    messagebox.showerror("エラー", f"パスが無効\nprogram_path={launch.program_path}")
        except Exception as e:
            messagebox.showerror("エラー", f"その他エラー。\n詳細:{e}")
        #
        return True

    def update_launch_table(self, matching_keys: list[str]):
        self.launch_table.delete(*self.launch_table.get_children())  # 全削除
        if len(matching_keys) == 0:
            matching_keys = self.config_data.launch_dict.keys()
        for key in matching_keys:
            launch = self.config_data.launch_dict[key]
            self.launch_table.insert(parent="", index="end", values=(key, launch.title))

    # ===================#
    # GUIイベント,Window #
    # ===================#
    def MainWindow_load(self):
        # self.title("(無題) - AltFN")
        self.title(f"{self.config_path} - AltFN")
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
        menu_tool.add_separator()
        menu_tool.add_command(label="ウィンドサイズと位置を保存", command=self.on_menu_tool_save_windows_click)
        menu_tool.add_separator()
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
        self.key_label = ttk.Label(frame1, text="")
        self.title_label = ttk.Label(frame1, text="")
        self.key_label.pack(expand=True, fill=tkinter.X)
        self.title_label.pack(expand=True, fill=tkinter.X)
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
        # 初期描画
        self.update_launch_table([])
        self.bind("<KeyRelease>", self.key_event)

    # ===================#
    # GUIイベント(menu) #
    # ===================#
    def on_menu_file_exit_click(self) -> None:
        self.destroy()

    def on_menu_help_about_click(self) -> None:
        messagebox.showinfo("バージョン情報", f"AltFN {__version__}")

    def on_menu_tool_clipboard_json_click(self) -> None:
        s = self.clipboard_get()
        escaped_string = json.dumps(s, ensure_ascii=False)
        self.clipboard_clear()
        self.clipboard_append(escaped_string)

    def on_menu_tool_reload_config_click(self) -> None:
        self.config_read()
        self.update_launch_table([])

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

    def key_event(self, e) -> None:
        if e.keysym == "BackSpace":
            self.key_label["text"] = self.key_label["text"][:-1]
        elif e.keysym == "Escape":
            self.key_label["text"] = ""
        elif e.keysym == "Return":
            if self.launch_key != "":
                launch = self.config_data.launch_dict[self.launch_key]
                self.exec_program(launch)
                #
                self.launch_key = ""
                self.key_label["text"] = ""
                self.title_label["text"] = ""
                self.update_launch_table([])
                #
                # self.iconify() # 最小化
                if self.config_data.launch_exit == True:
                    self.destroy()
                return
        elif e.char != "":  # 文字キーの入力
            self.key_label["text"] += e.keysym
        else:  # 文字キー以外の入力は無視
            return
        #
        self.title_label["text"] = ""
        prefix = self.key_label["text"]
        matching_keys = [key for key in self.config_data.launch_dict.keys() if key.startswith(prefix)]
        self.update_launch_table(matching_keys)
        if len(matching_keys) == 1:
            self.launch_key = matching_keys[0]
            launch = self.config_data.launch_dict[self.launch_key]
            self.title_label["text"] = launch.title


def analyze_option(argv: List[str]) -> argparse.Namespace:
    """!
    @brief コマンドラインオプションの解析
    @param[in] argv コマンドラインオプション
    @return argparse.namespace コマンドラインオプション解析結果
    """
    parser = argparse.ArgumentParser(
        prog="AltFN",
        usage="アプリケーションランチャ",
        epilog="end",
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter,
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


def main(argv: List[str]) -> int:
    """!
    @brief 主入口点
    @param argv コマンドラインオプション
    @retval 0 成功
    @retval 1 失敗
    """
    # オプション解析
    args = analyze_option(argv)
    global g_args
    g_args = args
    # ウィンドの表示
    win = MainWindow(config_path=args.config)
    win.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
