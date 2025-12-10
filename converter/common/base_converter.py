from abc import ABC, abstractmethod
from .javadoc_utils import (
    find_javadoc,
    insert_into_javadoc,
    create_javadoc,
)
from .code_utils import (
    delete_line,
    find_type_definition,
    find_annotation_block_start,
)


class BaseConverter(ABC):

    @abstractmethod
    def get_pattern(self):
        """正则表达式"""
        pass

    @abstractmethod
    def locate_target(self, lines, index, indent):
        """子类根据不同注解决定 javadoc 插入位置"""
        pass

    def convert(self, content):
        lines = content.split("\n")
        i = 0
        count = 0

        pattern = self.get_pattern()

        while i < len(lines):
            line = lines[i]

            m = pattern.search(line)
            if not m:
                i += 1
                continue

            text = m.group(1)
            indent = delete_line(lines, i)
            count += 1

            # 子类决定插入位置
            insert_pos, meta = self.locate_target(lines, i, indent)

            # 查是否已有 javadoc
            start, end = find_javadoc(lines, insert_pos)

            if start is not None:
                insert_into_javadoc(lines, start, text)
            else:
                new_doc = create_javadoc(indent, text, with_meta=meta)
                lines[insert_pos:insert_pos] = new_doc

            i += 1

        return "\n".join(lines), count
