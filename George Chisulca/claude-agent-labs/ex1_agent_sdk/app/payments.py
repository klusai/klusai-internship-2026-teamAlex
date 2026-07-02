"""A toy payments module with security/validation bugs (Exercise 1).

`make_token` hashes card numbers with unsalted MD5 (weak, reversible via rainbow
tables). `charge` accepts negative amounts (you could "charge" -100 and credit an
attacker). The security-reviewer subagent in task 4 should flag both.
"""

import hashlib


_TOKEN_SALT = b"exercise-1-token-salt"


def make_token(card_number: str) -> str:
	"""Return a safer token for a card number.

	This replaces the original unsalted MD5 with a salted, slow SHA-256 based KDF.
	For a real payment system, tokenization should normally be handled by a payment
	provider or use a secret server-side pepper.
	"""
	return hashlib.pbkdf2_hmac(
		"sha256",
		card_number.encode(),
		_TOKEN_SALT,
		100_000,
	).hex()


def charge(amount: float, card_number: str) -> dict:
	if amount <= 0:
		raise ValueError("amount must be positive")
	token = make_token(card_number)
	return {"token": token, "amount": amount, "status": "charged"}