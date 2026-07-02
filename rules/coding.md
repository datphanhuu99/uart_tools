# Coding Standards & Execution Workflow

This file is the canonical source for Python, Textual UI, UART, protocol, and configuration coding rules in this
repository. Read it before reviewing or editing files under `uart/`, `protocol/`, `ui/`, `formats/`, `presets/`,
or `main.py`.

## 1. Safe Execution Workflow

Every source-code change must follow this workflow:

- **Plan:** Before editing code, define the problem, affected files, intended logic, verification plan, and any
  decision points or tradeoffs.
- **Confirm:** Ask for explicit approval before editing source code unless the current user turn already asks for
  the edit.
- **Act:** Make surgical changes only in the scoped files.
- **Verify:** Run the narrowest useful checks and report the result. If hardware, serial loopback, or TUI execution
  is unavailable, state that verification gap clearly.

For documentation-only rule updates, keep the diff reviewable and do not change runtime code.

## 2. Coding Philosophy

- **Maintainability First:** Prefer code that is easy to read, inspect, and debug during ECU bring-up.
- **Simplicity Over Complexity:** Keep the existing modular boundaries. Add abstractions only when they remove real
  duplication or clarify ownership.
- **Protocol Compatibility:** Treat command IDs, payload layout, CRC/framing behavior, byte order, and value maps as
  compatibility contracts with ECU firmware.
- **Bounded Runtime Behavior:** Serial reads, writes, worker shutdown, and UI callbacks must not block indefinitely.
- **Local Style:** Match the naming, docstring, exception handling, and layout style already used in the touched file.

## 3. Runtime Ownership Rules

- `main.py` owns application startup and CLI argument flow.
- `ui/` owns Textual screens, bindings, presentation state, and user-facing messages.
- `uart/controller.py` owns orchestration between UI, serial transport, frame codec, and protocol helpers.
- `uart/serial_manager.py` owns pyserial port lifecycle, raw reads/writes, and log-file writes.
- `uart/rx_worker.py` owns background receive-loop lifetime and callback handoff.
- `uart/frame_codec.py`, `uart/cobs.py`, and `uart/crc.py` own framing, buffering, COBS, and CRC behavior.
- `protocol/` owns YAML loading, value mapping, packing, and parsing.
- `formats/*.yaml` define user-editable command/message/map contracts.
- `presets/` and `logs/` are user/runtime data. Do not overwrite them as part of tests unless the task explicitly
  targets them.

## 4. Textual UI Safety

- Before using lifecycle-dependent Textual methods such as `mount`, ensure the widget is in a valid mounted state.
- Prefer declarative UI composition through `compose()` or constructor-owned children over imperative nesting on
  widgets that may not be mounted yet.
- Keep long-running work outside the UI event path. Serial I/O and parsing loops must not block the Textual app loop.
- UI screens should reach shared runtime state through `self.app.controller` unless a more specific owner already
  exists.
- When changing screen IDs, bindings, or app-level attributes, search globally for all references before editing.

## 5. UART And Worker Safety

- Serial operations must have bounded timeouts or a documented reason why blocking is safe.
- Worker threads must have a clear stop path and must not prevent application shutdown.
- Callback handoff from `RXWorker` to controller/UI must preserve exception handling so receive-loop failures are
  visible in logs or UI state.
- Do not silently swallow decode, CRC, framing, or parse failures unless the caller has a documented recovery path.
- Avoid sharing mutable buffers across worker/UI boundaries without clear ownership.

## 6. Protocol And YAML Rules

- Keep YAML schemas backward-compatible unless the task explicitly changes the protocol contract.
- When adding or modifying RX layouts with the same `msg_id`, use `payload_len` or another explicit discriminator
  so parsing remains deterministic.
- Preserve byte order, CRC, COBS/legacy framing, and length-field assumptions unless the firmware-side impact is
  reviewed.
- Use structured YAML parsing and existing loader APIs. Do not parse YAML through ad hoc string manipulation.
- When editing `formats/*.yaml`, validate that the tool can load the file after the change.

## 7. Refactoring Safety

- When moving or renaming attributes, methods, command IDs, message IDs, or YAML fields, search the entire repo and
  update all references, including error paths and UI callbacks.
- Do not combine behavior changes with broad reformatting.
- Remove only code made unused by the current change.
- If a suspicious block might be intentional behavior, ask before changing it.

## 8. Commenting Rules

- Add short English comments only where logic would otherwise be hard to reconstruct.
- Comment timing, lifecycle, protocol compatibility, ownership, or recovery constraints when they are non-obvious.
- Do not add comments for straightforward assignments, obvious branches, or boilerplate control flow.

## 9. Verification Hints

- Syntax/import check: `rtk python -m compileall main.py uart protocol ui`
- App help/startup check when available: `rtk python main.py --help`
- YAML load check should exercise `FormatLoader` against `formats/commands.yaml`, `formats/rx_messages.yaml`, and
  `formats/maps.yaml`.
- Protocol changes should include representative pack/parse/frame-codec examples.
- UI changes should include at least a construction/import smoke check, and a real TUI smoke when practical.
