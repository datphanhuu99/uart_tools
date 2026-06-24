# UART Terminal Tool for ECU

A Python-based terminal tool for ECU communication, featuring a modern Textual TUI, YAML-based protocol definition, and dynamic command generation.

## Features

- **Terminal UI**: Real-time TX/RX display with timestamped logs.
- **Protocol Frame**: Implements `0x00 | COBS(CMD | LEN_BE | PAYLOAD | CRC16_BE) | 0x00`.
- **YAML Definitions**: Define commands (TX) and messages (RX) in simple YAML files.
- **Dynamic Forms**: Automatically generates a configuration UI for sending commands based on YAML definitions.
- **Value Mapping**: Translates raw numeric values to human-readable labels (enums and error codes).
- **Presets**: Save and load command configurations.
- **Logging**: Automatically saves all communication to `logs/`.

## Installation

1. Clone this repository.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Ensure your virtual environment is activated, then run:

```bash
python main.py --port /dev/ttyUSB0 --baudrate 115200
```

### Key Bindings

- **F1**: Switch to Terminal Screen.
- **F2**: Switch to Config Screen.
- **Q**: Quit the application.

## Configuration

### Commands (TX)
Edit `formats/commands.yaml` to define your ECU commands.

### RX Messages
Edit `formats/rx_messages.yaml` to define how incoming frames should be parsed.
When a `msg_id` has multiple payload layouts, add multiple entries with the same `msg_id` and distinguish them using `payload_len`.

### Maps
Edit `formats/maps.yaml` for shared lookup tables (e.g., error codes).

## Directory Structure

- `uart/`: Serial communication and frame protocol logic.
- `protocol/`: YAML loading, packing, and parsing.
- `ui/`: Textual application and screens.
- `formats/`: Protocol definition files.
- `presets/`: Saved command configurations.
- `logs/`: Communication logs.
