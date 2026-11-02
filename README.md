# Embedded QA Case Study - ESP32 Thermostat

An ESP32 thermostat tested in **Wokwi for VS Code**, with a DHT22 sensor, ILI9341 display, KY-040 encoder and relay. Defaults: VIEW, lower 20 C, upper 25 C. Testing was done in simulation; physical hardware was not tested.

**Status: NO-GO.** Three bugs remain: heating after sensor failure, release bounce and slow mode feedback. See the [conclusion](qa-conclusion.md) and [release decision](release-decision.md).

## Enable and run

1. Extract/open **thermostat-vscode** in VS Code—the folder containing `platformio.ini` and `wokwi.toml`.
2. Install/enable **PlatformIO IDE** and **Wokwi Simulator** from workspace recommendations. Wait for initialization.
3. Use **F1 → Wokwi: Request a new License** and complete activation with your Wokwi account. [Activation guide](https://docs.wokwi.com/vscode/getting-started).
4. Select root `wokwi.toml` with **F1 → Wokwi: Select Config File**, then **Wokwi: Start Simulator**. Firmware is included. No physical board or COM port is needed.
5. Wait for the thermostat screen and normal 24 C reading; inspect the Wokwi Terminal. Stop/close the simulator before changing fixtures.

After source edits, save, build successfully and reopen Wokwi. Simulation executes the selected binary, not the source file directly.

## Build

Use **PlatformIO → Project Tasks → esp32dev → General → Build**, or **Ctrl+Shift+B** for the included Windows task. **Terminal → Run Task → Thermostat: Build all images** builds all four images sequentially. Wait for SUCCESS.

PowerShell fallback from the project root:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -e esp32dev
```

The first build may download the pinned toolchain; library sources are included in `lib/`. If `pio` is unrecognized, use the full path or PlatformIO's terminal. Ctrl+Alt+B may have competing bindings. Custom installations should use PlatformIO Project Tasks.

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

Use Python 3.11+ from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt -r requirements-live.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/check_project.py
.\.venv\Scripts\python.exe scripts/verify_portfolio.py
```

| Check | Result / purpose |
|---|---|
| Default `pytest` | All offline checks: 54 passed / 4 known-bug assertions |
| Integrity scripts | Check wiring, source files, links, hashes and recorded reports |

`pytest` checks saved results in `tests/`; four assertions fail on the known bugs. Live Wokwi tests are in `validation/tests/`. After changing firmware behavior, record a new run.

For live Wokwi tests and component checks, see the [test guide](docs/validation.md).

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

## Project documents

[Master Test Plan](master-test-plan.md) · [Acceptance Criteria](acceptance-criteria.md) · [Risk Matrix](risk-matrix.md) · [Test Matrix](test-matrix.md) · [Evidence](evidence/README.md) · [Technical Decisions](docs/technical-decisions.md) · [Assignment Checklist](docs/submission-checklist.md).

Three reports: [T03 sensor fault](bug-reports/BUG-T03.md), [T04 release bounce](bug-reports/BUG-T04.md), [T05 stale feedback](bug-reports/BUG-T05.md).

Source attribution, dependencies and build details are documented in [Source and attribution](docs/source-and-changes.md).

