from typing import List
import re
from .base import CodeBlock, CODE_BLOCK_PATTERN
from . import LOG


class PythonCodeExtractor():
    def __call__(self, message: str) -> CodeBlock:
        return self.extract_code_blocks(message)

    def extract_code_blocks(self, message: str) -> CodeBlock:
        match = re.findall(CODE_BLOCK_PATTERN, message, flags=re.DOTALL)

        for lang, code in match:
            # curretnly only supporting one code block
            return CodeBlock(code=code, language=lang)
    

