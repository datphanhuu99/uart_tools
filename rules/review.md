# Review Guidelines

Use this file for code reviews, self-reviews after implementation, and risk scans before changing behavior.

## 1. Review Priorities

Lead with concrete findings, ordered by severity:

- Functional correctness defects
- TUI freezes, worker leaks, shutdown hangs, or unbounded serial blocking
- Protocol incompatibility with ECU firmware
- Data loss or accidental overwrite of presets/logs/configuration
- Exception swallowing that hides serial, decode, parse, or UI failures
- Missing verification for changed runtime behavior
- Readability issues that make future changes risky

If there are no findings, say so and still mention residual test gaps.

## 2. Ambiguity Rule

If a block looks like a bug but could be intentional feature behavior, do not silently "fix" it. Ask for clarification
or list it as an open question with the evidence.

## 3. Runtime Risk Checklist

Classify behavior changes as one or more of:

- `startup`
- `tui-context`
- `uart-worker`
- `protocol-format`
- `serial-io`
- `filesystem-config`
- `logging`

Then check whether the change affects:

- Textual lifecycle, screen mounting, bindings, or app-level state
- RX worker start/stop, exception handling, or callback handoff
- Serial port ownership, timeout, reconnect, or read/write blocking behavior
- Frame buffering, COBS/legacy framing, CRC, byte order, command IDs, or payload lengths
- YAML schema compatibility and duplicate `msg_id` parsing
- Preset/log path handling and user-data preservation
- Documentation, build/run commands, or test workflow

## 4. Evidence Standard

- Cite exact file paths and line references when available.
- Prefer source code and `formats/*.yaml` over external firmware notes when they disagree.
- Separate `Observed`, `Inferred`, `Missing`, and `Unknown` claims when surveying unfamiliar code.
- Do not call a runtime behavior verified unless the relevant path was actually exercised.

## 5. Review Output Shape

Use this order:

1. Findings
2. Open questions or assumptions
3. Verification performed and gaps
4. Brief change summary, only if useful
