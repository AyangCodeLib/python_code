from .common.base_converter import BaseConverter
from .common.patterns import API_OPERATION_PATTERN
from .common.code_utils import find_annotation_block_start


class ApiOperationConverter(BaseConverter):

    def get_pattern(self):
        return API_OPERATION_PATTERN

    def locate_target(self, lines, index, indent):
        anno_start = find_annotation_block_start(lines, index)
        return anno_start, False
