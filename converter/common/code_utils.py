import re
from .patterns import TYPE_PATTERN


def delete_line(lines, index):
    """删除指定行，并返回删除行的缩进"""
    indent = re.match(r"\s*", lines[index]).group()
    lines.pop(index)
    return indent


def find_type_definition(lines, i):
    """
    向下查找 class/interface/enum/@interface
    """
    j = i
    while j < len(lines):
        stripped = lines[j].strip()
        if TYPE_PATTERN.search(stripped):
            return j
        if stripped in ("", "}"):
            return None
        j += 1
    return None


def find_annotation_block_start(lines, index):
    """
    向上寻找连续 @ 注解块的开始位置
    """
    pos = index
    while pos - 1 >= 0 and lines[pos - 1].lstrip().startswith("@"):
        pos -= 1
    return pos
