# ECU Config Desktop App - AI Development Guidelines & Skills

## Project Overview

A desktop application for ECU configuration management.

The application is used to:

* Connect to ECU/MCU through UART/Serial
* Send configuration data to ECU
* Read realtime data from ECU
* Display ECU status, logs, and diagnostic information
* Save and load configuration files locally

## Tech Stack

* **Application Type**: Desktop App
* **Frontend/UI**: Python GUI
* **Backend/Application Logic**: Python
* **Communication**: UART/Serial
* **Storage**: Local File
* **Packaging**: PyInstaller or similar tool

---

## Core Development Principles

### Always Follow These Rules

* Always inspect existing code, `docs/`, and `skills/` before changing anything
* Prefer minimal, focused changes
* Do not rewrite unrelated files
* Do not change anything unrelated to the requested task
* Keep UI, business logic, serial communication, and storage concerns separated
* Use environment variables or config files for application settings
* Never hardcode sensitive data
* Do not run destructive commands without confirmation
* Always explain changed files after implementation
* Always document important changes in `docs/`

---

## Application Architecture

Use a layered structure:

```text
desktop-app/
├── app/
│   ├── ui/                 # Desktop screens, dialogs, widgets
│   ├── services/           # Business logic
│   ├── serial_comm/        # UART/Serial communication
│   ├── models/             # Config models and validation schemas
│   ├── storage/            # Local file read/write logic
│   ├── utils/              # Shared helpers
│   └── main.py             # Application entry point
├── config/                 # Default app configuration
├── docs/                   # Documentation
├── tests/                  # Unit and integration tests
├── skills/                 # AI development skill guides
├── requirements.txt
├── .env.example
├── AGENTS.md
└── README.md
```

---

## Separation of Concerns

### UI Layer

The UI layer should only handle:

* User interactions
* Displaying data
* Triggering commands
* Showing errors and status messages

The UI must not directly contain:

* Serial protocol logic
* File parsing logic
* Business validation rules
* ECU command formatting

### Service Layer

The service layer should handle:

* ECU configuration workflow
* Validation coordination
* Calling serial communication layer
* Calling storage layer
* Transforming UI input into valid commands

### Serial Communication Layer

The serial layer should handle:

* Opening and closing COM ports
* Sending commands to ECU
* Reading realtime data from ECU
* Handling timeout and connection errors
* Encoding and decoding protocol packets
* CRC/checksum validation if required

### Storage Layer

The storage layer should handle:

* Saving configuration files
* Loading configuration files
* Exporting logs
* Managing local app data

---

## UART / Serial Communication Rules

### Serial Connection

* Do not hardcode COM port names
* Allow users to select available ports
* Allow users to configure baudrate
* Handle disconnected devices gracefully
* Show connection status clearly in the UI

Example settings:

```text
port: COM3
baudrate: 115200
timeout: 1s
parity: none
stop_bits: 1
data_bits: 8
```

### Realtime Data

Realtime data from ECU should be handled in a background worker or thread.

Do not block the UI thread.

Recommended flow:

```text
ECU → UART → Serial Reader Thread → Signal/Event → UI Update
```

### Sending Config

Recommended flow:

```text
User Input → Validate → Build Packet → Send UART → Wait ACK/NACK → Show Result
```

### Protocol Design

Use a clear packet format.

Example:

```text
[HEADER][LENGTH][COMMAND][PAYLOAD][CRC][END]
```

Example command types:

```text
0x01 = SET_CONFIG
0x02 = GET_CONFIG
0x03 = SAVE_CONFIG
0x04 = READ_STATUS
0x05 = REBOOT_ECU
```

The application should handle:

* ACK response
* NACK response
* Timeout
* Invalid packet
* CRC mismatch
* Device disconnected

---

## Code Quality Standards

* Use clear and descriptive naming
* Keep functions small and focused
* Validate input at application boundaries
* Handle errors explicitly with meaningful messages
* Avoid duplicated business logic
* Keep serial protocol logic reusable and testable
* Add tests for important business rules
* Write readable, self-documenting code

---

## Security Requirements

* Never expose secrets in UI code
* Never log passwords, tokens, private keys, or sensitive ECU data
* Validate all imported files
* Validate file type, size, and content before loading
* Sanitize and validate all user input
* Do not allow arbitrary file writes outside approved folders
* Follow the principle of least privilege

---

## Local File Storage Rules

The application may store:

* ECU configuration files
* User preferences
* Connection profiles
* Diagnostic logs
* Exported reports

Recommended formats:

```text
.json   for configuration
.yaml   for readable configuration
.log    for application logs
.csv    for exported realtime data
```

Rules:

* Validate config files before applying them
* Use versioned config schemas
* Keep backups before overwriting important files
* Show clear errors for invalid or outdated config files

---

## Error Handling

Always handle these cases:

* ECU not connected
* Invalid COM port
* Serial timeout
* Invalid user input
* Invalid config file
* ECU returns NACK
* CRC/checksum mismatch
* Permission denied when writing files
* Unexpected application error

Error messages should be meaningful and user-friendly.

Example:

```text
Cannot connect to ECU on COM3. Please check the cable, port, and baudrate.
```

---

## Logging Rules

Use structured logging for:

* App startup and shutdown
* Serial connection open/close
* Commands sent to ECU
* ACK/NACK responses
* Errors and exceptions
* Config import/export actions

Do not log:

* Passwords
* Tokens
* Private data
* Sensitive ECU security keys

---

## Testing Guidelines

Add tests for:

* Config validation
* Packet encoding and decoding
* CRC/checksum calculation
* Serial protocol parsing
* Storage read/write logic
* Error handling behavior

Use mocks for serial communication.

Example:

```text
tests/
├── test_config_validation.py
├── test_packet_codec.py
├── test_serial_service.py
├── test_storage_service.py
└── test_error_handling.py
```

---

## Packaging and Deployment

Use a packaging tool such as:

```text
PyInstaller
```

Recommended output:

```text
dist/
└── ecu-config-app.exe
```

Packaging rules:

* Do not include `.env` files
* Do not include test files in release builds
* Include required assets only
* Include default config templates
* Test the packaged app on a clean machine

---

## Documentation Requirements

Update `docs/` when changing:

* Serial protocol
* Config schema
* UI workflow
* Packaging steps
* Error handling behavior
* File storage structure

Recommended docs:

```text
docs/
├── architecture.md
├── serial-protocol.md
├── config-schema.md
├── user-guide.md
├── packaging.md
└── changelog.md
```

---

## Output Format

After completing any task, provide:

1. **What was changed**
   Brief description of modifications

2. **Files changed**
   List of modified files

3. **How to run and test**
   Commands and test procedures

4. **Risks or notes**
   Any potential issues or important notes

---

## Review Checklist

Before committing code:

* [ ] Code follows existing patterns and style
* [ ] UI, service, serial, and storage layers are separated
* [ ] Serial communication does not block the UI thread
* [ ] Input is validated appropriately
* [ ] Errors are handled gracefully
* [ ] Tests are added or updated
* [ ] No hardcoded COM ports
* [ ] No hardcoded secrets
* [ ] Logs do not expose sensitive data
* [ ] Documentation is updated
* [ ] Packaged app is tested locally

---

## How to Apply These Skills

When working on ECU Config App features:

1. **Identify the domain**
   UI, serial communication, ECU protocol, storage, security, testing, deployment, or documentation

2. **Refer to the relevant skill**
   Check the matching skill guide before implementation

3. **Follow the rules**
   Apply the project rules and best practices

4. **Document changes**
   Update `docs/` when behavior or architecture changes

5. **Test thoroughly**
   Add or update tests for important logic

---

## Quick Reference Checklist

Before committing code:

* [ ] Code follows the style and patterns of existing code
* [ ] Serial communication is isolated from UI
* [ ] Realtime reading uses background thread or worker
* [ ] UI remains responsive
* [ ] Config input is validated
* [ ] ECU responses are handled properly
* [ ] Timeout and disconnected device cases are handled
* [ ] Local files are validated before loading
* [ ] No hardcoded secrets or COM ports
* [ ] Tests are added or updated
* [ ] Documentation is updated

---

**Last Updated:** June 26, 2026
**Project:** ECU Config Desktop App
**Version:** 1.0
