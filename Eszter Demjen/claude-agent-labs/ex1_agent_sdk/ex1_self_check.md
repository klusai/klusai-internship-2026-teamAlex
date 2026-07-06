# Exercise 1 — Self-Check Answers

## Tool restriction for the bug-fixer

The agent only needed Glob to locate files, Read to inspect them, and Edit to patch them. No Bash was required to complete the task. Granting Bash under acceptEdits mode, where actions apply automatically, would expand the agent's capabilities well beyond what the task needed.

## Source of cost without a budget option

There is no preventive budget parameter. ResultMessage.total_cost_usd is computed and reported only after a run finishes, based on actual token usage. Cost control is therefore reactive: log the cost, flag it if it exceeds a ceiling, and stop further turns. The only preventive lever is max_turns, set in advance.

## Why Task stays in the parent only

Keeping Task parent-only gives one place visibility over the full delegation tree. In testing, a subagent without execution access tried over a dozen workarounds when blocked, escalating through different shells, interpreters, and sandbox-bypass flags. A subagent with its own Task tool could have spawned further subagents to keep escalating, with no single point able to observe or stop it.

## Findings from running the exercise

Agents initially guessed wrong working-directory paths in task1 and task4 before self-correcting.

max_budget_usd does not exist in the installed SDK. max_turns and total_cost_usd are the real levers.

Session management helpers (rename_session, tag_session, list_sessions) were available, contrary to the original uncertainty. The real issue was signature mismatches: list_sessions takes no tag filter and must be filtered client-side on the tag field returned per session.

An unscoped delegation prompt in task4 caused a subagent to read and write files in a sibling teammate's project folder. Adding an explicit directory boundary to the prompt fixed this on rerun.

Bash and PowerShell execution of pytest was blocked in this environment even with sandbox-disable flags. Subagents could write valid tests but not run them. Running the test file manually outside the agent loop was needed to get real results, and also caught a case where an agent reported test results from an unexecuted static trace rather than an actual run.
