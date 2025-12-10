# ================================
# swagger的ApiModelProperty -> 注释
# ================================
import os
import re

# 匹配 @ApiModelProperty("xxx") 各种写法
API_PATTERN = re.compile(
    r'@ApiModelProperty\s*\(\s*(?:value\s*=\s*)?"([^"]+)"',
    re.S
)

# 判断下一行是否已经是注释（避免重复生成）
DEF_COMMENT_PATTERN = re.compile(r'\s*/\*\*')


def convert_api_to_comment(content: str) -> (str, int):
    """
    将 @ApiModelProperty("xxx") 转成 JavaDoc 注释块
    返回：新内容 + 替换次数
    """

    lines = content.split("\n")
    i = 0
    replace_count = 0

    while i < len(lines):
        line = lines[i]

        m = API_PATTERN.search(line)
        if not m:
            i += 1
            continue

        value = m.group(1)
        indent = re.match(r"\s*", line).group()

        # 1. 删除当前这一行 @ApiModel
        lines.pop(i)
        replace_count += 1

        # 3. 找类型上方的注解块起点（紧挨着 type 之上的一串 @XXX）
        anno_start = i
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
            new_javadoc = [
                f"{indent}/**",
                f"{indent} * {value}.",
                f"{indent} */"
            ]
            lines[anno_start:anno_start] = new_javadoc
            # 插入后 type_index 向后偏移了，但我们后面不再用它，直接从原 j 后继续往下扫即可

        i += 1

    return "\n".join(lines), replace_count


def process_directory(root_dir: str):
    """
    批量处理目录下所有 .java 文件，并输出日志
    """

    total_files = 0
    total_replacements = 0

    for folder, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".java"):
                file_path = os.path.join(folder, file)
                total_files += 1

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content, replaced = convert_api_to_comment(content)

                if replaced > 0:
                    total_replacements += replaced

                    # 回写新内容
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f"修改: {file_path}   ({replaced} 处注释已替换)")

    print("\n===== 处理完成 =====")
    print(f"总文件数: {total_files}")
    print(f"替换 @ApiModelProperty 注释总数: {total_replacements}")


if __name__ == "__main__":
    directory = input("请输入要处理的目录路径：").strip()
    process_directory(directory)
