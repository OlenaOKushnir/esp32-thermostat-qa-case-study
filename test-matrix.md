# Test Matrix — Thermostat

All planned simulation tests have been executed. The matrix links each test to its risks, expected behavior, results, and supporting evidence. Three bugs remain open.

| ID | Priority | Risks / requirements | Level / test type | Steps and expected | Current status / evidence |
|---|---|---|---|---|---|
| TT-01 | P1 | T06/T07; RTH-01/09 | System; startup/regression | Connected sensor, restart. Defaults VIEW/20/25, valid 24 C, output initially LOW, no GPIO/IPC errors | PASS after configured output initialization: defaults, valid 24 C and GPIO5 LOW; cold pre-initialization levels are separately qualified. [live campaign](evidence/runs/campaign/README.md) |
| TT-02 | P0 | T02; RTH-02 | System; functional/boundary | From known state, set 19.9/20/20.1 and 24.9/25/25.1 C; below lower ON; >=upper OFF | PASS on sensor-observer variant for all six listed temperatures with recorded histories; [sensor evidence](evidence/runs/sensor/README.md) |
| TT-03 | P0 | T02; RTH-03 | System; state transition | Set 19→22→25→22 C. ON→ON→OFF→OFF | PASS: output follows both deadband histories. [sensor evidence](evidence/runs/sensor/README.md) |
| TT-04 | P1 | T02; RTH-02/03/12 | System; reliability/stress | Repeat crossings 20 cycles, include values inside deadband; count transitions and measure sim-time latency | PASS: 20 cycles, 80 states, 40 request edges / 20 rising; maximum response 1890 device ms. [live campaign](evidence/runs/campaign/README.md) |
| TT-05 | P1 | T03; RTH-04/05 | Interface/system; boundary/negative | Adjust each threshold ± counts; test -50/100, gap=0.5, clamp/reversal, VIEW rotation | PASS on GPIO-driven ESP32 variant: both directions, half steps, four boundaries, clamp/reversal, VIEW rotation. [live campaign](evidence/runs/campaign/README.md) |
| TT-06 | P1 | T04/T06; RTH-06/09/12 | Interface/system; debounce/negative/recovery | One press/hold/rapid press/bounce, rotate both directions; one expected action per valid input | FAIL T04 release bounce on input variant; campaign controls PASS for 30 deliberate presses, rapid train and encoder boundaries. [live campaign](evidence/runs/campaign/README.md) |
| TT-07 | P0 | T01/T05; RTH-07/08 | System; fault injection/safety-oriented | Use disconnected SDA fixture at startup; restart. Expect explicit fault, no new heat request; distinguish valid 0 C | FAIL: [capture](evidence/bugs/sensor-fault/live-serial.log) shows a sensor error followed by a heat request; false 0 C is documented in the bug report; [raw fault log](evidence/support/previous-sensor-fault.log), [BUG-T03](bug-reports/BUG-T03.md), [fixture](diagram.sensor-fault.json) |
| TT-08 | P0 | T01; RTH-11/12 | System; fault recovery | Disconnect while ON and OFF; reconnect at low/high temperature; check agreed safe recovery and delay | EXECUTED: all four ON/OFF × low/high restoration combinations and device-time budgets. Recovery PASS; OFF-state fault FAIL T03. [live campaign](evidence/runs/campaign/README.md) |
| TT-09 | P1 | T05; RTH-08 | System/UI; consistency | Compare TFT temperature/mode/thresholds with actual input and Serial; normal/edit/fault states | FAIL: T03 false-zero fault display; T05 completed matching mode frame after 1024 device ms on instrumented variant versus proposed 500 ms. Orientation fixed; [device input evidence](evidence/bugs/input-feedback/README.md) |
| TT-10 | P1 | T07; RTH-01 | System; reset/recovery | Restart while ON/OFF/SET LOWER/SET UPPER; verify defaults and safe boot. Persistence policy first clarified | PASS: warm reset from ON/OFF/SET LOWER/SET UPPER restores defaults and configured GPIO LOW. [live campaign](evidence/runs/campaign/README.md) |
| TT-11 | P0 | T08; RTH-10 | Interface/hardware; polarity/protocol | Capture GPIO5 and inspect relay COM/NO/NC for LOW/HIGH, boot, fault | PASS for settled simulated GPIO/contact polarity; boot/fault levels recorded. Pre-initialization GPIO and physical load safety are separate limitations. [live campaign](evidence/runs/campaign/README.md) |
| TT-12 | P1 | T01/T02/T06; RTH-07/09 | Host; recorded-evidence regression | Run offline Pytest checks against saved logs and build records | 54 passed/4 failed assertions about T03/T04/T05. [Offline report](evidence/support/offline.xml) |
| TT-13 | P1 | T03/T04/T05; RTH-04/05/06/08/12 | Component; boundary/negative | Clamp/gap, input and feedback controls; exact 199/200/201 ms decision boundary | 25 controls PASS; T04/T05 FAIL; three clock controls PASS. [Fresh results](evidence/components/current/README.md) |

T01–T08 are risk suffixes. Expected results are defined in [Acceptance Criteria](requirements.md).


## Priority and execution

P0 tests address critical fault/output behavior; P1 tests cover other control, UI and regression risks. Execution commands and new-run evidence procedure are in the [README](README.md). All planned simulation categories are executed; FAIL remains FAIL. [Short-pulse/fault-contact follow-up](evidence/runs/inputs/README.md) adds four passing controls.
