# Main-image sensor fault — 2026-11-01

TT-07; RISK-T01/T05; RTH-07/08; BUG-T03. [Build identity](../../support/tested-build.json). The disconnected-data fixture retains the MCU-side 3V3 pull-up; defaults are 20/25 C with output initially false. This is a communication fault, not an injected zero reading.

Start the fault fixture, connect RFC2217 localhost:4000 at 115200 baud, restart and capture. Restore the normal diagram and stop afterward.

Expected: explicit invalid state and no new heat request. Actual: [raw Serial](live-serial.log) contains reboot at host 24.407 s, sensor error followed by Relay Activated at 29.625 s, then repeated errors. **FAIL T03.** Earlier TFT false-zero observation is documented in the bug report; this log confirms the heat request, not pixels or physical heater energy.

Host receipt timestamps do not measure device latency. [Offline JUnit](pytest-current.xml) evaluates the retained capture: 17 passed/3 T03/T04/T05 failures. Separate [device input](../input-feedback/README.md) and [campaign](../../runs/campaign/README.md) runs provide their own identified evidence.
