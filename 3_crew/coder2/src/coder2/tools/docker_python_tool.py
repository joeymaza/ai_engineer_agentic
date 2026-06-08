from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

import subprocess
import tempfile
from pathlib import Path


class DockerPythonInput(BaseModel):
    """Input schema for running Python code in Docker."""

    code: str = Field(
        ...,
        description="Python code to execute inside a temporary Docker container.",
    )


class DockerPythonTool(BaseTool):
    name: str = "Run Python Code in Docker"
    description: str = (
        "Executes complete, valid Python code inside an isolated Docker container. "
        "The input must be a single self-contained Python script. "
        "Do not use unfinished triple-quoted strings. "
        "Do not write nested Python files using f.write(\"\"\"...\") unless all quotes are closed correctly. "
        "Prefer simple Python code that prints final results to stdout."
    )
    args_schema: Type[BaseModel] = DockerPythonInput

    def _run(self, code: str) -> str:
        try:
            compile(code, "submitted_code.py", "exec")
        except SyntaxError as e:
            return (
                "The submitted Python code has a syntax error before Docker execution.\n\n"
                f"Error: {e}\n"
                f"Line: {e.lineno}\n"
                f"Text: {e.text}\n\n"
                 "===== CODE SUBMITTED =====\n"
                f"{code}"
    )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            script_path = temp_path / "script.py"
            script_path.write_text(code, encoding="utf-8")

            command = [
                "docker",
                "run",
                "--network",
                "none",
                "--memory",
                "512m",
                "--cpus",
                "1",
                "-v",
                f"{temp_path}:/workspace",
                "-w",
                "/workspace",
                "python:3.11-slim",
                "python",
                "script.py",
            ]

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                output = ""

                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"

                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"

                if not output:
                    output = "Code ran successfully with no output."

                return output

            except subprocess.TimeoutExpired:
                return "Error: Code execution timed out after 30 seconds."

            except FileNotFoundError:
                return (
                    "Error: Docker command not found. "
                    "Make sure Docker Desktop is installed and running."
                )

            except Exception as e:
                return f"Error running code in Docker: {e}"
