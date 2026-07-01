"""Exercise 1, task 4 — subagents with explicit context passing.

Two subagents:
  - security-reviewer: tools Read, Grep, Glob — finds the issues in app/payments.py
    and buggy/utils.py.
  - test-writer:       tools Read, Write, Bash — writes tests and runs them.

The parent orchestrates: it has the Task tool (so it can delegate), the subagents do
NOT — they cannot spawn further subagents. The parent stitches the two subagents'
outputs into a single report.

⚠️ FLAG — two things to verify against your installed SDK:
  1. `AgentDefinition` is exported by claude-agent-sdk, but its exact field names
     (here: description / prompt / tools / model) were not fully confirmed in docs.
     Adjust to match your version if construction fails.
  2. "Task only in the parent, never in a subagent" — we enforce this by simply not
     granting subagents the Task tool. Whether the SDK also blocks nested delegation
     structurally was not confirmed; treat the no-Task-in-subagents rule as the
     design contract regardless.

Setup:
    pip install claude-agent-sdk
    python task4_subagents.py
"""

import asyncio
from pathlib import Path

from claude_agent_sdk import AgentDefinition, ClaudeAgentOptions, query

HERE = Path(__file__).parent

# Subagent rosters. NOTE: neither list contains "Task" — subagents must not delegate.
SECURITY_REVIEWER = AgentDefinition(
	description="Reviews code for security and correctness issues. Read-only.",
	prompt=(
		"You are a security reviewer. Use Grep/Glob/Read to inspect the code. Report "
		"concrete issues (weak hashing, missing validation, crash-on-edge-input) with "
		"file and line references. Do not modify any files."
	),
	tools=["Read", "Grep", "Glob"],
	model="sonnet",
)

TEST_WRITER = AgentDefinition(
	description="Writes and runs unit tests for the issues the reviewer finds.",
	prompt=(
		"You are a test writer. Read the relevant files, write pytest tests that "
		"reproduce the reported bugs (empty-list average, missing-key user, negative "
		"charge amount), and run them with Bash. Report which pass and which fail."
	),
	tools=["Read", "Write", "Bash"],
	model="sonnet",
)

PARENT_PROMPT = (
	"Coordinate a review of this project.\n"
	"1. Delegate to the 'security-reviewer' subagent to find issues in "
	"app/payments.py and buggy/utils.py.\n"
	"2. Delegate to the 'test-writer' subagent to write and run tests for those "
	"issues.\n"
	"3. Stitch their outputs into ONE report with two sections: 'Findings' and "
	"'Tests', and a final verdict line.\n"
	"You (the parent) own delegation via the Task tool; the subagents do not "
	"delegate further."
)


async def main() -> int:
	options = ClaudeAgentOptions(
		# The parent gets Task (to delegate) plus read tools; subagents' tools are
		# defined on each AgentDefinition above.
		allowed_tools=["Task", "Read", "Glob"],
		agents={
			"security-reviewer": SECURITY_REVIEWER,
			"test-writer": TEST_WRITER,
		},
		permission_mode="acceptEdits",
		cwd=str(HERE),
	)
	agent_by_task: dict[str, str] = {}        # Task call id -> subagent name
	tools_used: dict[str, set[str]] = {}      # subagent name -> tools it called

	async for message in query(prompt=PARENT_PROMPT, options=options):
		kind = type(message).__name__
		if kind == "AssistantMessage":
			# Who emitted this? Parent (parent_tool_use_id is None) or a subagent?
			owner = agent_by_task.get(getattr(message, "parent_tool_use_id", None), "parent")
			for block in getattr(message, "content", []):
				btype = type(block).__name__
				if btype == "TextBlock":
					print(block.text)
				elif btype == "ToolUseBlock":
					# This SDK streams the delegation tool as "Agent"; the parent's
					# allow-list names it "Task". Match both.
					if block.name in ("Task", "Agent"):
						# Parent delegating: map this call id to the subagent it spawns.
						sub = block.input.get("subagent_type", "?")
						agent_by_task[block.id] = sub
						print(f"[delegate] -> {sub}")
					else:
						# A tool call by whoever owns this message.
						tools_used.setdefault(owner, set()).add(block.name)
						print(f"[{owner}] {block.name}")
		elif kind == "ResultMessage":
			print(f"[done] cost_usd={getattr(message, 'total_cost_usd', None)}")

	# Per-subagent tool breakdown — the answer to "which tools did each one use".
	print("\n=== tools used per agent ===")
	for agent, tools in sorted(tools_used.items()):
		print(f"  {agent}: {sorted(tools)}")
	return 0


if __name__ == "__main__":
	raise SystemExit(asyncio.run(main()))
