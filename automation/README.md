# Automation and Test Runs

| Execution | Result | Evidence |
|---|---|---|
| Main-image absent sensor | T03 reproduced after reboot | [Raw capture](../evidence/bugs/sensor-fault/live-serial.log) |
| Device input/frame observer | Clean hold PASS; release bounce FAIL; feedback 1024 ms versus proposed 500 ms FAIL | [Run](../evidence/bugs/input-feedback/README.md) |
| DHT boundaries, zero and recovery | Boundaries/restored-data controls PASS; dynamic T03 FAIL | [Sensor](../evidence/runs/sensor/README.md), [recovery](../evidence/runs/recovery/README.md) |
| Full GPIO campaign | 19 passed/2 T03 failures; 20 cycles, 80 states, 40 edges; max response 1890 device ms | [Run](../evidence/runs/campaign/README.md) |
| Short pulses and fault/reset contacts | 4 passed; actual intervals retained | [Follow-up](../evidence/runs/inputs/README.md) |
| Exact debounce clock | 199/200 ms reject; 201 ms accepts | [Results](../evidence/components/current/README.md) |
| Cleaned sources | Four successful builds, identical loadable sections; 27 component values unchanged; three clock checks PASS | [Correspondence](../evidence/components/current/README.md) |

All planned simulation categories have executed results. T03/T04/T05 remain open. See the [evidence index](../evidence/README.md) for logs and supporting records.

## Offline checks

Run `python -m pytest -q` from the project root. It checks the recorded evidence: 54 passed, four assertions fail on the three known bugs. [Example](test_recorded_evidence.py): the sensor-fault assertion requires no heat request after a failed read. These checks replay saved results; they do not control Wokwi.

## Run live and component tests

Run the commands below from the project root.

Install both requirements, start the intended configuration and use a **new output directory** for each run. Keep the simulator tab visible and desktop available.

| Configuration / port | Command / procedure |
|---|---|
| Root / 4000 | `python scripts/capture_serial.py --output runs/new-main/serial.log --seconds 60`; restart after connection to capture boot |
| `validation/device/wokwi.toml` / 4001 | `python -m pytest validation/tests/live -v -s --run-dir runs/new-input`; after LIVE CAPTURE CONNECTED, restart. Baseline: 1 passed/2 T04/T05 failures |
| `validation/sensor/wokwi.toml` / 4002 | Manual DHT/switch inputs with sample observer; [procedure](../validation/sensor/README.md) |
| `validation/campaign/wokwi.toml` / 4003 | Wait for QA_READY and valid 24 C, then `python -m pytest validation/tests/campaign -v -s --campaign-output runs/new-campaign --junitxml runs/new-campaign.xml` |

The campaign covers encoder limits, deliberate/rapid inputs, reset, 20 cycles, contacts, fault/recovery, display fields and short-pulse follow-up. Baseline: 23 passed/2 T03 failures. [Fixture and limits](../validation/campaign/README.md). Stop/close validation and reselect root `wokwi.toml` for normal use.

Optional component execution requires a local TinyCC x64 installation:

```powershell
python scripts/run_component_checks.py --extended --tcc-root C:\Tools\tcc --output runs/new-components/results.json
python scripts/run_debounce_components.py --tcc-root C:\Tools\tcc --output runs/new-debounce/results.json
```

The 27-scenario run has 25 passing controls/two known findings; three exact 199/200/201 ms checks pass. Component clocks do not measure ESP32/TFT timing.


## UART trace

[Captured waveform and procedure](../evidence/runs/uart/README.md). Decode the application UART and GPIO5 edges with:

```powershell
python automation/decode_uart.py evidence/runs/uart/sensor-fault.vcd
```
