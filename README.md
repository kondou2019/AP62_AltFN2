# AltFN2

アプリケーションランチャ【Windows用】

## 設定ファイル

config.json

| #   | 階層 | フィールド名         | 属性      | 必須 | 意味                                     | 備考 |
| --- | ---- | -------------------- | --------- | ---- | ---------------------------------------- | ---- |
| 1   | 1    | version              | str       |      | バージョン                               |      |
| 2   | 1    | actions_after_launch | str       |      | アプリケーションを起動したあとの処理     | ※1   |
| 3   | 1    | main_window_geometry | obj       |      | ウィンドのサイズ・位置                   |      |
| 4   | 2    | height               | int       |      | 高さ                                     |      |
| 5   | 2    | width                | int       |      | 幅                                       |      |
| 6   | 2    | x                    | int       |      | 座標x                                    |      |
| 7   | 2    | y                    | int       |      | 座標y                                    |      |
| 8   | 1    | launch_dict          | dict      |      | アプリケーション情報                     |      |
| 9   | 2    | 辞書キー             | str       | ◯    | ショートカット                           |      |
| 10  | 2    | program_path         | str       | ◯    | プログラムパス                           |      |
| 11  | 2    | title                | str       | ◯    | タイトル                                 |      |
| 12  | 2    | args                 | list[str] |      | コマンドオプション                       |      |
| 14  | 2    | work_dir             | str       |      | 作業ディレクトリ                         | ※2   |
| 15  | 2    | shell                | bool      |      | アプリケーションをシェルによって起動する |      |

※1:actions_after_launch

| #   | 値       | 意味           |
| --- | -------- | -------------- |
| 1   | minimize | 最小化。最小化 |
| 1   | exit     | プログラム終了 |
| 1   | none     | 何もしない     |

※2:work_dir 省略時は、program_pathのディレクトリ
