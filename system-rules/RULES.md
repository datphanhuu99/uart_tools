# System Rules

Use this folder when entering an unfamiliar codebase and you need a durable, transferable understanding of how
the system is organized, configured, operated, and extended.

This folder is generic process guidance. It is not the canonical source of project-specific architecture or
runtime truth. Project-specific conclusions belong under the repo's `docs/` tree.

## Goal

Produce a project context that lets another engineer or agent answer these questions quickly:

- What does this project do?
- How is the codebase divided?
- What starts first, what runs continuously, and what triggers what?
- Where do configuration values come from and where are they stored?
- How does the system communicate internally and externally?
- Which files define protocols, APIs, logs, debug paths, and operational risks?
- What is missing, risky, generated, or environment-dependent?
- Which files must be read before making changes?

## Output Contract

For each project, create a filled project context from [`TEMPLATE_PROJECT_CONTEXT.md`](./TEMPLATE_PROJECT_CONTEXT.md).

The context must distinguish clearly between:

- `Observed`: directly confirmed from source or config files.
- `Inferred`: likely true from structure or naming, but not fully confirmed.
- `Missing`: referenced by the codebase but not present or not inspectable.
- `Unknown`: important but not discoverable from the available files.

Do not blur these categories.

## Survey Workflow

1. Read top-level files first.
   Start with `README`, project manifests, launch/debug files, protocol docs, and configuration files.

2. Map the directory structure.
   Identify layers such as UI, coordinator, protocol, transport, configuration, logs, tests, docs, and scripts.

3. Find the bootstrap path.
   Trace from the main entrypoint into initialization order, background workers, callbacks, and shutdown behavior.

4. Locate configuration sources.
   Capture environment/config files, persisted runtime config, defaults, reset behavior, credentials, and feature flags.

5. Map communication paths.
   Record internal callbacks, queues, worker threads, state machines, UART, file I/O, and protocol payload schemas.

6. Map system interfaces.
   Record APIs, module contracts, command surfaces, callback registration, payload schemas, and event models.

7. Map operational observability.
   Record logs, debug helpers, tracing hooks, test functions, CLI/debug commands, launch configs, and failure handling.

8. Identify external dependencies.
   Record package dependencies, missing folders, toolchain assumptions, hardware assumptions, and infrastructure assumptions.

9. Record change-entry guidance.
   List the files that must be read before editing each subsystem.

10. Record risks and gaps.
    Call out mismatches between docs and code, hard-coded assumptions, dead code, partial implementations, and unverifiable
    assumptions.

## Required Sections

Every project context must cover these areas:

1. Project purpose and system type
2. Top-level structure
3. Runtime and control flow
4. Configuration model
5. Communication model
6. Peripheral or infrastructure interfaces
7. Internal API surfaces
8. Logging, debugging, and diagnostics
9. Build, deploy, and run workflow
10. Dependency and source-availability status
11. Safe change guide
12. Risks, ambiguities, and follow-up questions

## Rules For Writing The Context

- Prefer concise statements over prose.
- Cite real file paths for every important claim.
- Group by subsystem, not by discovery order.
- Capture both structure and behavior.
- Note update frequency, timers, retries, and state transitions when relevant.
- Call out generated or user-data files separately from handwritten source.
- Separate logical architecture from physical interfaces for hardware-facing tools.
- If docs disagree with source, say so explicitly and prefer source as the current implementation unless proven otherwise.
- Never mark secrets as safe just because they are in source control.

## Heuristics By Project Type

### UART / Hardware-Facing Tools

Also capture:

- Serial port assumptions, baudrate defaults, timeout behavior, reconnect behavior, and shutdown path
- Framing, CRC, byte order, payload schemas, and compatibility with target firmware
- RX/TX worker ownership, queues/callbacks, and thread-safety boundaries
- User-data files such as presets and logs
- Hardware availability needed for verification

### Frontend / Desktop / TUI

Also capture:

- Routing/screens, state ownership, widget lifecycle, background workers, and event callbacks
- Build/run pipeline, environment assumptions, and error reporting

### Backend / Services

Also capture:

- Process model, workers, queues, scheduled jobs
- DB ownership, migration flow, cache and broker dependencies
- Auth model, request lifecycle, external service integrations

## Safe Change Guidance

Before editing any subsystem, identify:

- The owner files that define the contract
- The runtime entrypoints that invoke it
- The persistence or protocol surfaces affected
- The logs or tests that would confirm behavior

If any required dependency is missing from the repo, document that limit before making deep changes.

## Deliverables In This Folder

- [`RULES.md`](./RULES.md): portable analysis rules
- [`TEMPLATE_PROJECT_CONTEXT.md`](./TEMPLATE_PROJECT_CONTEXT.md): reusable context template
- [`CHECKLIST.md`](./CHECKLIST.md): short execution checklist
