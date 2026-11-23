import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "100+ Python challenging programming exercises for Python 3.md"


def extract_solution():
    source = ARTICLE.read_text(encoding="utf-8")
    question = re.search(
        r"(?ms)^### Question 62\s*\n(.*?)(?=^### Question 63\s*$)",
        source,
    )
    if not question:
        raise ValueError("Question 62 section was not found")

    section = question.group(1)
    fences = re.findall(r"(?m)^```", section)
    if len(fences) % 2:
        raise ValueError("Question 62 contains an unbalanced code fence")

    solution = re.search(
        r"(?ms)^Solution:\s*\n```python\s*\n(.*?)^```$",
        section,
    )
    if not solution:
        raise ValueError("Question 62 Python solution block was not found")
    return solution.group(1).strip() + "\n"


def run_solution(code, input_text):
    assertions = (
        "\nassert type(s) is str\n"
        "assert type(u) is str\n"
        "assert u == s\n"
    )
    with tempfile.TemporaryDirectory(prefix="check_q62_") as temporary_directory:
        script = Path(temporary_directory) / "question62.py"
        script.write_text(code.rstrip() + assertions, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(script)],
            input=input_text,
            capture_output=True,
            text=True,
            check=True,
        )


def main():
    solution = extract_solution()
    result = run_solution(solution, "hello\n")
    expected = "hello\n"
    assert result.stdout == expected, (
        f"Published demonstration mismatch: {result.stdout!r}"
    )

    print(f"Source: {ARTICLE.name}, Question 62 solution")
    print(f"Input: 'hello'; expected output: {expected!r}; actual: {result.stdout!r}")
    print("Intermediate assertions passed: s and u are str, with u == s.")
    print("Question 62 published demonstration passed.")


if __name__ == "__main__":
    main()
