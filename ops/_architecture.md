# DOCC Architecture

**Status:** Living document. Iterated through real usage, not upfront design.

---

## The Three Buckets of Work

All work falls into three categories. Each requires different tools, skills, and systems.

### Bucket 1: Route (People/Coordination)
Work that flows through you because of your context, relationships, and position in the network. You're a router, not the executor.

- **Information routing** — someone asks a question, you know the answer or know who does
- **Project coordination** — making sure everyone does their job on time
- **Key insight:** If your knowledge is documented (second brain), most routing can be automated or at least draft-assisted

### Bucket 2: Execute (Action/Task)
Work that requires your hands on it. Data analysis, procurement, configuration, process work.

- **Key insight:** If you can articulate how to solve it tactically, you can codify it, systematize it, then automate it
- **Maturity path:** Manual → Documented → Semi-automated → Fully automated

### Bucket 3: Think (Strategy/Planning)
No people coordination, no tactical action. Planning, team structure, capability building, architecture decisions, upskilling.

- This is the highest-leverage work
- The goal of improving Buckets 1 and 2 is to free more time for Bucket 3
- Strategy Council supports this work but doesn't replace the thinking

### The Capture Layer (runs across all three)
Documentation happens as a byproduct of doing the work, not as a separate activity.

- Router conversations build the scoped KB (`ops/_kb/`)
- Executor runs build process playbooks
- Coordinator work builds project history
- Strategy sessions build decision records

---

## Framework: Engines, Skills, Agents

### Engines
Persistent systems with their own data, workflows, and state. They represent *types of work* with fundamentally different patterns.

| Engine | Purpose | Maps to Bucket | Status |
|--------|---------|---------------|--------|
| **Router** | Communication, people connection, information sharing | Route | Build when: routing table (`_routing.md`) fills up, `/route` command gets regular use |
| **Executor** | Repeatable task work, process automation | Execute | Build when: 3+ processes are documented and repeatable |
| **Coordinator** | Multi-person project tracking, deadlines, accountability | Route + Execute | Partially built via awaiting, tasks, project context files |
| **Strategist** | Long-range planning, decision support, capability building | Think | Built via Strategy Council agents |

### Skills
Shared capabilities any engine can call on. Not tied to a specific type of work.

| Skill | Description | Used By |
|-------|-------------|---------|
| **Data Analysis** | Counts, comparisons, trend spotting, root cause analysis | Any engine |
| **Technical Writing** | Decision records, runbooks, reports | Any engine |
| **Research** | Gathering info from multiple sources, web search, doc review | Any engine |
| **Drafting** | Writing in the operator's voice for emails, updates, reports | Router, Coordinator |

### Agents
Engine + skills combined for a specific job. An agent has a role, the right engine context, and the skills it needs.

Core agents: `ops--scheduler`, `ops--tracker`, `ops--briefer`, `ops--processor`, plus the Strategy Council (`str--*`).

**Build criteria for a new agent:**
1. A pattern has repeated 3+ times across sessions
2. The manual effort is clearly wasteful (admin, not thinking)
3. The input/output contract is clear from real examples
4. Building it would free meaningful capacity

### How They Relate
- DOCC is the interface layer (persona, orchestrator)
- DOCC routes to the right engine based on the type of work
- Engines call on skills as needed
- Agents are pre-configured engine+skill combos for common jobs

---

## Engine Interconnection

Engines are not silos. Real work chains across engines:

**Typical patterns:**
- Router (gather inputs) → Executor (do the work) → Router (distribute output)
- Strategist (decide what) → Coordinator (assign work) → Executor (do it) → Router (share results)
- Coordinator (detect a gap) → Router (collect info) → Executor (fix it) → Coordinator (close the loop)

Don't pre-engineer handoff patterns. Let them emerge from real usage and document them as they become clear.

---

## Design Principles

1. **Iterate, don't over-engineer.** Build when real friction demands it, not speculatively.
2. **Documentation is a byproduct, not an activity.** Working through DOCC produces the paper trail automatically.
3. **Engines chain together.** Don't design them as silos. Work flows across buckets.
4. **Skills are shared.** Data analysis and technical writing belong to the system, not to any one engine.
5. **Adapt both ways.** You adapt to the system where it makes you more effective. The system adapts to you where your judgment is the value-add.
6. **The system handles the *how*, you focus on the *what* and *why*.**
7. **Auto-save, don't prompt.** When DOCC knows enough to ask, it knows enough to just do it.

---

## What's Next (driven by usage, not by plan)

Update this section as the system evolves:

- [ ] Router Engine: routing table (`_routing.md`) with domain-to-owner entries
- [ ] Executor engine: codify first repeatable process
- [ ] Coordinator improvements: automated check-ins, deadline tracking
- [ ] Process playbook format: define how codified processes are stored and replayed
