import re
from datetime import datetime

START = re.compile(r'\s*/\*\*')
END = re.compile(r'\s*\*/')


def find_javadoc(lines, index):
    """
    检查 index 上方是否存在 javadoc
    返回 (javadoc_start, javadoc_end)
    """
    j = index - 1
    if j < 0 or not END.search(lines[j]):
        return None, None

    end_index = j
    k = j - 1
    while k >= 0:
        if START.search(lines[k]):
            return k, end_index
        k -= 1

    return None, None


def insert_into_javadoc(lines, start, text):
    """在已有 javadoc 内部插入描述"""
    indent = get_indent(lines[start])
    insertion = [f"{indent} * {text}.", f"{indent} *"]
    lines[start + 1:start + 1] = insertion


def create_javadoc(indent, text, with_meta=False):
    """返回一个 javadoc block"""
    today = datetime.now().strftime("%Y-%m-%d")

    if with_meta:
        return [
            f"{indent}/**",
            f"{indent} * {text}.",
            f"{indent} *",
            f"{indent} * @author kupower",
            f"{indent} * @since {today}",
            f"{indent} */",
        ]
    else:
        return [
            f"{indent}/**",
            f"{indent} * {text}.",
            f"{indent} */",
        ]


def get_indent(line: str):
    """返回代码行前导空格"""
    return re.match(r"\s*", line).group()
