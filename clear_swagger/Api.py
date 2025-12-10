import re
from datetime import datetime

# 匹配 @Api("xxx") 或 @Api(tags="xxx")
API_TAGS_PATTERN = re.compile(
    r'@Api\s*\(\s*tags\s*=\s*"([^"]+)"\s*\)'
)


# 匹配 class / interface / enum / @interface
TYPE_PATTERN = re.compile(r'\b(class|interface|enum|@interface)\b')


def convert_api_tag_to_javadoc(content: str) -> (str, int):
    """
    将 @ApiModel 转为类/接口/注解上的 JavaDoc。
    规则：
    1. 删除 @ApiModel 行
    2. 有现成 JavaDoc：在第一行后插入 “* xxx.” 和一个空行
    3. 没有 JavaDoc：在所有注解之上新建 JavaDoc
    4. 支持 class / interface / enum / @interface / 内部类
    """
    lines = content.split("\n")
    i = 0
    replace_count = 0

    while i < len(lines):
        line = lines[i]

        m = API_TAGS_PATTERN.search(line)
        if not m:
            i += 1
            continue

        value = m.group(1)
        indent = re.match(r"\s*", line).group()

        # 1. 删除当前这一行 @ApiModel
        lines.pop(i)
        replace_count += 1

        # 2. 向下找到对应的类型定义行（class/interface/enum/@interface）
        j = i
        type_index = None
        while j < len(lines):
            stripped = lines[j].strip()
            if TYPE_PATTERN.search(stripped):
                type_index = j
                break
            # 遇到空行或 '}'，认为这个 @ApiModel 不挂在类型上，放弃
            if stripped in ("", "}"):
                break
            j += 1

        if type_index is None:
            # 找不到对应类型，继续往后扫，避免死循环
            i = j
            continue

        # 3. 找类型上方的注解块起点（紧挨着 type 之上的一串 @XXX）
        anno_start = type_index
        while anno_start - 1 >= 0 and lines[anno_start - 1].lstrip().startswith("@"):
            anno_start -= 1

        # 4. 尝试检测是否已经有 JavaDoc（在注解块之上且以 /** 开头，以 */ 结束）
        javadoc_start = None
        javadoc_end = anno_start - 1

        if javadoc_end >= 0 and lines[javadoc_end].strip().endswith("*/"):
            k = javadoc_end
            while k >= 0:
                if lines[k].strip().startswith("/**"):
                    javadoc_start = k
                    break
                k -= 1

        if javadoc_start is not None:
            # === 已有 JavaDoc：在其开头后一行插入 “* xxx.” 和空行 ===
            indent_doc = re.match(r"\s*", lines[javadoc_start]).group()
            insertion = [
                f"{indent_doc} * {value}.",
                f"{indent_doc} *"
            ]
            insert_pos = javadoc_start + 1
            lines[insert_pos:insert_pos] = insertion

        else:
            # === 没有 JavaDoc：在注解块之前新建一个 ===
            today = datetime.now().strftime("%Y-%m-%d")
            new_javadoc = [
                f"{indent}/**",
                f"{indent} * {value}.",
                f"{indent} *",
                f"{indent} * @author kupower",
                f"{indent} * @since {today}",
                f"{indent} */"
            ]
            lines[anno_start:anno_start] = new_javadoc
            # 插入后 type_index 向后偏移了，但我们后面不再用它，直接从原 j 后继续往下扫即可

        # 为避免重复扫描刚插入的注释块，从 type_index 之后继续
        i = type_index + 1

    return "\n".join(lines), replace_count


if __name__ == "__main__":
    fp = input("请输入 Java 文件路径：")
    with open(fp, "r", encoding="utf-8") as f:
        txt = f.read()

    new_txt, total = convert_api_tag_to_javadoc(txt)

    with open(fp, "w", encoding="utf-8") as f:
        f.write(new_txt)

    print(f"ApiModel 转换完成，共替换 {total} 处！")
