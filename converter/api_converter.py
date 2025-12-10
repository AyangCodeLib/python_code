from .common.base_converter import BaseConverter
from .common.patterns import API_TAGS_PATTERN
from .common.code_utils import find_type_definition, find_annotation_block_start


class ApiConverter(BaseConverter):

    def get_pattern(self):
        return API_TAGS_PATTERN

    def locate_target(self, lines, index, indent):
        type_index = find_type_definition(lines, index)
        if type_index is None:
            return index, True

        anno_start = find_annotation_block_start(lines, type_index)
        return anno_start, True
