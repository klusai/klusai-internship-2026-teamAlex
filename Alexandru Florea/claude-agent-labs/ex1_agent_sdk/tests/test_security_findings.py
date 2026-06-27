"""
Security-finding regression tests (Exercise 1).

Each test documents a specific vulnerability or crash found during the security
review. Tests assert CURRENT (buggy) behavior so they pass against the existing
code and serve as living documentation of the bugs.

Finding-to-test mapping
-----------------------
F1  test_make_token_unsalted_md5
        payments.py: make_token uses plain MD5 with no salt.
F2  test_charge_float_imprecision
        payments.py: float addition yields IEEE-754 imprecision stored in charge result.
F3a test_charge_accepts_inf
        payments.py: charge() does not guard against float('inf').
F3b test_charge_accepts_nan
        payments.py: charge() does not guard against float('nan').
F4  test_charge_accepts_empty_card
        payments.py: charge() applies no card-number validation.
F5  test_calculate_average_non_numeric_raises
        buggy/utils.py: calculate_average crashes on non-numeric list elements.
F6  test_get_user_name_int_name_raises
        buggy/utils.py: get_user_name crashes when the 'name' value is not a string.
F7  test_calculate_average_empty_list
        buggy/utils.py: calculate_average([]) silently returns 0.0.
"""

import hashlib
import math
import sys
import os
import pytest

# ---------------------------------------------------------------------------
# Path setup: allow imports from sibling app/ and buggy/ directories.
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(BASE_DIR, "app")
BUGGY_DIR = os.path.join(BASE_DIR, "buggy")

for _dir in (APP_DIR, BUGGY_DIR):
    if _dir not in sys.path:
        sys.path.insert(0, _dir)

from payments import make_token, charge        # noqa: E402
from utils import calculate_average, get_user_name  # noqa: E402

SAMPLE_CARD = "4111111111111111"

# ===========================================================================
# F1 — make_token uses unsalted MD5
# ===========================================================================

def test_make_token_unsalted_md5():
    """F1 (Critical): make_token returns the raw MD5 hex-digest of the card number
    with no salt.  The same card always produces the same token, making it
    trivially reversible via a rainbow table."""
    known_md5 = hashlib.md5(SAMPLE_CARD.encode()).hexdigest()
    assert make_token(SAMPLE_CARD) == known_md5


# ===========================================================================
# F2 — charge() stores IEEE-754 float imprecision
# ===========================================================================

def test_charge_float_imprecision():
    """F2 (High): charge(0.1 + 0.2, card) stores 0.30000000000000004 in the
    returned dict because float addition is not exact.  Monetary values should
    use decimal.Decimal, not float."""
    result = charge(0.1 + 0.2, SAMPLE_CARD)
    assert result["amount"] == 0.30000000000000004


# ===========================================================================
# F3 — charge() accepts non-finite float amounts
# ===========================================================================

def test_charge_accepts_inf():
    """F3a (Critical): charge(float('inf'), card) does NOT raise — the guard
    `amount <= 0` passes for positive infinity, so an infinite charge is
    accepted and returned as-is."""
    # Documents the bug: this call must NOT raise.
    result = charge(float("inf"), SAMPLE_CARD)
    assert math.isinf(result["amount"])


def test_charge_accepts_nan():
    """F3b (Critical): charge(float('nan'), card) does NOT raise — NaN is not
    <= 0 in Python, so the guard passes and NaN is stored as the charge amount."""
    # Documents the bug: this call must NOT raise.
    result = charge(float("nan"), SAMPLE_CARD)
    assert math.isnan(result["amount"])


# ===========================================================================
# F4 — charge() does not validate card_number
# ===========================================================================

def test_charge_accepts_empty_card():
    """F4 (Medium): charge(10.0, '') succeeds with an empty string card number.
    No format or length validation is performed."""
    result = charge(10.0, "")
    assert result["status"] == "charged"


# ===========================================================================
# F5 — calculate_average crashes on non-numeric list elements
# ===========================================================================

def test_calculate_average_non_numeric_raises():
    """F5 (Medium): calculate_average([1, 2, 'three']) raises TypeError because
    sum() cannot add a str to an int.  The function has no type-guard."""
    with pytest.raises(TypeError):
        calculate_average([1, 2, "three"])


# ===========================================================================
# F6 — get_user_name crashes when name value is not a string
# ===========================================================================

def test_get_user_name_int_name_raises():
    """F6 (Low): get_user_name({'name': 42}) raises AttributeError because int
    has no .upper() method.  The function does not validate that the retrieved
    value is actually a str before calling .upper()."""
    with pytest.raises(AttributeError):
        get_user_name({"name": 42})


# ===========================================================================
# F7 — calculate_average([]) silently returns 0.0
# ===========================================================================

def test_calculate_average_empty_list():
    """F7 (Low): calculate_average([]) returns 0.0 via an early-return guard
    instead of raising.  Callers cannot distinguish 'average is zero' from
    'no data was provided'."""
    assert calculate_average([]) == 0.0
