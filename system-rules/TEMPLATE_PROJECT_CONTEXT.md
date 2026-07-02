# Project Context Template

Use this template to summarize a project after applying the rules in [`RULES.md`](./RULES.md).

## 1. Project Summary

- Project name:
- System type:
- Primary purpose:
- Primary runtime environment:
- Observed entrypoints:
- Context confidence:

## 2. Source Coverage

- Observed:
- Missing:
- Unknown:

## 3. Top-Level Structure

| Path | Role | Notes |
| --- | --- | --- |
| `/` |  |  |

## 4. Architecture Map

### Logical layers

- Layer:
  Responsibility:
  Key files:

### Major subsystems

- Subsystem:
  Responsibility:
  Owner files:
  Depends on:
  Used by:

## 5. Runtime And Control Flow

### Bootstrap sequence

1.
2.
3.

### Continuous runtime behavior

- Main loop / request loop / worker loop:
- Scheduler / timer model:
- Event sources:
- State machines:
- Reset / shutdown / recovery behavior:

## 6. Configuration Model

### Static configuration

- Source:
- Important values:
- Risks:

### Runtime configuration

- Source:
- Persistence:
- Defaults:
- Reset behavior:

### Secrets / credentials

- Observed locations:
- Handling notes:

## 7. Communication Model

### Internal communication

- Queues / buffers:
- Callbacks:
- Shared state:
- Message formats:

### External communication

- Interface:
  Protocol:
  Files:
  Addressing / command pattern:
  Payload shape:
  Retry / timeout behavior:

## 8. Peripheral / Infrastructure Interfaces

Use this section for hardware buses, OS services, databases, brokers, cloud services, external binaries, or device control.

- Interface:
  Purpose:
  Configuration files:
  Runtime files:
  Notes:

## 9. Internal API Surfaces

- API / function family:
  Defined in:
  Used by:
  Contract summary:

## 10. Logging, Debugging, Diagnostics

- Logging mechanism:
- Key log points:
- Debug/test hooks:
- Launch/debug configs:
- Failure handling:

## 11. Build / Deploy / Run

- Toolchain:
- Build files:
- Artifact outputs:
- Deploy path:
- Debug launch path:
- Environment assumptions:

## 12. Dependency And Availability Status

- Vendored dependencies:
- Generated code:
- Referenced but missing source:
- External tools required:

## 13. File Reading Order For Safe Changes

### If changing runtime flow

- Read:

### If changing configuration

- Read:

### If changing communication / protocol

- Read:

### If changing hardware-facing integrations

- Read:

## 14. Risks, Mismatches, Ambiguities

- Risk:
  Evidence:
  Impact:

## 15. Recommended Follow-Up

-
