# --------------------------------------------------------------------------------
# This file contains code derived from the [microsoft/autogen] project.
# Project Link: https://github.com/microsoft/autogen
# 
# The original source code is licensed under the MIT License:
# MIT License
# 
# Copyright (c) Microsoft Corporation.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE RESOLVE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------------------


from pydantic import BaseModel, Field


# Regular expression for finding a code block
# ```[ \t]*(\w+)?[ \t]*\r?\n(.*?)[ \t]*\r?\n``` Matches multi-line code blocks.
#   The [ \t]* matches the potential spaces before language name.
#   The (\w+)? matches the language, where the ? indicates it is optional.
#   The [ \t]* matches the potential spaces (not newlines) after language name.
#   The \r?\n makes sure there is a linebreak after ```.
#   The (.*?) matches the code itself (non-greedy).
#   The \r?\n makes sure there is a linebreak before ```.
#   The [ \t]* matches the potential spaces before closing ``` (the spec allows indentation).
CODE_BLOCK_PATTERN = r"```[ \t]*(\w+)?[ \t]*\r?\n(.*?)\r?\n[ \t]*```"

class CodeBlock(BaseModel):
    code: str = Field(description="The code to execute.")
    language: str = Field(description="The language of the code.")