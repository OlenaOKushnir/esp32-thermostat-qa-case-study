"""Capture Wokwi Serial RX to a new file; never overwrite existing evidence."""
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=60)
    parser.add_argument('--port', default='rfc2217://localhost:4000')
    args = parser.parse_args()
    if not 0 < args.seconds <= 3600:
        parser.error('--seconds must be greater than zero and at most 3600')
    if args.output.exists():
        parser.error('Output exists; choose a new run/file name.')
    try:
        import serial
    except ImportError:
        parser.error('Install live capture dependencies: python -m pip install -r requirements-live.txt')
    try:
        connection = serial.serial_for_url(args.port, baudrate=115200, timeout=.2)
    except serial.SerialException as error:
        parser.error(f'Cannot connect. Start Wokwi and check port 4000: {error}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    received = 0
    started = time.monotonic()
    status = 'completed'
    try:
        with args.output.open('x', encoding='utf-8') as output:
            output.write('# ' + json.dumps({'started_utc': datetime.now(timezone.utc).isoformat(),
                'port': args.port, 'baud': 115200, 'time_basis': 'host elapsed RX seconds'}) + '\n')
            output.flush()
            print('Connected. Restart Wokwi now to capture the complete boot. Ctrl+C stops capture.', flush=True)
            try:
                while time.monotonic() - started < args.seconds:
                    packet = connection.readline()
                    if packet:
                        received += len(packet)
                        line = f'{time.monotonic()-started:.3f} RX ' + packet.decode(errors='replace').rstrip('\r\n')
                        output.write(line + '\n')
                        output.flush()
                        print(line, flush=True)
            except KeyboardInterrupt:
                status = 'interrupted by operator'
            except serial.SerialException as error:
                status = f'connection lost: {error}'
            output.write(f'# capture_end: {status}; received_bytes={received}\n')
    finally:
        connection.close()
    print(f'Saved {args.output}; {status}; RX bytes={received}. Capture is not a test verdict.')
    if status.startswith('connection lost') or received == 0:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
