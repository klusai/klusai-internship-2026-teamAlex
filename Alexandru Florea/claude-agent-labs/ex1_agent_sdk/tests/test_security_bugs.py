"""
Security-review bug tests.

Each finding has:
  - A "confirms_crash" or "confirms_weak" test that PASSES against the current
    (buggy) code, proving the bug exists.
  - A "desired_behavior" test that FAILS against the current code, documenting
    what the fixed code should do.
"""

import hashlib
import math
import pytest

from app.payments import make_token, charge
from buggy.utils import calculate_average, get_user_name


# ---------------------------------------------------------------------------
# F1 – Unsalted MD5 tokenisation (payments.py make_token, lines 12-13)
# ---------------------------------------------------------------------------

KNOWN_CARD = "4111111111111111"
KNOWN_MD5  = hashlib.md5(KNOWN_CARD.encode()).hexdigest()  # 9301a3ae1c5fb5cf35d4601e98f38ceb


def test_f1_confirms_weak_md5_deterministic():
    """
    Confirms the bug: make_token returns a deterministic unsalted MD5 digest.
    Two calls with the same card produce the exact same token — demonstrating
    it is unsalted and reversible via rainbow tables.
    EXPECTED: PASS (proves the weak behavior is present).
    """
    token1 = make_token(KNOWN_CARD)
    token2 = make_token(KNOWN_CARD)
    # Both calls return the same hard-coded MD5 value.
    assert token1 == token2, "token is not deterministic – unexpected"
    assert token1 == KNOWN_MD5, (
        f"Expected unsalted MD5 {KNOWN_MD5!r} but got {token1!r}"
    )


def test_f1_desired_unique_tokens():
    """
    Documents desired behavior: two calls with the same card should NOT return
    the same token (a salted / HMAC / random approach would differ each call,
    or at minimum not match a known preimage).
    EXPECTED: FAIL against current code (token is deterministic, so they match).
    """
    token1 = make_token(KNOWN_CARD)
    token2 = make_token(KNOWN_CARD)
    assert token1 != token2, (
        "BUG (F1): make_token is deterministic and unsalted — tokens are identical "
        "across calls, enabling rainbow-table reversal."
    )


# ---------------------------------------------------------------------------
# F2 – Missing amount validation (payments.py charge, lines 16-19)
# ---------------------------------------------------------------------------

def test_f2_confirms_negative_charge_accepted():
    """
    Confirms the bug: charge(-100.0, ...) returns status 'charged' with a
    negative amount instead of raising an error.
    EXPECTED: PASS (proves the missing validation is present).
    """
    result = charge(-100.0, KNOWN_CARD)
    assert result["status"] == "charged"
    assert result["amount"] == -100.0


def test_f2_confirms_zero_charge_accepted():
    """
    Confirms the bug: charge(0.0, ...) also succeeds without raising.
    EXPECTED: PASS (proves the missing validation is present).
    """
    result = charge(0.0, KNOWN_CARD)
    assert result["status"] == "charged"
    assert result["amount"] == 0.0


def test_f2_desired_negative_raises():
    """
    Documents desired behavior: charge with a negative amount should raise ValueError.
    EXPECTED: FAIL against current code (no validation exists).
    """
    with pytest.raises(ValueError):
        charge(-100.0, KNOWN_CARD)


def test_f2_desired_zero_raises():
    """
    Documents desired behavior: charge with zero should raise ValueError.
    EXPECTED: FAIL against current code (no validation exists).
    """
    with pytest.raises(ValueError):
        charge(0.0, KNOWN_CARD)


def test_f2_desired_non_finite_raises():
    """
    Documents desired behavior: charge with non-finite amount (inf, nan) should raise.
    EXPECTED: FAIL against current code (no validation exists).
    """
    with pytest.raises((ValueError, TypeError)):
        charge(math.inf, KNOWN_CARD)


# ---------------------------------------------------------------------------
# F3 – ZeroDivisionError on empty list (utils.py calculate_average, line 10)
# ---------------------------------------------------------------------------

def test_f3_confirms_empty_list_crashes():
    """
    Confirms the bug: calculate_average([]) raises ZeroDivisionError.
    EXPECTED: PASS (proves the crash exists).
    """
    with pytest.raises(ZeroDivisionError):
        calculate_average([])


def test_f3_desired_empty_list_returns_none_or_zero():
    """
    Documents desired behavior: calculate_average([]) should return 0.0 or None
    rather than crashing.
    EXPECTED: FAIL against current code (it raises ZeroDivisionError instead).
    """
    result = calculate_average([])
    assert result in (0.0, None), (
        f"BUG (F3): expected 0.0 or None for empty list, got {result!r}"
    )


def test_f3_normal_case_still_works():
    """
    Sanity check: calculate_average works correctly for a non-empty list.
    EXPECTED: PASS.
    """
    assert calculate_average([1, 2, 3]) == 2.0


# ---------------------------------------------------------------------------
# F4 – Crashes on degenerate user inputs (utils.py get_user_name, line 16)
# ---------------------------------------------------------------------------

def test_f4_confirms_none_user_crashes():
    """
    Confirms the bug: get_user_name(None) raises TypeError.
    EXPECTED: PASS (proves the crash exists).
    """
    with pytest.raises(TypeError):
        get_user_name(None)


def test_f4_confirms_missing_key_crashes():
    """
    Confirms the bug: get_user_name({}) raises KeyError because 'name' is absent.
    EXPECTED: PASS (proves the crash exists).
    """
    with pytest.raises(KeyError):
        get_user_name({})


def test_f4_confirms_none_name_crashes():
    """
    Confirms the bug: get_user_name({"name": None}) raises AttributeError
    because None has no .upper() method.
    EXPECTED: PASS (proves the crash exists).
    """
    with pytest.raises(AttributeError):
        get_user_name({"name": None})


def test_f4_desired_none_user_returns_empty_string():
    """
    Documents desired behavior: get_user_name(None) should return "" not crash.
    EXPECTED: FAIL against current code (raises TypeError).
    """
    assert get_user_name(None) == "", (
        "BUG (F4): get_user_name(None) should return '' but raised instead"
    )


def test_f4_desired_missing_key_returns_empty_string():
    """
    Documents desired behavior: get_user_name({}) should return "" not crash.
    EXPECTED: FAIL against current code (raises KeyError).
    """
    assert get_user_name({}) == "", (
        "BUG (F4): get_user_name({}) should return '' but raised instead"
    )


def test_f4_desired_none_name_returns_empty_string():
    """
    Documents desired behavior: get_user_name({"name": None}) should return "".
    EXPECTED: FAIL against current code (raises AttributeError).
    """
    assert get_user_name({"name": None}) == "", (
        "BUG (F4): get_user_name({'name': None}) should return '' but raised instead"
    )


def test_f4_normal_case_still_works():
    """
    Sanity check: get_user_name works correctly for a well-formed user dict.
    EXPECTED: PASS.
    """
    assert get_user_name({"name": "alice"}) == "ALICE"
