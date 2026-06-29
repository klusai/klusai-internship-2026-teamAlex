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

_EMAILS = {
    "contact@acme.com": {"name": "Acme Corporation", "tier": "enterprise", "open_orders": 3},
    "info@globex.com": {"name": "Globex", "tier": "smb", "open_orders": 1},
    "jane.doe@gmail.com": {"name": "Jane Doe", "tier": "consumer", "open_orders": 0},
    "procurement@wayne.com": {"name": "Wayne Enterprises", "tier": "enterprise", "open_orders": 7},
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
	"""Looks up an order based on its order ID.

	Use this tool when the user supplies an order identifier, a numeric
	string like "100897" or "11231", or a prefixed code like "ORD-5576".
	Bare numbers with no name context should be treated as order IDs.

	Example: "Find order #33" or What is the status of 88734?"

	NOT for looking up by customer name or company name. If the user only
	provides a name (ex: "order from Napoca Enterprise"), use search_customers
	first to resolve the customer.
	"""
	if not order_id or not order_id.strip():
		return make_error("invalid_input", "order_id must not be empty.")
	
	order = _ORDERS.get(order_id)
	if order is None:
		return make_error("not_found", f"No order with id {order_id!r}.")
	return order


@mcp.tool()
def search_customers(name: str) -> dict:
	"""Looks up a customer account by person or company name.
	Use this tool when the user supplies the name of a person like
	"Keanu Reeves" or the name of a company: "Evil Corps". Also use
	this when the user say "order from [name]" or "order placed by 
	[name]" and no order ID is given, since you must resolve the
	customer before finding their orders.

	Example: "Show me everything for Digi" or "Find the order from
	William"

	NOT for looking up by order ID or numeric code.
	"""
	customer = _CUSTOMERS.get(name.strip().lower())
	if customer is None:
		return make_error("not_found", f"No customer named {name!r}.")
	return customer

@mcp.tool()
def search_by_email(email:str) -> dict:
	"""Looks up a customer account by their email address.
	Use this tool when the user supplies a valid email address:
	a string that contains "@", like "keanu.reeves@gmail.com" or
	"jane_12@gmail.com".

	Example: "Find the customer with email info@city.ro"

	NOT for looking up by name or order ID. If the input looks like
	a name or does not contain '@', use search_customers instead.
	"""
	if "@" not in email:
		return make_error("invalid_input", f"{email!r} is not a valid email address.")
	customer = _EMAILS.get(email.strip().lower())
	if customer is None:
		return make_error("not_found", f"No customer with email {email!r}.")
	return customer
	


if __name__ == "__main__":
	# Runs the server over stdio. An MCP client (or Claude Desktop) connects to it.
	mcp.run()
