import configparser
import json
import dataclasses
import pytest

from src.main import Config, Launch, remove_none_keys

def split_string_quotes(s:str) -> list[str]:
    """スペース区切りで分割する。
    ダブルクォートで囲まれた部分のスペースは無視する。
    クォート文字は削除する。
    """
    result = []
    quote = False
    value = ""
    for c in s:
        if c == '"':
            quote = not quote
        elif c == ' ' and not quote:
            result.append(value)
            value = ""
        else:
            value += c
    result.append(value)
    return result

@pytest.mark.skip
def test_convert_config():
    config = configparser.ConfigParser()
    config.read('D:/tmp/entry_program.ini')
    #config.read('D:/tmp/entry_program_quote.ini')
    #
    config2 = Config()
    for section in config.sections():
        dic = {k: v for k, v in config.items(section)}
        #print("Section:", section)
        key = section
        title = config.get(section, "Comment")
        program_path = config.get(section, "Program")
        work_dir = None
        if "workdir" in dic:
            work_dir = dic["workdir"]
        args = None
        if "programswitch" in dic:
            s = dic["programswitch"]
            args = split_string_quotes(s)
        launch = Launch(title=title, program_path=program_path, work_dir=work_dir,args=args, shell=None)
        config2.launch_dict[key] = launch
    #
    # 設定ファイル更新
    json_dic = dataclasses.asdict(config2)
    remove_none_keys(json_dic)  # Noneのキーを削除
    json_data = json.dumps(json_dic, indent=4, sort_keys=True, ensure_ascii=False)
    with open(f"D:/tmp/entry_program.json", mode="w", encoding="utf-8") as f:
        f.write(json_data)
    pass

@pytest.mark.parametrize('test_id, val, expected', [
     ('0101N', 'a', ['a']),
     ('0102N', 'a b', ['a', 'b']),
     ('0103N', 'a "b"', ['a', 'b']),
     ('0104N', 'a "b c" d', ['a', 'b c', 'd']),
     ('0104N', 'a --d="b c" d', ['a', '--d=b c', 'd']),
    ])
def test_split_string_quotes_0001X(test_id:str, val:str, expected:list[str]):
    result = split_string_quotes(val)
    assert result == expected
