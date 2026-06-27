"""
Standalone runner for security bug tests (no pytest required).
Imports the buggy modules from Alex Ghiurau's ex1_agent_sdk.
"""
import sys
import os
import hashlib
import math

GHIURAU_SDK = "/home/alex/anthropic_certification/klusai-internship-2026/Alex Ghiurau/claude-agent-labs/ex1_agent_sdk"
sys.path.insert(0, GHIURAU_SDK)

from app.payments import make_token, charge
from buggy.utils import calculate_average, get_user_name

CARD = "4111111111111111"
KNOWN_MD5 = hashlib.md5(CARD.encode()).hexdigest()

results = []


def record(name, passed, note=""):
    label = "PASS" if passed else "FAIL"
    msg = f"{label}  {name}"
    if note:
        msg += f"  [{note}]"
    results.append(msg)


t1 = make_token(CARD)
t2 = make_token(CARD)
record(
    "test_f1_confirms_weak_md5_deterministic",
    t1 == t2 == KNOWN_MD5,
)

record(
    "test_f1_desired_unique_tokens",
    t1 != t2,
    "BUG: deterministic unsalted MD5" if t1 == t2 else "",
)

r = charge(-100.0, CARD)
record("test_f2_confirms_negative_charge_accepted", r["status"] == "charged" and r["amount"] == -100.0)

r = charge(0.0, CARD)
record("test_f2_confirms_zero_charge_accepted", r["status"] == "charged" and r["amount"] == 0.0)

try:
    charge(-100.0, CARD)
    record("test_f2_desired_negative_raises", False, "BUG: no ValueError raised")
except ValueError:
    record("test_f2_desired_negative_raises", True)

try:
    charge(0.0, CARD)
    record("test_f2_desired_zero_raises", False, "BUG: no ValueError raised")
except ValueError:
    record("test_f2_desired_zero_raises", True)

try:
    charge(math.inf, CARD)
    record("test_f2_desired_non_finite_raises", False, "BUG: no ValueError/TypeError raised")
except (ValueError, TypeError):
    record("test_f2_desired_non_finite_raises", True)

try:
    calculate_average([])
    record("test_f3_confirms_empty_list_crashes", False)
except ZeroDivisionError:
    record("test_f3_confirms_empty_list_crashes", True)

try:
    result = calculate_average([])
    record(
        "test_f3_desired_empty_list_returns_none_or_zero",
        result in (0.0, None),
        "" if result in (0.0, None) else f"unexpected {result!r}",
    )
except ZeroDivisionError:
    record("test_f3_desired_empty_list_returns_none_or_zero", False, "BUG: ZeroDivisionError")

record("test_f3_normal_case_still_works", calculate_average([1, 2, 3]) == 2.0)

try:
    get_user_name(None)
    record("test_f4_confirms_none_user_crashes", False)
except TypeError:
    record("test_f4_confirms_none_user_crashes", True)

try:
    get_user_name({})
    record("test_f4_confirms_missing_key_crashes", False)
except KeyError:
    record("test_f4_confirms_missing_key_crashes", True)

try:
    get_user_name({"name": None})
    record("test_f4_confirms_none_name_crashes", False)
except AttributeError:
    record("test_f4_confirms_none_name_crashes", True)

try:
    result = get_user_name(None)
    record("test_f4_desired_none_user_returns_empty_string", result == "", f"got {result!r}" if result != "" else "")
except (TypeError, KeyError, AttributeError) as e:
    record("test_f4_desired_none_user_returns_empty_string", False, f"BUG: {type(e).__name__}")

try:
    result = get_user_name({})
    record("test_f4_desired_missing_key_returns_empty_string", result == "", f"got {result!r}" if result != "" else "")
except (TypeError, KeyError, AttributeError) as e:
    record("test_f4_desired_missing_key_returns_empty_string", False, f"BUG: {type(e).__name__}")

try:
    result = get_user_name({"name": None})
    record("test_f4_desired_none_name_returns_empty_string", result == "", f"got {result!r}" if result != "" else "")
except (TypeError, KeyError, AttributeError) as e:
    record("test_f4_desired_none_name_returns_empty_string", False, f"BUG: {type(e).__name__}")

record("test_f4_normal_case_still_works", get_user_name({"name": "alice"}) == "ALICE")

print()
for r in results:
    print(r)

passed = sum(1 for r in results if r.startswith("PASS"))
failed = sum(1 for r in results if r.startswith("FAIL"))
print()
print(f"{passed} passed, {failed} failed out of {len(results)} tests")
sys.exit(0 if failed == 0 else 1)
