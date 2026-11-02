# Risk Matrix — Thermostat

Impact and probability use a 1–3 scale; score = impact × probability. Scores 7–9 are critical, 4–6 high, and 1–3 normal. Scores guide test priority; defect severity is separate.

| Risk ID | Quality risk / consequence | I | P | Score / priority | Requirements | Tests / mitigation | Current disposition |
|---|---|---|---|---|---|---|---|
| RISK-T01 | Sensor fault is interpreted as a cold room and requests heating | 3 | 3 | 9 critical | RTH-07/11/12 | TT-07/08; SDA disconnect + recovery, Serial/TFT/output evidence | OPEN, BUG-T03; [capture](evidence/bugs/sensor-fault/live-serial.log) |
| RISK-T02 | Incorrect hysteresis causes chatter or unnecessary heating | 3 | 2 | 6 high | RTH-02/03/12 | TT-02/03/04; boundary/state history + repeated crossings | PASS in simulated 20-cycle/80-state campaign with transition counts and device timing. [live campaign](evidence/runs/campaign/README.md) |
| RISK-T03 | Thresholds or the gap become invalid after encoder adjustment | 3 | 2 | 6 high | RTH-04/05 | TT-05/13; lower/upper min/max, reversal, VIEW rotation | PASS for full GPIO encoder boundary, clamp/reversal and VIEW controls. [live campaign](evidence/runs/campaign/README.md) |
| RISK-T04 | Missed/double button events or encoder counts alter settings | 2 | 2 | 4 high | RTH-06/12 | TT-06; bounce/hold/rapid inputs, logical count accounting | OPEN T04: reproduced on input-observer Wokwi variant; clean-hold control PASS |
| RISK-T05 | Display shows an incorrect mode/value or conceals a fault | 2 | 3 | 6 high | RTH-07/08 | TT-07/09; compare input/Serial/TFT | OPEN T03/T05: dynamic false-zero fault and 1024 ms completed-frame feedback on identified Wokwi variants |
| RISK-T06 | Startup ISR errors disrupt control | 3 | 2 | 6 high | RTH-01/09 | TT-01/06; deferred initialization, boot capture, input regression | PASS: startup, encoder and repeated-input checks. [live campaign](evidence/runs/campaign/README.md) |
| RISK-T07 | Reset state/settings do not match expectations | 2 | 2 | 4 high | RTH-01; RAM defaults policy | TT-10; startup and warm resets from active/edit states | PASS: all four warm-reset states restore defaults. [live campaign](evidence/runs/campaign/README.md) |
| RISK-T08 | GPIO request and relay contacts have opposite semantics | 3 | 2 | 6 high | RTH-10 | TT-11; GPIO/contact traces, physical bench follow-up | Settled simulated contact polarity PASS; early boot HIGH and physical load behavior remain qualified. [live campaign](evidence/runs/campaign/README.md) |

## Impact × Probability

| Impact / Probability | 1 Low | 2 Medium | 3 High |
|---|---|---|---|
| 3 High | 3 normal | 6: T02/T03/T06/T08 | 9: T01 |
| 2 Medium | 2 normal | 4: T04/T07 | 6: T05 |
| 1 Low | 1 normal | 2 normal | 3 normal |

T01–T08 are risk suffixes, distinct from test IDs TT-xx. Critical RISK-T01 remains open: [sensor-fault evidence](evidence/bugs/sensor-fault/README.md).
