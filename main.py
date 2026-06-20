import argparse
import sys
import os
from ui.app import UARTToolApp

def main():
    parser = argparse.ArgumentParser(description="UART Terminal Tool for ECU Communication")
    parser.add_argument("--port", type=str, default="/dev/ttyUSB0", help="Serial port (e.g., /dev/ttyUSB0)")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baudrate (e.g., 9600, 115200, 921600)")
    parser.add_argument("--no-mouse", action="store_false", dest="mouse", help="Disable TUI mouse tracking (restores native terminal selection)")
    parser.set_defaults(mouse=True)
    
    args = parser.parse_args()
    
    # Ensure formats and presets directories exist
    if not os.path.exists("formats"):
        os.makedirs("formats")
    if not os.path.exists("presets"):
        os.makedirs("presets")
    if not os.path.exists("logs"):
        os.makedirs("logs")

    app = UARTToolApp(port=args.port, baudrate=args.baudrate)
    app.run(mouse=args.mouse)

if __name__ == "__main__":
    main()
