"""Decode Wokwi's 1 ns UART_TX trace at 115200 baud, 8N1 (application output after 1 s)."""
from bisect import bisect_right
from pathlib import Path
import sys


def decode(path):
    lines = Path(path).read_text().splitlines()
    assert '$timescale 1ns $end' in lines
    signals = {line.split()[4]: line.split()[3] for line in lines if line.startswith('$var ')}
    edges = {name: [] for name in ['UART_TX', 'HEAT_REQUEST']}
    timestamp = 0
    for line in lines:
        if line.startswith('#'):
            timestamp = int(line[1:])
        for name, values in edges.items():
            if line in ['0' + signals[name], '1' + signals[name]]:
                values.append((timestamp, int(line[0])))
    uart = edges['UART_TX']
    times = [time for time, value in uart]
    bit = 1e9 / 115200
    end = 0
    text = bytearray()
    started = None
    output = ['UART_TX: 115200 baud, 8N1; seconds from simulation start; boot before 1 s excluded.']
    for time, value in uart:
        if value or time < 1e9 or time < end:
            continue
        sample = lambda offset: uart[bisect_right(times, time + offset * bit) - 1][1]
        assert sample(9.5) == 1, f'Invalid stop bit at {time} ns'
        byte = sum(sample(1.5 + i) << i for i in range(8))
        end = time + 9.8 * bit
        if started is None:
            started = time
        text.append(byte)
        if byte == 10:
            output.append(f'{started / 1e9:.9f}  {text.decode("ascii").rstrip()}')
            text.clear()
            started = None
    assert not text, 'Incomplete final line'
    output.append('\nHEAT_REQUEST (GPIO5):')
    output.extend(f'{time / 1e9:.9f}  {value}' for time, value in edges['HEAT_REQUEST'])
    return '\n'.join(output) + '\n'


if __name__ == '__main__':
    print(decode(sys.argv[1]), end='')
