---
title: /council - Strategy Council Activation
type: note
---

# /council - Strategy Council Activation

Spawn the Strategy Council to deliberate on a major decision.

$ARGUMENTS is the question or decision.

## Steps

1. **Capture the question.** Use $ARGUMENTS or ask [YOUR NAME] to state it clearly.

2. **Gather context:** `ops/_index.md`, `ops/_goals.yaml`, relevant `{project-name}.context.md`, `ops/_tasks.md`.

3. **Spawn three agents in parallel:**

   - **str--strategist:** "Analyze [QUESTION] strategically. Long-term implications for [YOUR ORG UNIT] goals, system dynamics, leverage points, second-order effects. What's the highest-leverage move? Read ops/_goals.yaml."

   - **str--critic:** "Challenge assumptions in [QUESTION]. What could go wrong? Biases? What aren't we seeing? Worst case? Read relevant project context."

   - **str--researcher:** "Research [QUESTION]. Precedents, best practices, evidence. What have others done? What does data suggest?"

4. **Synthesize with str--synthesizer:** After all three report, spawn the synthesizer with their findings. Resolve tensions. Produce unified recommendation with confidence level.

5. **Present:**

```
## Strategy Council Recommendation

### Question
[What was deliberated]

### Recommendation
[Clear recommendation with reasoning]

### Confidence: [High/Medium/Low]

### Strategist's View
[Key strategic insight]

### Critic's Concerns
[Key risks and challenged assumptions]

### Evidence Base
[Researcher's findings]

### Alternatives Considered
[Other options with tradeoffs]

### Decision Framework
If [condition A] → [action A]
If [condition B] → [action B]
```

6. **Ask:** "Here's what the council recommends. What's your call?"

7. **Log the decision** to relevant `{project-name}.context.md` Key Decisions table with source: "Strategy Council deliberation [date]".

## When to Use

- Decisions with significant cost, time, or people impact
- Process design that will be repeated many times
- Strategic choices about where to invest time
- Multiple valid approaches exist
- "I'm not sure about this" / "help me think through this"

## Rules

- Council debates. [YOUR NAME] decides.
- Always present dissenting views, even if council converges.
- State confidence clearly.
- If council is split, present the split. Don't force consensus.
