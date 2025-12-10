# ================================
# swagger的ApiModelProperty -> 注释
# ================================
import os
import re

# 匹配 @ApiModelProperty("xxx") 各种写法
API_PATTERN = re.compile(
    r'@ApiModelProperty\s*\(\s*[^)]*?value\s*=\s*"([^"]+)"[^)]*\)',
    re.S
)

# 判断下一行是否已经是注释（避免重复生成）
DEF_COMMENT_PATTERN = re.compile(r'\s*/\*\*')


def convert_api_to_comment(java_text: str) -> (str, int):
    """
    将 @ApiModelProperty("xxx") 转成 JavaDoc 注释块
    返回：新内容 + 替换次数
    """

    lines = java_text.split("\n")
    output = []
    replace_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("//"):
            i += 1
            continue

        match = API_PATTERN.search(line)
        if match:
            comment = match.group(1)
            indent = re.match(r'\s*', line).group()

            # 检查下一行是否已有注释，避免重复生成
            if i + 1 < len(lines) and DEF_COMMENT_PATTERN.search(lines[i + 1]):
                output.append(line)  # 保留原注解行
                i += 1
                continue

            # 生成 JavaDoc 注释块
            block = [
                f"{indent}/**",
                f"{indent} * {comment}.",
                f"{indent} */"
            ]
            output.extend(block)
            replace_count += 1

            i += 1
            continue

        output.append(line)
        i += 1

    return "\n".join(output), replace_count


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
