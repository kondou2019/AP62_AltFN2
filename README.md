# AltFN2

アプリケーションランチャ【Windows用】

## コマンドオプション

```shell
python AlfFN2.py [--disable_duplicate_process_check] [--config 設定ファイル]
```

### --disable_duplicate_process_check

2重起動防止機能を無効にする。  
--disable_duplicate_process_checkは先頭に指定してください。



## 一時ファイル

| #   | ファイル名  | 用途                            | 備考 |
| --- | ----------- | ------------------------------- | ---- |
| 1   | AltFN2.hwnd | 2重起動防止用のhwnd保存ファイル |      |

## 設定ファイル

config.json

| #   | 階層 | フィールド名         | 属性 | 必須 | 省略値        | 意味                                 | 備考 |
| --- | ---- | -------------------- | ---- | ---- | ------------- | ------------------------------------ | ---- |
| 1   | 1    | version              | str  |      |               | バージョン                           |      |
| 2   | 1    | actions_after_launch | str  |      | minimize      | アプリケーションを起動したあとの処理 |      |
| 3   | 1    | active_key_interval  | int  |      | 300           | ウィンドウがアクティブになってから一定時間キー入力を無視する |      |
| 4   | 1    | font_name            | str  |      | ＭＳ ゴシック | 表示フォント名                           |      |
| 5   | 1    | font_size            | int  |      | 12            | 表示フォントサイズ                       |      |
| 6   | 1    | hotkey               | bool |      |               | ホットキーの有無                         |      |
| 7   | 1    | main_window_geometry | obj       |      |          | ウィンドのサイズ・位置                   |      |
| 8   | 2    | height               | int       |      |          | 高さ                                     |      |
| 9   | 2    | width                | int       |      |          | 幅                                       |      |
| 10   | 2    | x                    | int       |      |          | 座標x                                    |      |
| 11   | 2    | y                    | int       |      |          | 座標y                                    |      |
| 12  | 1    | variable_list        | list[obj] |      |          | 設定変数                                 |      |
| 13  | 2    | name                 | str       |      |          | 変数の名称                               |      |
| 14  | 2    | value                | str       |      |          | 変数の値                                 |      |
| 15  | 1    | launch_dict          | dict      |      |          | アプリケーション情報                     |      |

actions_after_launch

| #   | 値       | 意味           |
| --- | -------- | -------------- |
| 1   | minimize | 最小化。最小化 |
| 2   | exit     | プログラム終了 |
| 3   | none     | 何もしない     |

launch_dict

| #   | 階層 | フィールド名 | 属性      | 必須 | 省略値 | 意味                                     | 備考 |
| --- | ---- | ------------ | --------- | ---- | ------ | ---------------------------------------- | ---- |
| 1   | 1    | 辞書キー     | str       | ◯    |        | ショートカット                           |      |
| 2   | 2    | program_path | str       | ◯    |        | プログラムパス ※1                       |      |
| 3   | 2    | title        | str       | ◯    |        | タイトル                                 |      |
| 4   | 2    | args         | list[str] |      |        | コマンドオプション ※1                   |      |
| 5   | 2    | work_dir     | str       |      |        | 作業ディレクトリ ※1                     |      |
| 6   | 2    | shell        | bool      |      | false  | アプリケーションをシェルによって起動する |      |

※1 環境変数指定が可能(%LOCALAPPDATA%形式)

work_dir
省略時は、program_pathのディレクトリ
