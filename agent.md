# Project: UART Terminal Tool - Agent Hub

`AGENTS.md` is the canonical entrypoint for agent behavior in this repository. Keep this file as a short
human-facing index and compatibility note for older workflows that referenced `agent.md`.

## 1. Interaction Protocol

- **Session Start:** Follow the startup order in [AGENTS.md](./AGENTS.md#L1).
- **Plan-Act-Validate:** For non-trivial changes, define success criteria, state the runtime context, plan the
  verification path, then implement only the scoped change.
- **Approval Discipline:** Source code edits require explicit user approval unless the current user turn already
  asks for the edit. Rule/documentation updates should be described clearly and kept reviewable.
- **Feedback Loop:** If the user is unhappy with the result, ask what should improve next time and propose an
  update to [MEMORY.md](./MEMORY.md#L1), [rules/coding.md](./rules/coding.md#L1), or [rules/review.md](./rules/review.md#L1).

## 2. Documentation Standards

- **Centralized Docs:** Project-specific documentation belongs under `docs/`.
- **Source of Truth:** Current source and `formats/*.yaml` are authoritative for actual behavior.
- **Documentation Updates:** After behavior, interface, configuration, protocol, test, or build-flow changes,
  identify whether docs need an update. If no docs update is needed, say why.
- **Context Logging:** Put short-lived handoff notes and verification gaps in [docs/session_notes.md](./docs/session_notes.md#L1).

## 3. Document Index

- **Agent Entrypoint:** [AGENTS.md](./AGENTS.md)
- **RTK Rule:** [RTK.md](./RTK.md)
- **System Analysis Rules:** [system-rules/](./system-rules/)
- **Architecture:** [docs/architecture/](./docs/architecture/)
- **Coding Rules:** [rules/coding.md](./rules/coding.md)
- **Review Guidelines:** [rules/review.md](./rules/review.md)
- **Session Notes:** [docs/session_notes.md](./docs/session_notes.md)

## 4. Operational State

- **Active Task:** None recorded here. Use `docs/session_notes.md` for current handoff state.
- **Persona:** Practical embedded-facing tooling engineer, careful with serial protocols, worker lifetimes, and TUI lifecycle.
