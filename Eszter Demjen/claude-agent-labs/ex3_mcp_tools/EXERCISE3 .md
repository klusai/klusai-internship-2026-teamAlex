# Exercise 3 — MCP Tool Design and Testing

## Task 1: Tool Descriptions

`search_orders` — looks up a single order by its ID. Use when the user provides a numeric string like `"10432"` or a prefixed code like `"ORD-5567"`. Bare numbers with no name context are treated as order IDs. Not for looking up by customer name.

`search_customers` — looks up a customer by person or company name, e.g. `"Jane Doe"` or `"Acme Corporation"`. Also use when the user says "order from [name]" with no ID given, since `search_orders` requires an ID. Not for looking up by order ID.

## Task 2: Accuracy

| State | Model | Accuracy |
|---|---|---|
| Baseline (vague stubs) | claude-haiku-4-5 | 10/10 |
| Post-edit | claude-haiku-4-5 | 10/10 |
| Post-edit | claude-sonnet-4-6 | 10/10 |
| Post-edit | claude-opus-4-6 | 10/10 |

Baseline was already 100% because the tool names are self-describing. The descriptions matter for robustness: swapping them collapses accuracy, proving they carry the routing logic, not the names.

## Task 3: Structured Errors

`make_error()` returns `error_category`, `message`, and `retryable`. Only `rate_limit` sets `retryable: True` — the server is temporarily unavailable and the same request may succeed after a wait. `not_found` and `invalid_input` are `False` because retrying an identical request will always produce the same result.

`invalid_input` was added to `search_orders`: an empty string now returns this category instead of `not_found`, since the two mean different things to the caller.

## Task 4: Ambiguous Cases

Case 8 (`"I need the record for 4521"`) — bare numbers default to order IDs, since names are always text in this system. Routed to `search_orders`.

Case 10 (`"Find the order from Wayne Enterprises"`) — `search_orders` requires an ID and cannot be called with a name alone. The only valid first step is to resolve the customer. Routed to `search_customers`.

## Stretch Goal: search_by_email

A third tool was added that looks up a customer by email address. The routing rule is simple: only use it when the input contains `@`. Three new cases were added and all 13 passed at 100% across all three models.
