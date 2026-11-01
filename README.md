# Embedded QA Case Study — ESP32 Thermostat

Risk-based QA of an ESP32/DHT22 thermostat with an ILI9341 display, KY-040 encoder and relay in **Wokwi for VS Code**. Defaults: VIEW, lower 20 C, upper 25 C. This is a simulated real-device design; no physical board or heater was tested.

**Release: NO-GO.** Three open bugs concern sensor-fault heating, release bounce and delayed mode feedback. The live campaign has **25 cases: 23 passed, 2 T03 failures, no errors or skips**. Separate live input tests reproduce T04/T05. [Conclusion](qa-conclusion.md) · [Release Decision](release-decision.md).

## Enable and run

1. Extract/open **thermostat-vscode** in VS Code—the folder containing `platformio.ini` and `wokwi.toml`.
2. Install/enable **PlatformIO IDE** and **Wokwi Simulator** from workspace recommendations. Wait for initialization.
3. Use **F1 → Wokwi: Request a new License** and complete activation with your Wokwi account. [Activation guide](https://docs.wokwi.com/vscode/getting-started).
4. Select root `wokwi.toml` with **F1 → Wokwi: Select Config File**, then **Wokwi: Start Simulator**. Identified firmware is included; no board upload/COM port is needed.
5. Wait for the thermostat screen and normal 24 C reading; inspect the Wokwi Terminal. Stop/close the simulator before changing fixtures.

After source edits, save, build successfully and reopen Wokwi. Simulation executes the selected binary, not the source file directly.

## Build

Use **PlatformIO → Project Tasks → esp32dev → General → Build**, or **Ctrl+Shift+B** for the included Windows task. **Terminal → Run Task → Thermostat: Build all images** builds all four images sequentially. Wait for SUCCESS.

PowerShell fallback from the project root:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e esp32dev
```

The first build may download the pinned toolchain; application libraries are vendored. If `pio` is unrecognized, use the full path or PlatformIO's terminal. Ctrl+Alt+B may have competing bindings. Custom installations should use PlatformIO Project Tasks.

## Controls and smoke test

| Input | Expected behavior |
|---|---|
| Click DHT22 | Change simulated temperature |
| Push encoder | VIEW → SET LOWER → SET UPPER → VIEW |
| Rotate in edit mode | Change selected threshold by 0.5 C per logical count |
| Rotate in VIEW | Leave thresholds unchanged |
| T < lower | Request HIGH |
| T >= upper | Request LOW |
| lower <= T < upper | Retain preceding output |

Set **19 → 22 → 25 → 22 C**, waiting for each reading. Expected: **ON → ON → OFF → OFF**. Serial logs output changes only. Reproduce T03 by stopping Wokwi and running `python scripts/select_fixture.py fault`, then reopening/restarting the simulator. Expected: explicit sensor error without a new heat request. Actual: failed read, false 0 C and heating request. After stopping, restore with `python scripts/select_fixture.py normal` and reopen. [BUG-T03](bug-reports/BUG-T03.md).

## Python checks

Use Python 3.11+ with one consistent interpreter:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt -r requirements-live.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/check_project.py
.\.venv\Scripts\python.exe scripts/verify_portfolio.py
```

| Check | Result / purpose |
|---|---|
| Default `pytest` | 17 passed / 3 ordinary T03/T04/T05 acceptance failures |
| `pytest tests component_checks sensor_checks` | 54 passed / 4 failures; T03 has startup and dynamic assertions |
| Integrity scripts | Exit 0: wiring, source correspondence, links, hashes and report consistency |

Offline tests evaluate saved evidence. They do not control Wokwi or validate a later fix. Preserve failed captures and record fresh evidence after behavior changes.

## Live tests

Install both requirements, start the intended configuration and use a **new output directory** for each run. Keep the simulator tab visible and desktop available.

| Configuration / port | Command / procedure |
|---|---|
| Root / 4000 | `python scripts/capture_serial.py --output runs/new-main/serial.log --seconds 60`; restart after connection to capture boot |
| `validation/device/wokwi.toml` / 4001 | `python -m pytest live_tests -v -s --run-dir runs/new-input`; after LIVE CAPTURE CONNECTED, restart. Baseline: 1 passed/2 T04/T05 failures |
| `validation/sensor/wokwi.toml` / 4002 | Manual DHT/switch inputs with sample observer; [procedure](validation/sensor/README.md) |
| `validation/campaign/wokwi.toml` / 4003 | Wait for QA_READY and valid 24 C, then `python -m pytest campaign_tests -v -s --campaign-output runs/new-campaign --junitxml runs/new-campaign.xml` |

The campaign covers encoder limits, deliberate/rapid inputs, reset, 20 cycles, contacts, fault/recovery, display fields and short-pulse follow-up. Baseline: 23 passed/2 T03 failures. [Fixture and limits](validation/campaign/README.md). Stop/close validation and reselect root `wokwi.toml` for normal use.

Optional component execution requires a local TinyCC x64 installation:

```powershell
python scripts/run_component_checks.py --extended --tcc-root C:\Tools\tcc --output runs/new-components/results.json
python scripts/run_debounce_components.py --tcc-root C:\Tools\tcc --output runs/new-debounce/results.json
```

The 27-scenario run has 25 passing controls/two known findings; three exact 199/200/201 ms checks pass. Component clocks do not measure ESP32/TFT timing.

## Troubleshooting

| Symptom | Action |
|---|---|
| Wokwi command/license unavailable | Enable extension and complete activation |
| Missing firmware or old behavior | Open correct root, build, select intended configuration and reopen Wokwi |
| Blank TFT | Allow initialization; inspect boot/build output and wiring if persistent |
| Missing pytest/serial | Install both requirements with the interpreter running the command |
| Serial connection fails | Start selected simulator, check port and close competing capture clients |
| Fault remains after restoration | Stop/close Wokwi, restore normal fixture and start again |
| Hash changes after rebuilding | Record a new identity/run; do not relabel old captures |

## Deliverables and provenance

[Master Test Plan](master-test-plan.md) · [Acceptance Criteria](acceptance-criteria.md) · [Risk Matrix](risk-matrix.md) · [Test Matrix](test-matrix.md) · [Evidence](evidence/README.md) · [Technical Decisions](docs/technical-decisions.md) · [Assignment Checklist](docs/submission-checklist.md).

Three reports: [T03 sensor fault](bug-reports/BUG-T03.md), [T04 release bounce](bug-reports/BUG-T04.md), [T05 stale feedback](bug-reports/BUG-T05.md).

Working sources remove inactive code/comments. Exact captured sources remain in `evidence/sources/`; `source_identity.py` verifies the cleanup. All four cleaned builds have byte-identical loadable sections. Supplied baseline binaries/ELFs preserve captured identities. [Source and attribution](docs/source-and-changes.md).

Create/upload the GitHub repository yourself. Preserve hidden configuration and allowed firmware artifacts; omit caches and local `runs/`. The assignment's literal physical-device requirement needs hardware evidence beyond this simulation scope.
