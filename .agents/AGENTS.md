# Project Rules & Customizations

Use the root [AGENTS.md](../AGENTS.md#L1) as the canonical project entrypoint.

This file exists for tools that discover `.agents/AGENTS.md` first. It intentionally mirrors only the high-level
rules so there is a single place to maintain detailed behavior.

## Required Reads

1. [../RTK.md](../RTK.md#L1)
2. [../AGENTS.md](../AGENTS.md#L1)
3. [../MEMORY.md](../MEMORY.md#L1)
4. [../docs/session_notes.md](../docs/session_notes.md#L1)
5. [../rules/coding.md](../rules/coding.md#L1)
6. [../rules/review.md](../rules/review.md#L1)

## Safety Defaults

- Prefix shell commands with `rtk`.
- Keep source changes scoped and verify them with the runtime context they affect.
- Treat `formats/*.yaml`, presets, logs, serial I/O, worker threads, and Textual widget lifecycle as compatibility
  surfaces that require explicit review when changed.
- If a behavior change affects protocol, runtime flow, configuration, build flow, or tests, update docs or state why
  no documentation update is needed.
