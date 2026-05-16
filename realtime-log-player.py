import os
import time
import sys
import re
from datetime import datetime

LOG_DIR = "sample_logs"

TIMESTAMP_PATTERNS = [

    (r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),

    (r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', '%Y-%m-%dT%H:%M:%S'),
]

def extract_timestamp(line: str) -> datetime | None:
    for pattern, fmt in TIMESTAMP_PATTERNS:
        match = re.match(pattern, line)
        if match:
            try:
                ts = datetime.strptime(match.group(1), fmt)
            
                if ts.year == 1900:
                    ts = ts.replace(year=datetime.now().year)
                return ts
            except ValueError:
                continue
    return None

def list_logs() -> list[tuple[str, str]]:
    logs = []
    for os_type in os.listdir(LOG_DIR):
        os_path = os.path.join(LOG_DIR, os_type)
        if os.path.isdir(os_path):
            for filename in os.listdir(os_path):
                if filename.endswith(".log"):
                    display = f"{os_type}/{filename.replace('.log', '')}"
                    filepath = os.path.join(os_path, filename)
                    logs.append((display, filepath))
    return sorted(logs)

def select_log(logs: list[tuple[str, str]]) -> str:
    print("\n=== LOG STORE ===")
    for i, (display, _) in enumerate(logs, 1):
        print(f"  [{i}] {display}")
    print()

    while True:
        try:
            choice = int(input("Select log to replay: "))
            if 1 <= choice <= len(logs):
                return logs[choice - 1][1]
            print(f"Enter a number between 1 and {len(logs)}")
        except ValueError:
            print("Enter a valid number")

def stream_log(filepath: str, speed_multiplier: float = 1.0):
    """
    Stream log file using actual timestamps to determine delay between lines.
    speed_multiplier: 1.0 = real time, 2.0 = 2x faster, 0.5 = half speed
    """
    print(f"\n=== STREAMING: {filepath} ===")
    print(f"Speed: {speed_multiplier}x real time | Ctrl+C to stop\n")
    time.sleep(1)

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()

        if not lines:
            print("Log file is empty.")
            return

        
        timestamps = [extract_timestamp(line) for line in lines]
        total = len(lines)

        try:
            for i, (line, ts) in enumerate(zip(lines, timestamps)):
                print(line, end="", flush=True)

                
                if i < total - 1:
                    next_ts = timestamps[i + 1]
                    if ts and next_ts:
                        delta = (next_ts - ts).total_seconds()
                        
                        delta = max(0, min(delta, 5.0))
                        time.sleep(delta / speed_multiplier)
                    else:
                        
                        time.sleep(0)

            print(f"\n\n=== STREAM COMPLETE ({total} lines) ===")

        except KeyboardInterrupt:
            print("\n\n=== STREAM INTERRUPTED ===")

    except FileNotFoundError:
        print(f"File not found: {filepath}")

if __name__ == "__main__":
    if not os.path.exists(LOG_DIR):
        print(f"No log store found at '{LOG_DIR}'. Generate some logs first.")
        sys.exit(1)

    logs = list_logs()
    if not logs:
        print("No .log files found. Run the attack generator first.")
        sys.exit(1)

    
    speed = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0

    filepath = select_log(logs)
    stream_log(filepath, speed_multiplier=speed)