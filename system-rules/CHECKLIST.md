# Project Analysis Checklist

Use this as a short execution checklist while reading a new project.

- Read top-level docs, manifests, run commands, launch/debug configs, and protocol/configuration files.
- Identify handwritten code versus generated files, user data, presets, and logs.
- Trace the real entrypoint and initialization order.
- Identify the always-running loop, worker thread, callback flow, or request lifecycle.
- Map configuration defaults, persistence, reset paths, and secrets.
- Map communication paths: internal and external.
- Map hardware-facing interfaces, integrations, or infrastructure dependencies.
- List the core APIs and module boundaries.
- Find logs, debug helpers, test hooks, and failure handlers.
- Record missing source, external dependencies, or unverifiable assumptions.
- Fill `TEMPLATE_PROJECT_CONTEXT.md` with `Observed`, `Inferred`, `Missing`, and `Unknown` clearly separated.
- End with a safe change guide: which files to read first before editing each subsystem.
