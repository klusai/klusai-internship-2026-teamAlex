"""Exercise 3 — a small MCP server with two *deliberately confusable* tools.

`search_orders` looks things up by **order id**; `search_customers` looks things up
by **customer name**. The whole point of the exercise is that the model picks the
right one based ONLY on the tool descriptions — so the descriptions below start as
weak TODO stubs that you must rewrite to disambiguate.

Run the server (after `pip install mcp`):

    python server.py            # stdio transport, for an MCP client / Claude Desktop

You don't need a running server to do the core exercise: `run_ambiguity_test.py`
imports the two tool functions and reads their docstrings directly.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("orders-and-customers")


# --- Tiny in-memory fixture data -------------------------------------------------

_ORDERS = {
	"10432": {"order_id": "10432", "customer": "Acme Corporation", "total": 249.00, "status": "shipped"},
	"88231": {"order_id": "88231", "customer": "Globex", "total": 18.50, "status": "processing"},
	"ORD-5567": {"order_id": "ORD-5567", "customer": "Wayne Enterprises", "total": 999.99, "status": "delivered"},
	"7741": {"order_id": "7741", "customer": "Jane Doe", "status": "cancelled", "total": 0.0},
}

_CUSTOMERS = {
	"acme corporation": {"name": "Acme Corporation", "tier": "enterprise", "open_orders": 3},
	"globex": {"name": "Globex", "tier": "smb", "open_orders": 1},
	"jane doe": {"name": "Jane Doe", "tier": "consumer", "open_orders": 0},
	"wayne enterprises": {"name": "Wayne Enterprises", "tier": "enterprise", "open_orders": 7},
}


# --- Structured errors -----------------------------------------------------------

# Only this category is safe to retry. Everything else is a permanent failure the
# caller should NOT hammer.
_RETRYABLE_CATEGORIES = {"rate_limit"}


def make_error(category: str, message: str) -> dict:
	"""Build a structured error the model can reason about.

	Returns a dict with three keys:
	  - error_category: a short machine-readable category (e.g. "not_found",
	    "rate_limit", "invalid_input").
	  - message: a human-readable explanation.
	  - retryable: True ONLY when the category is `rate_limit`; False otherwise.

	The retry flag is the important bit: a `not_found` should never be retried,
	but a `rate_limit` should be retried after a backoff.
	"""
	return {
		"error_category": category,
		"message": message,
		"retryable": category in _RETRYABLE_CATEGORIES,
	}


# --- Tools -----------------------------------------------------------------------

@mcp.tool()
def search_orders(order_id: str) -> dict:
	"""
	Use this tool when the user provides an order id — a bare number like "10432",
	"88231", or "7741", or a prefixed code like "ORD-5567". The single argument
	`order_id` must be that identifier string. Example: order_id="10432".

	Bare numbers (no prefix, no company name) are always treated as order ids —
	use this tool for them.

	Do NOT use this tool when the user provides only a person's name or a company
	name with no order id. You cannot search orders by name. If the user says
	"find the order from Wayne Enterprises", you must call search_customers first
	to resolve the customer, then use the order id from the result.

	Do NOT use this tool for empty or missing ids — that is an invalid input.
	"""
	if not order_id or not order_id.strip():
		return make_error("invalid_input", "order_id must not be empty.")
	order = _ORDERS.get(order_id)
	if order is None:
		return make_error("not_found", f"No order with id {order_id!r}.")
	return order


@mcp.tool()
def search_customers(name: str) -> dict:
	"""
	Use this tool when the user provides a person's name or a company name —
	strings like "Acme Corporation", "Jane Doe", or "Globex". The single argument
	`name` is that name string. Example: name="Acme Corporation".

	Also use this tool when the user mentions an order but only gives a company or
	person name (e.g. "find the order from Wayne Enterprises") — you must resolve
	the customer by name first before any order lookup is possible.

	Do NOT use this tool when the user gives a bare number or an order code like
	"10432" or "ORD-5567". Those are order ids, not customer names — use
	search_orders for them.
	"""
	customer = _CUSTOMERS.get(name.strip().lower())
	if customer is None:
		return make_error("not_found", f"No customer named {name!r}.")
	return customer


if __name__ == "__main__":
	# Runs the server over stdio. An MCP client (or Claude Desktop) connects to it.
	mcp.run()
