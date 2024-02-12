# AltFN2

アプリケーションランチャ【Windows用】

## コマンドオプション

```shell
python AlfFN2.py [--duplicate_Process_check enable|disable] [--config 設定ファイル]
```

## 設定ファイル

config.json

| #   | 階層 | フィールド名         | 属性      | 必須 | 省略値   | 意味                                     | 備考 |
| --- | ---- | -------------------- | --------- | ---- | -------- | ---------------------------------------- | ---- |
| 1   | 1    | version              | str       |      |          | バージョン                               |      |
| 2   | 1    | actions_after_launch | str       |      | minimize | アプリケーションを起動したあとの処理     |      |
| 3   | 1    | main_window_geometry | obj       |      |          | ウィンドのサイズ・位置                   |      |
| 4   | 2    | height               | int       |      |          | 高さ                                     |      |
| 5   | 2    | width                | int       |      |          | 幅                                       |      |
| 6   | 2    | x                    | int       |      |          | 座標x                                    |      |
| 7   | 2    | y                    | int       |      |          | 座標y                                    |      |
| 8   | 1    | launch_dict          | dict      |      |          | アプリケーション情報                     |      |
| 9   | 2    | 辞書キー             | str       | ◯    |          | ショートカット                           |      |
| 10  | 2    | program_path         | str       | ◯    |          | プログラムパス                           |      |
| 11  | 2    | title                | str       | ◯    |          | タイトル                                 |      |
| 12  | 2    | args                 | list[str] |      |          | コマンドオプション                       |      |
| 13  | 2    | work_dir             | str       |      |          | 作業ディレクトリ                         |      |
| 14  | 2    | shell                | bool      |      | false    | アプリケーションをシェルによって起動する |      |

actions_after_launch

| #   | 値       | 意味           |
| --- | -------- | -------------- |
| 1   | minimize | 最小化。最小化 |
| 2   | exit     | プログラム終了 |
| 3   | none     | 何もしない     |

work_dir
省略時は、program_pathのディレクトリ
