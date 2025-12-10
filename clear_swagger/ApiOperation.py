import re

API_OPERATION_PATTERN = re.compile(
    r'@ApiOperation\s*\(\s*"([^"]+)"\s*\)'
)

# 匹配 JavaDoc 起始与结束
JAVADOC_START = re.compile(r'\s*/\*\*')
JAVADOC_END = re.compile(r'\s*\*/')


def convert_java_file(java_text: str) -> (str, int):
    lines = java_text.split("\n")
    i = 0
    replace_count = 0

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("//"):
            i += 1
            continue

        match = API_OPERATION_PATTERN.search(line)
        if not match:
            i += 1
            continue

        description = match.group(1)
        indent = re.match(r"\s*", line).group()

        # ---------------------------
        # 找 @ApiOperation 上方是否存在 JavaDoc
        # ---------------------------
        j = i - 1
        javadoc_start = None
        javadoc_end = None

        # 找 */ 结尾
        if j >= 0 and JAVADOC_END.search(lines[j]):
            javadoc_end = j
            k = j
            while k >= 0:
                if JAVADOC_START.search(lines[k]):
                    javadoc_start = k
                    break
                k -= 1

        if javadoc_start is not None:
            # ---------------------------
            # 在 JavaDoc 内插入 ApiOperation 描述
            # ---------------------------

            insert_line = javadoc_start + 1
            lines.insert(insert_line, f"{indent} * {description}.")
            replace_count += 1

            # 删除 @ApiOperation 行
            lines.pop(i + 1)
            continue

        # ==========================================================
        # 否则：无 JavaDoc → 生成新的 JavaDoc（但放在所有注解之前）
        # ==========================================================
        # 查找插入位置（跳过 @ 注解）
        insert_pos = i
        while insert_pos > 0 and lines[insert_pos - 1].strip().startswith("@"):
            insert_pos -= 1

        new_doc = [
            f"{indent}/**",
            f"{indent} * {description}.",
            f"{indent} *",
            f"{indent} */"
        ]

        # 插入新 JavaDoc
        lines[insert_pos:insert_pos] = new_doc

        replace_count += 1

        # 删除 @ApiOperation 行（但注意位置偏移）
        del lines[i + len(new_doc)]

        i += 1

    return "\n".join(lines), replace_count
