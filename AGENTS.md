# Agent Instructions

Use this file as the repo entrypoint only.

Startup order:

1. Read [RTK.md](RTK.md#L1) for the shell-command execution rule.
2. Read [system-rules/RULES.md](system-rules/RULES.md#L1) for the generic analysis workflow.
3. Use [system-rules/CHECKLIST.md](system-rules/CHECKLIST.md#L1) while surveying unfamiliar areas.
4. Read [MEMORY.md](MEMORY.md#L1) for durable user preferences and lessons learned.
5. Read [docs/session_notes.md](docs/session_notes.md#L1) for current project state, handoff notes, and known verification gaps.
6. Read [README.md](README.md#L1) and [docs/architecture/README.md](docs/architecture/README.md#L1) for the canonical project overview.
7. Read [rules/coding.md](rules/coding.md#L1) before reviewing or editing Python runtime code, protocol files, or Textual UI code.
8. Read [rules/review.md](rules/review.md#L1) before review work or before changing behavior.

Documentation roles:

- `docs/`: canonical project-specific architecture, session notes, feature notes, integration notes, and test notes.
- `MEMORY.md`: durable user preferences, recurring mistakes, and long-lived agent memory.
- `docs/session_notes.md`: short-lived continuation memory for recent task state, assumptions, and verification gaps.
- `rules/`: project-specific coding and review rules for this UART terminal tool.
- `system-rules/`: reusable analysis rules, checklists, and templates. Do not treat it as project architecture truth.

Priority of evidence for this repo:

1. Source code in `main.py`, `uart/`, `protocol/`, and `ui/`
2. Protocol/configuration files in `formats/` and persisted state in `presets/`
3. Project documentation under `docs/`, `README.md`, and `MEMORY.md`
4. Project-specific process guidance under `rules/`
5. Generic process guidance under `system-rules/`
6. External documents or firmware projects outside this repo

Behavioral rule scope:

- The following sections define default agent behavior for code and documentation work in this repository.
- Follow them unless a higher-priority system or developer instruction overrides them.
- This project is a Python UART terminal tool that communicates with ECU firmware. Do not apply STM32CubeMX,
  HAL, linker-script, or generated-firmware rules unless the task explicitly crosses into firmware work.

Engineering Principles:

- Purpose: decision-making rules before implementation.

- Think before coding. State assumptions explicitly when they affect implementation.
- If multiple interpretations are plausible, present them instead of choosing silently.
- Prefer the simplest approach that fully satisfies the request.
- Surface tradeoffs when they matter.
- If a requirement is materially unclear and a reasonable assumption would be risky, stop and ask.
- Prioritize tool stability: do not write code that can freeze the TUI, block shutdown indefinitely, leak worker
  threads, or block serial reads/writes without bounded timeouts.

Working Style:

- Purpose: scope-control rules while editing existing code or docs.

- Always ask for permission and obtain explicit user approval before modifying source code files unless the user
  has already made an explicit edit request for the current turn.
- Make surgical changes. Touch only the files required for the task.
- Do not refactor, reformat, or clean up unrelated code, comments, or structure.
- Match the local style of the file or subsystem, even if another style would also be valid.
- Remove only imports, variables, functions, or code paths that your own change made unused.
- If you notice unrelated dead code or design issues, mention them without changing them unless asked.
- Add short explanatory comments when logic would otherwise be hard to reconstruct from code alone.
- Prefer comments that explain constraints, rationale, or non-obvious flow, not comments that restate obvious code.

Planning And Verification Rules:

- Purpose: turn requests into verifiable work and close tasks with explicit evidence.

- Define concrete success criteria before implementation when the task is more than trivial.
- Translate broad requests into verifiable goals whenever practical.
- For multi-step tasks, state a short plan and include how each step will be checked.
- For bug fixes, reproduce or clearly identify the failure mode first when practical, then verify the fix.
- Do not treat the task as complete until the requested behavior is verified or the verification limit is stated explicitly.

UART Tool Change Checks:

- Purpose: pre-implementation classification and runtime risk scan.

- Before editing behavior, classify the requested change as one or more of:
  - `startup`
  - `tui-context`
  - `uart-worker`
  - `protocol-format`
  - `serial-io`
  - `filesystem-config`
  - `logging`
- State the runtime context that owns the change before implementation if it is not already obvious.
- Check whether the change affects any of the following:
  - Textual widget lifecycle, screen mounting, or app state ownership
  - RX worker thread lifetime, shutdown path, or callback flow
  - Serial timeout, blocking time, reconnect behavior, or port ownership
  - Frame buffering, COBS/legacy framing, CRC behavior, or byte order
  - YAML schema compatibility for `formats/*.yaml`
  - Preset/log file compatibility or path handling
- If the change touches live serial behavior, name the timing and hardware assumptions explicitly.
- Do not treat `import succeeded` as sufficient verification for UI, serial, worker, or protocol changes.

Runtime Verification:

- Purpose: choose the verification method that matches the runtime context after implementation.

- Match the verification method to the runtime context:
  - `startup`: run the app entrypoint help/import path, plus a smoke run when practical
  - `tui-context`: Textual import/screen construction check, plus manual or automated UI smoke where available
  - `uart-worker`: unit/smoke coverage for worker start/stop, callback handoff, and bounded shutdown
  - `protocol-format`: parser/packer/frame-codec tests with representative TX/RX payloads
  - `serial-io`: pyserial path review plus hardware or loopback verification when available
  - `filesystem-config`: read/write test for YAML, presets, or logs without overwriting user data
  - `logging`: confirm log path, timestamp behavior, and failure handling
- If ECU hardware, a serial loopback, or a terminal UI cannot be exercised, state the exact verification gap.

Repo-specific rules:

- Prefer current source and `formats/*.yaml` over external firmware documents when they disagree.
- Treat `formats/*.yaml` as protocol contracts used by the tool and the ECU firmware.
- For changes to command IDs, payload layouts, CRC/framing mode, byte order, or value maps, identify the
  firmware-side compatibility risk before implementation.
- For any source change that affects behavior, ownership, interface, runtime flow, configuration, build flow,
  or test flow, explicitly identify the documentation files that should be updated before closing the task.
- If no documentation update is needed for such a source change, state that conclusion explicitly and justify it.
- Do not overwrite user presets, logs, or local serial configuration while testing.
- For important claims, cite concrete file paths and line references when available.

Coding rules:

- Project coding and refactoring rules are defined in [rules/coding.md](rules/coding.md#L1).
- Review rules are defined in [rules/review.md](rules/review.md#L1).
- Read the relevant rule file before reviewing or editing matching code.

@RTK.md
