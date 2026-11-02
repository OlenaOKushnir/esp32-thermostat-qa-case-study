# UART Sensor-Fault Trace

Captured from the supplied main firmware in Wokwi with the sensor data disconnected. No test firmware was used.

- [Raw VCD](sensor-fault.vcd): UART TX (GPIO1), heat request (GPIO5) and DHT data (GPIO16), 1 ns timescale.
- [Decoded output](decoded.txt): 115200 baud, 8 data bits, no parity, 1 stop bit. Boot output before 1 s is excluded from decoding; the raw trace is retained.
- [Circuit](diagram.json) and [configuration](wokwi.toml.txt).
- Main firmware SHA-256: `3e6e3fcb15a8b95049e4e3f40c73f3205d283fb64e4b417b16617cfbfcb43411`. [Build identity](../../support/tested-build.json).

## Finding

After GPIO5 is configured LOW at 0.512426521 s, it rises at 3.581639333 s following the first failed sensor read. UART reports `Failed to read from DHT sensor!` followed by `Relay Activated.` This corroborates [BUG-T03](../../../bug-reports/BUG-T03.md).

The trace also starts with GPIO5 HIGH before application setup. This is a simulator observation, not a physical power-on safety measurement. DHT22 uses single-wire data; this project has no I2C interface to capture.

## Repeat

Stop Wokwi. Back up root `diagram.json` and `wokwi.toml`. Copy this circuit to root `diagram.json` and the saved configuration to root `wokwi.toml`; change `vcdFile` to a new path to preserve this run. Start the root simulator, wait for the sensor error and heat request, then stop to save the VCD. Restore both original root files.

From the project root, run `python automation/decode_uart.py evidence/runs/uart/sensor-fault.vcd` to reproduce the decoded output. The decoder prints GPIO5 changes separately and checks UART stop bits.
