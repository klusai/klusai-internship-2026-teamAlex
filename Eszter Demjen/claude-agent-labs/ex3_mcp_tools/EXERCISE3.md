# Exercise 3 — MCP Tool Design and Testing

## Task 1 — Disambiguating Tool Descriptions

The server exposes two confusable tools: `search_orders` (lookup by order ID) and `search_customers` (lookup by customer name). The docstrings were rewritten so the model routes correctly based only on the description, not the tool name.

**`search_orders`**
> Look up a single order by its order ID. Use this when the user supplies an order identifier — a numeric string like `"10432"` or a prefixed code like `"ORD-5567"`. Bare numbers with no name context are treated as order IDs. Not for looking up by customer name — if the user only provides a name, use `search_customers` first.

**`search_customers`**
> Look up a customer account by person or company name. Use this when the user supplies a name like `"Jane Doe"` or `"Acme Corporation"`. Also use this when the user says "order from [name]" and no order ID is given — you must resolve the customer before finding their orders. Not for looking up by order ID.

---

## Task 2 — Baseline vs. Post-Edit Accuracy

The harness builds Anthropic tool definitions from the docstrings directly and asks the model to pick a tool for each of 10 prompts, measured against gold `expected_tool` labels.

| State | Model | Accuracy | Notes |
|---|---|---|---|
| Baseline (vague stubs) | claude-haiku-4-5 | 10/10 = 100% | Routing driven by tool names, not descriptions |
| Post-edit | claude-haiku-4-5 | 10/10 = 100% | Descriptions now carry the disambiguation load |
| Post-edit | claude-sonnet-4-6 | 10/10 = 100% | No change — descriptions were sufficient |
| Post-edit | claude-opus-4-6 | 10/10 = 100% | No change — descriptions were sufficient |

The baseline was already 100% because the tool names are self-describing. The meaningful test is the self-check: swapping the two descriptions collapses accuracy, which proves the descriptions — not the names — are doing the routing work after the rewrite.

---

## Task 3 — Structured Errors

Tools return structured error dicts rather than raising exceptions because exceptions do not travel cleanly across the MCP network boundary. A structured dict gives the model something it can read and act on.

| Category | Retryable | Rationale |
|---|---|---|
| `rate_limit` | `True` | The server is temporarily overwhelmed. The request is valid — waiting and retrying will likely succeed. |
| `not_found` | `False` | The record does not exist. Retrying the same request will always return the same result. |
| `invalid_input` | `False` | The request is malformed (e.g. empty order ID). No amount of waiting fixes a bad input. |

`invalid_input` was added to `search_orders`: when given an empty string, the tool returns `make_error("invalid_input", ...)` rather than a misleading `not_found`. The distinction matters — `not_found` tells the caller to try a different ID; `invalid_input` tells the caller to fix the request.

---

## Task 4 — Ambiguous Cases

Two prompts are genuinely ambiguous. A stance was chosen for each and encoded in the descriptions.

**Case 8 — `"I need the record for 4521"`**

`4521` is a bare number with no name context. In this system names are always text and IDs are always numbers, so a bare number defaults to order lookup. Encoded in the description: *"bare numbers with no name context are treated as order IDs."* Routed to: `search_orders`.

**Case 10 — `"Find the order from Wayne Enterprises"`**

The word "order" might suggest `search_orders`, but that tool requires an ID — it cannot be called with only a company name. The only valid first step is to resolve the customer. Encoded in the description: *"if the user says 'order from [name]' and no ID is given, use `search_customers` first."* Routed to: `search_customers`.

---

## Stretch Goal — Third Tool: `search_by_email`

A third tool was added to test collisions with the existing two. It looks up a customer by email address and requires a valid `@` in the input. Three new ambiguity cases were added:

| Case | Prompt | Expected Tool | Why it could collide |
|---|---|---|---|
| 11 | `"Find the customer with email john.doe@acme.com"` | `search_by_email` | Name-like local part could pull toward `search_customers` |
| 12 | `"Get the record for user@globex.com"` | `search_by_email` | "Record" mirrors case 8; without `@` detection could go to `search_orders` |
| 13 | `"Look up jane.doe"` | `search_customers` | Looks like an email local part but has no `@`; treated as a name |

All 13 cases passed at 100% across all three models. The key rule encoded in `search_by_email`: only use this tool when the input contains `@`. Without `@`, route to `search_customers` regardless of dot notation.
