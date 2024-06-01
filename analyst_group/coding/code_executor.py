from pathlib import Path
import subprocess
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages.base import BaseMessage
from typing import Literal, List


class CodeResult(BaseModel):
    exit_code: int = Field(description="The exit code of the code execution.")

    output: str = Field(description="The output of the code execution.")

class ExecutorMessage(BaseMessage):
    example: bool = False
    type: Literal["code executor"] = "code executor"
    result: CodeResult

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["custom", "messages"]


class CodeExecutor():

    def __init__(self, module_path: Path, timeout: int = 90):
        self.module_path = module_path
        self.timeout = timeout

    # ignore the *args passed from .invoke()
    def __call__(self, *args) -> ExecutorMessage:
        code_result = self.execute_code()

        return ExecutorMessage(
            content=[code_result.dict()],
            result=code_result
        )

    def execute_code(self) -> CodeResult:
        cmd = ["python", '-m', self.module_path]
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