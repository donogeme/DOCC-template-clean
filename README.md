# DOCC — Distributed Operations Command Console

A personal AI operating system built on Claude Code. DOCC turns Claude into a persistent, context-aware operations partner — not just a chat assistant.

## What This Is

DOCC is a structured set of files, rules, and slash commands that give Claude Code a persistent operating context. Instead of re-explaining your situation every session, DOCC maintains a living picture of your projects, tasks, contacts, and open loops — and Claude uses that context to help you work faster.

**Core design goals:**
- Double the operator's productivity by automating administrative overhead
- Create documentation as a byproduct of work (not a separate activity)
- Nothing falls through the cracks (loop tracking, source citation, project state)
- Evolve from real usage, not upfront design

## Core Concepts

### Three Buckets of Work

All work falls into one of three categories:

| Bucket | What It Is | Example |
|--------|-----------|---------|
| **Route** | Work that flows through you because of your context and relationships | Answering questions, connecting people, coordinating across teams |
| **Execute** | Work that requires your hands on it | Data analysis, procurement, configuration, process work |
| **Think** | Strategy, planning, capability building — highest leverage | Architecture decisions, team structure, process design |

The goal: improve Route and Execute efficiency to free more time for Think.

### The Capture Layer

Documentation happens as a byproduct of working through DOCC — not as a separate activity. Conversations build `_kb.md`. Project work builds context files. Decisions produce source-cited records automatically.

### Engines, Skills, Agents

**Engines** are persistent systems for different types of work:
- **Router** — communication, people connection, information sharing
- **Executor** — repeatable task work, process automation
- **Coordinator** — multi-person project tracking, deadlines, accountability
- **Strategist** — long-range planning, decision support

**Skills** are shared capabilities any engine can use:
- Data Analysis, Technical Writing, Research, Drafting

**Agents** are engine + skills combined for a specific job (e.g., `ops--scheduler`, `ops--tracker`).

**DOCC** is the interface layer — it routes to the right engine based on what you need.

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/docc.git
cd docc
```

### 2. Set up your identity in `CLAUDE.md`

Open `CLAUDE.md` and replace the placeholder sections:
- `[YOUR NAME]` — your name
- `[YOUR ROLE]` — your role/function
- `[YOUR BOSS]` — who you report to
- `[YOUR DIRECT REPORTS]` — who reports to you (or leave blank)
- Voice guide — update `ops/_voice.md` with your writing style

### 3. Initialize your ops files

```bash
cp ops/_goals.yaml.example ops/_goals.yaml
cp ops/_contacts.md.example ops/_contacts.md
```

Edit these with your actual goals and key contacts.

### 4. Open in Claude Code

```bash
claude .
```

Run `/gm` to start your first morning briefing.

## File Structure

```
docc/
├── CLAUDE.md                    # System instructions (read by Claude every session)
├── .claude/
│   └── rules/
│       └── ops.md               # Always-active operational rules
├── ops/
│   ├── _index.md                # Master project registry
│   ├── _tasks.md                # Unified task list
│   ├── _awaiting.md             # Open loops / waiting on others
│   ├── _contacts.md             # People catalog
│   ├── _kb.md                   # Domain knowledge base
│   ├── _goals.yaml              # Your OKRs / objectives
│   ├── _voice.md                # Your writing style guide
│   ├── _google-chat-spaces.md   # Chat space ID mapping (if using Google Chat)
│   ├── _architecture.md         # System architecture (evolves with usage)
│   ├── _future-agents.md        # Agent development roadmap
│   ├── _changelog.md            # System changes log
│   └── {project-name}/
│       ├── {project-name}.context.md   # Living project state
│       └── {date}-{description}.md     # Dated notes (calls, meetings, etc.)
└── .claude/
    └── commands/                # Slash command definitions
```

## Slash Commands

| Command | Purpose |
|---------|---------|
| `/gm` | Morning briefing — scan all channels, surface priorities, plan the day |
| `/triage` | Multi-channel inbox scan — check for new messages needing response |
| `/sitrep` | Generate upstream or downstream status report |
| `/followup` | Find stale loops — things you're waiting on with no response |
| `/council` | Strategy Council — major decisions get multi-perspective analysis |
| `/meetings` | Process meeting transcripts into decisions and action items |
| `/route` | Route a question/request to the right person |
| `/classify` | Classify inbox items: IGNORE / FYI / ACTION:ME / ACTION:ROUTE |
| `/work` | Execute green-light tasks autonomously |
| `/queue` | What's on my plate right now? |
| `/close` | Session flush — persist all context before ending |

## Data Files

### `ops/_tasks.md`
Unified task list across all projects. Tiered by priority (Critical / High / Medium / Deferred). Critical is capped at 8 items. Tasks include owner, due date, project, and source.

### `ops/_awaiting.md`
Everything you're waiting on from others. Automatically tracked when you ask someone for something. Checked during `/triage` and `/followup` for responses.

### `ops/_kb.md`
Domain knowledge base — organized by topic headers. Grows as you work. Contains decision patterns, domain knowledge, and operational rules you've shared with Claude. Read before drafting to avoid repeating yourself.

### `ops/{project-name}.context.md`
Living project state. Every project gets one once it has enough complexity. Contains: current state, key people, key decisions (source-cited), open questions, and a sources table.

## Session Persistence

Three layers ensure context is never lost:

1. **Auto-save** (continuous) — After substantive work, DOCC persists to the relevant files immediately. No prompt needed.
2. **`/close` command** (comprehensive) — Full session review that catches anything auto-save missed.
3. **SessionEnd hook** (safety net) — Logs which ops files were modified when the session ends.

## Guardrails

- **Never send emails without explicit approval** — Draft and present. Wait for confirmation.
- **Never fabricate information** — Unknown = say so. Uncertain = state confidence level.
- **Never skip source citations** — Every claim traces to an email, chat, meeting, or document.
- **Confirm before irreversible actions** — Sending messages, modifying shared documents, calendar changes.

## Integrations

DOCC is built to work with these MCP servers (configure in your MCP settings):

| Integration | MCP Server | Used For |
|-------------|-----------|---------|
| Gmail | Google MCP | Email scanning, drafting, sending |
| Google Chat | Google MCP | Chat scanning, message lookup |
| Google Calendar | Google MCP | Scheduling, event lookup |
| Google Drive | Google MCP | Document retrieval |
| Google Sheets | Google MCP | Data lookups |
| Notion | Notion MCP | Meeting transcripts, project tracking |
| Slack | Slack MCP | Channel monitoring (read-only) |

You can use DOCC with fewer integrations — Claude will note which sources are unavailable and work with what's there.

## Agents

### Operations Team (`ops--`)

| Agent | Role |
|-------|------|
| `ops--scheduler` | Calendar, deadlines, daily planning |
| `ops--tracker` | Follow-ups, stale loop detection |
| `ops--briefer` | Status reports, upstream/downstream updates |
| `ops--processor` | Meeting transcript processing |

### Strategy Council (`str--`)

For major decisions — spawns multiple perspectives:

| Agent | Role |
|-------|------|
| `str--strategist` | Long-term implications, system dynamics |
| `str--critic` | Devil's advocate, risk detection |
| `str--researcher` | Evidence gathering, best practices |
| `str--synthesizer` | Integrates perspectives into a recommendation |

## Design Principles

1. **Iterate, don't over-engineer** — Build when real friction demands it, not speculatively
2. **Documentation is a byproduct** — Working through DOCC produces the paper trail automatically
3. **Engines chain together** — Work flows across buckets; don't design them as silos
4. **Skills are shared** — Capabilities belong to the system, not to any one engine
5. **Adapt both ways** — You adapt where the system makes you more effective; system adapts where your judgment is the value-add
6. **System handles the how** — You focus on the what and why
7. **Auto-save, don't prompt** — When Claude knows enough to ask, it knows enough to just do it

## Evolving the System

DOCC grows from real usage. New agents get built when a pattern repeats 3+ times. Commands are added when the workflow demands it.

**Build criteria for a new agent:**
1. A pattern has repeated 3+ times across sessions
2. The manual effort is clearly wasteful (admin, not thinking)
3. The input/output contract is clear from real examples
4. Building it would free meaningful capacity

**Project promotion** — DOCC auto-proposes creating a project context file when a topic shows up repeatedly across `_tasks.md`, `_awaiting.md`, and conversations. No manual filing needed.

## Contributing

This system is designed to be forked and adapted. The core framework (engines, agents, slash commands, file structure) is generic. Your specific content (contacts, projects, goals, KB) is yours.

If you build something useful on top of DOCC, PRs welcome.

## License

MIT
