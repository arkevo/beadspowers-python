# Never Ask Which Model an Agent Run Uses

**Section:** Interaction Guidelines

The model tier a workflow, subagent or fan-out runs on is configuration, not a user
decision. Never print it in a budget gate, list it as an option, or ask for confirmation
of it. A budget gate may show scope, agent count, artifacts and a cost band against "the
5-hr usage limit" — no `Model:` line.

In `opts.model`, use only tier aliases (`"opus"`, `"sonnet"`, `"haiku"`, `"fable"`),
never a versioned model id: a pinned version strands the fan-out on a superseded
generation and goes stale in every gate that prints it.

If the user asks, answer plainly: name the tier, or read the resolved id back from the
run.
