import re

# 匹配@Api(tags="xxx")
API_TAGS_PATTERN = re.compile(
    r'@Api\s*\(\s*tags\s*=\s*"([^"]+)"\s*\)'
)

# 匹配@ApiModel(value="xxx") 或 @ApiModel("xxx")
API_MODEL_PATTERN = re.compile(
    r'@ApiModel\s*\(\s*(?:value\s*=\s*)?"([^"]+)"',
    re.S
)

# 匹配@ApiModelProperty("xxx") 或 @ApiModelProperty(value = "xxx")
API_MODEL_PROPERTY_PATTERN = re.compile(
    r'@ApiModelProperty\s*\(\s*(?:value\s*=\s*)?"([^"]+)"',
    re.S
)

# 匹配@ApiOperation("xxx")
API_OPERATION_PATTERN = re.compile(
    r'@ApiOperation\s*\(\s*"([^"]+)"\s*\)'
)

# 匹配类型
TYPE_PATTERN = re.compile(r'\b(class|interface|enum|@interface)\b')
