import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARTICLE = ROOT / "100+ Python challenging programming exercises for Python 3.md"


def extract_published_example(article):
    source = article.read_text(encoding="utf-8")
    match = re.search(
        r"### Question 66\r?\n(.*?)(?=### Question 67\r?\n)",
        source,
        re.DOTALL,
    )
    if not match:
        raise ValueError("Question 66 section was not found")

    section = match.group(1)
    if len(re.findall(r"(?m)^```", section)) != 8:
        raise ValueError("Question 66 must contain four balanced fenced blocks")

    example = re.search(
        r"Example:\s*"
        r"If the following n is given as input to the program:\s*(\d+)\s*"
        r"Then, the output of the program should be:\s*(\d+)",
        section,
    )
    solution = re.search(
        r"Solution:\s*```python\r?\n(.*?)```",
        section,
        re.DOTALL,
    )
    if not example or not solution:
        raise ValueError("Question 66 published example or solution was not found")

    return {
        "section": section,
        "input": example.group(1),
        "expected": example.group(2) + "\n",
        "code": solution.group(1).strip() + "\n",
    }


def execute_solution(code, input_text, assertion):
    script = code.rstrip() + "\n\n" + assertion + "\n"
    with tempfile.TemporaryDirectory(prefix="check_q66_") as temporary_directory:
        script_path = Path(temporary_directory) / "published_question66.py"
        script_path.write_text(script, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(script_path)],
            input=f"{input_text}\n",
            capture_output=True,
            text=True,
            check=True,
        )


def main():
    example = extract_published_example(ARTICLE)
    assert example["input"] == "7", f"Unexpected published input: {example['input']}"
    assert example["expected"] == "13\n", (
        f"Unexpected published output: {example['expected']!r}"
    )
    result = execute_solution(
        example["code"],
        example["input"],
        f"assert f({example['input']}) == {int(example['expected'])}",
    )

    assert result.stdout == example["expected"], (
        f"Published output mismatch: expected {example['expected']!r}, "
        f"got {result.stdout!r}"
    )
    assert int(result.stdout.strip()) == int(example["expected"])
    print(f"Source: {ARTICLE}")
    print(f"Published input: {example['input']}")
    print(f"Expected output: {example['expected']!r}")
    print(f"Actual output:   {result.stdout!r}")
    print("Published Question 66 check passed.")


if __name__ == "__main__":
    main()
