import argparse
import math
import os
import re
import subprocess
import sys
import tempfile

here = os.path.dirname(os.path.abspath(__file__))
md_path = os.path.join(here, "..", "..", "100+ Python challenging programming exercises for Python 3.md")


def get_solution_code(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Question 6 section
    q_match = re.search(r"### Question 6\n(.*?)(?=### Question 7)", content, re.S)
    if not q_match:
        print("Error: Question 6 not found in markdown file")
        sys.exit(1)

    sec = q_match.group(1)
    code_match = re.search(r"Solution:\s*```python\n(.*?)```", sec, re.S)
    if not code_match:
        print("Error: Question 6 solution code block not found")
        sys.exit(1)

    return code_match.group(1).strip()


def run_code(code, input_str):
    fd, tmp_file = tempfile.mkstemp(prefix="check_q6_", suffix=".py")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code)
        res = subprocess.run(
            [sys.executable, tmp_file],
            input=input_str,
            capture_output=True,
            text=True
        )
        return res
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def verify_intermediate_values(d_val, c=50, h=30):
    float_d = float(d_val)
    numerator = 2 * c * float_d
    radicand = numerator / h
    sqrt_val = math.sqrt(radicand)
    round_val = round(sqrt_val)
    int_val = int(round_val)
    return {
        "d": d_val,
        "float_d": float_d,
        "numerator": numerator,
        "radicand": radicand,
        "sqrt_val": sqrt_val,
        "round_val": round_val,
        "int_val": int_val,
    }


def main():
    parser = argparse.ArgumentParser(description="Automated checker for Question 6")
    parser.add_argument("--wrong", action="store_true", help="Trigger deliberate failure to test checker rejection")
    args = parser.parse_args()

    print(f"Reading solution from: {md_path}")
    code = get_solution_code(md_path)
    print("Extracted code from markdown:\n---")
    print(code)
    print("---")

    # If --wrong flag is active, trigger deliberate failure
    if args.wrong:
        print("\n[SIMULATING DELIBERATE FAILURE (--wrong flag active)]")
        res = run_code(code, "100,150,180\n")
        assert res.returncode == 0
        actual = res.stdout.strip()
        deliberate_wrong = "10,20,30"
        print(f"Actual: {actual!r} | Deliberate Wrong Expected: {deliberate_wrong!r}")
        assert actual == deliberate_wrong, f"DELIBERATE FAILURE TRIGGERED: Output {actual!r} did not match wrong expectation {deliberate_wrong!r}"
        print("Error: Deliberate failure should have raised an AssertionError!")
        sys.exit(1)

    # 1. Test Published Example (input: "100,150,180", expected: "18,22,24")
    print("\n[1] Testing published example (input: 100,150,180)...")
    res_pub = run_code(code, "100,150,180\n")
    if res_pub.returncode != 0:
        print("Execution crashed on published input 100,150,180!")
        print("stderr:", res_pub.stderr)
        sys.exit(1)

    expected_pub_str = "18,22,24\n"
    actual_pub_str = res_pub.stdout
    print(f"Published Expected: {expected_pub_str!r}")
    print(f"Published Actual:   {actual_pub_str!r}")
    assert actual_pub_str == expected_pub_str, f"Mismatch: expected {expected_pub_str!r}, got {actual_pub_str!r}"

    parsed_ints = [int(x) for x in actual_pub_str.strip().split(",")]
    assert parsed_ints == [18, 22, 24], f"Numerical mismatch: {parsed_ints} != [18, 22, 24]"
    print("Published example verified successfully (string formatting and numerical values).")

    # 2. Record and Verify Exact Intermediate Values for Published Inputs
    print("\n[2] Verifying mathematical pipeline and intermediate values...")
    published_inputs = [100, 150, 180]
    expected_finals = [18, 22, 24]
    for d, exp in zip(published_inputs, expected_finals):
        calc = verify_intermediate_values(d)
        print(f"  D = {d}: float={calc['float_d']} | num={calc['numerator']} | radicand={calc['radicand']:.4f} | sqrt={calc['sqrt_val']:.6f} | round={calc['round_val']} | int={calc['int_val']}")
        assert calc["int_val"] == exp, f"Calculated value mismatch for D={d}: {calc['int_val']} != {exp}"
    print("Intermediate values verified against mathematical breakdown.")

    # 3. Test Smallest Supported Input (D = 0)
    print("\n[3] Testing smallest supported input (D = 0)...")
    res_zero = run_code(code, "0\n")
    assert res_zero.returncode == 0, f"D=0 crashed: {res_zero.stderr}"
    print(f"D=0 Expected: '0\\n' | Actual: {res_zero.stdout!r}")
    assert res_zero.stdout == "0\n"
    calc_0 = verify_intermediate_values(0)
    assert calc_0["int_val"] == 0
    print("Smallest supported input verified successfully.")

    # 4. Test Additional Bounded Variations
    print("\n[4] Testing additional bounded variations...")
    variations = [
        ("1", "2\n", [2]),
        ("50,75", "13,16\n", [13, 16]),
        ("300", "32\n", [32]),
    ]
    for inp_s, exp_s, exp_vals in variations:
        res_v = run_code(code, f"{inp_s}\n")
        assert res_v.returncode == 0, f"Variation {inp_s} crashed: {res_v.stderr}"
        assert res_v.stdout == exp_s, f"Mismatch for {inp_s}: expected {exp_s!r}, got {res_v.stdout!r}"
        vals = [int(x) for x in res_v.stdout.strip().split(",")]
        assert vals == exp_vals
        print(f"Input: {inp_s:8} | Expected: {exp_s.strip():8} | Actual: {res_v.stdout.strip():8}")
    print("All bounded variations verified successfully.")

    # 5. Internal Deliberate Wrong-Result Self-Test
    print("\n[5] Running internal wrong-result self-test...")
    wrong_pub = "18,22,25\n"
    if actual_pub_str == wrong_pub:
        print("Self-test FAILED: accepted incorrect expected output!")
        sys.exit(1)
    print("Self-test PASSED: mismatch against wrong expectation correctly detected and rejected.")

    print("\nAll checks passed successfully! (exit code 0)")


if __name__ == "__main__":
    main()
