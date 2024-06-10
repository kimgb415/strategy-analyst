from pathlib import Path
import subprocess
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AIMessage
from typing import Literal, Dict, List


class CodeResult(BaseModel):
    exit_code: int = Field(description="The exit code of the code execution.")
    output: str = Field(description="The output of the code execution.")


class CodeExecutor():

    def __init__(self, module_path: Path, args: str = "--qa", timeout: int = 360):
        self.module_path = module_path
        self.args = args
        self.timeout = timeout

    # ignore the *args passed from .invoke()
    def __call__(self, *args) -> AIMessage:
        code_result = self.execute_code()

        return AIMessage(
            content=[code_result.dict()],
        )

    def execute_code(self) -> CodeResult:
        cmd = ["python", '-m', self.module_path, self.args]
        outputs = []

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=float(self.timeout)
            )
            outputs += result.stdout 
            outputs += result.stderr
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            outputs += "\n" + "The code execution timed out."
            exit_code = 124

        return CodeResult(exit_code=exit_code, output="".join(outputs))