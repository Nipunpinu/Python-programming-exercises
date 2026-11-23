import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "100+ Python challenging programming exercises for Python 3.md"
PUBLISHED_OUTPUT = "hello world!\n"


def extract_published_example(article):
    source = article.read_text(encoding="utf-8")
    match = re.search(
        r"### Question 61\r?\n(.*?)(?=### Question 62\r?\n)",
        source,
        re.DOTALL,
    )
    if not match:
        raise ValueError("Question 61 section was not found")

    section = match.group(1)
    if len(re.findall(r"(?m)^```", section)) != 12:
        raise ValueError("Question 61 must contain six balanced fenced blocks")

    example = re.search(
        r"Solution:\s*```python\r?\n(.*?)```\s*"
        r"Output:\s*```text\r?\n(.*?)\r?\n```",
        section,
        re.DOTALL,
    )
    if not example:
        raise ValueError("Published Question 61 solution/output pair was not found")

    return example.group(1).strip() + "\n", example.group(2) + "\n"


def execute_source_example(code):
    checked_code = code.rstrip() + (
        '\n\nassert type(unicodeString) is str\n'
        'assert unicodeString == "hello world!"\n'
    )
    with tempfile.TemporaryDirectory(prefix="check_q61_") as temporary_directory:
        script = Path(temporary_directory) / "published_question61.py"
        script.write_text(checked_code, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            check=True,
        )


def main():
    parser = argparse.ArgumentParser(
        description="Extract and check the published Question 61 Python example"
    )
    parser.add_argument(
        "--wrong",
        action="store_true",
        help="compare against a deliberately incorrect output",
    )
    args = parser.parse_args()

    code, expected_output = extract_published_example(ARTICLE)
    assert expected_output == PUBLISHED_OUTPUT, (
        f"Published output in the article changed: {expected_output!r}"
    )
    result = execute_source_example(code)

    if args.wrong:
        incorrect_output = "not the published output\n"
        print(f"Actual output: {result.stdout!r}")
        print(f"Deliberately wrong expected output: {incorrect_output!r}")
        assert result.stdout == incorrect_output, (
            "Deliberate negative test: actual output did not match the wrong result"
        )
        return

    assert result.stdout == expected_output, (
        f"Published output mismatch: expected {expected_output!r}, "
        f"got {result.stdout!r}"
    )
    print(f"Extracted and executed source from: {ARTICLE}")
    print(f"Expected output: {expected_output!r}")
    print(f"Actual output:   {result.stdout!r}")
    print("Python 3 value type: str (verified)")
    print("Published example check passed.")


if __name__ == "__main__":
    main()
