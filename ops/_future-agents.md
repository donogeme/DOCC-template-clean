# Future Ops Agents Roadmap

**Status:** Planning — build when patterns emerge from real usage.

Don't build speculatively. Let pain points reveal themselves. An agent gets built when:
1. A pattern has repeated 3+ times across sessions
2. The manual effort is clearly wasteful (admin, not thinking)
3. The input/output contract is clear from real examples
4. Building it would free meaningful capacity

---

## Core Agents (Build These First)

| Agent | Purpose | Trigger Examples | Status |
|-------|---------|-----------------|--------|
| `ops--scheduler` | Calendar, deadlines, priorities, time-blocking, daily planning | "What's on my plate?" "Plan my day" | **Build when:** /gm is used 5+ times and scheduling logic is clear |
| `ops--tracker` | Follow-ups, loop-closing, stale item detection, nudge drafting | "What's overdue?" "Who am I waiting on?" | **Build when:** `_awaiting.md` has 10+ items and `/followup` is a regular workflow |
| `ops--briefer` | Draft emails, updates, status reports for upstream/downstream | "Draft an update for [boss]" "Weekly summary" | **Build when:** drafting patterns are established and voice guide is solid |
| `ops--processor` | Process meeting transcripts into structured notes, action items, decisions | "Process today's meetings" "Catch me up" | **Build when:** meeting volume is high and transcript source is stable |

---

## Future Possibilities (As Needs Emerge)

- `ops--decision-logger` — Capture decisions with rationale, stakeholders, alternatives considered, and date. Makes institutional knowledge retrievable.
- `ops--process-optimizer` — Analyze repeated workflows and suggest automation or streamlining
- `ops--people-manager` — Track 1:1s, feedback, development goals, delegation patterns
- `ops--onboarder` — Generate onboarding docs and context packages for new team members or handoffs

---

## Autonomous Communication Agent

**Goal:** Build an agent that autonomously handles routine communication tasks.

**Three paths:**

| Path | Approach | Effort | Notes |
|------|----------|--------|-------|
| 1. Claude Agent SDK | Python script using Anthropic SDK + existing MCP tools. Runs on schedule. Reads ops files, drafts communications, updates state. | 1-2 days | Best fit. Uses same model + MCP tools as DOCC. |
| 2. Extend existing bot | Add Claude-powered capabilities to existing Slack/Teams bot. Could handle nudges, loop closures, routing messages natively. | 1 day | Reuses existing infra. Channel-native. |
| 3. n8n / Make.com | No-code visual workflows. Email → Claude API → ops files. | Hours | Fast but limited reasoning about full ops context. |

**Good starting tasks for automation:**
- Stale nudges (X days no response → draft nudge email)
- Loop closure confirmations ("Got it, thanks" replies)
- Routing messages ("Forwarding this to X per routing table")
- Daily action digest (scan all channels, produce prioritized list)

---

## Transcript Search Scaling Strategy

| Tier | Trigger | Approach | Cost |
|------|---------|----------|------|
| 0 (Now) | <50 transcripts | Metadata queries + pre-indexed signals + on-demand body reads | Minimal |
| 1 | ~50+ transcripts | Add Topic Tags to transcripts DB; classifier extracts 3-5 tags per meeting | One extra field at write time |
| 2 | Topics aren't enough | Local transcript index (markdown/JSON) mapping topics/people/projects to IDs with summaries | File read instead of API calls |
| 3 | Hundreds of transcripts | Vector DB (Pinecone/Weaviate/Supabase pgvector) with chunked embeddings + RAG pipeline | Embedding API + vector DB hosting |

**Key insight:** An indexed signals/summary layer is already an effective index. Most retrieval needs can be met by searching summaries first, then deep-diving into full transcripts only when needed.

---

## Design Principles

- Agents should be optimized for YOUR recall through DOCC, not for reading files directly
- Output should be both machine-retrievable (for DOCC) and human-shareable (for teammates when needed)
- Start simple, add sophistication based on real friction
