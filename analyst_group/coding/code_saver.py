from .base import CodeBlock
from pathlib import Path
from typing import List


class CodeSaver():
    def __init__(self, save_to: Path) -> None:
        self.save_to = save_to
    
    def __call__(self, code_block: CodeBlock) -> str:
        self.save_code_blocks(code_block)

        return code_block.code
    
    def save_code_blocks(self, code_block: CodeBlock) -> None:
        with open(self.save_to, 'w') as f:
            f.write(code_block.code)

