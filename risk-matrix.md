# Risk Matrix — Thermostat

Version 1.1, 2026-11-01. Impact/Probability: 1 low, 2 medium, 3 high; score=I×P. 7–9 critical priority; 4–6 high; 1–3 normal. These are expert prioritization estimates, not statistical probabilities. Defect severity is assigned separately.

| Risk ID | Quality risk / consequence | I | P | Score / priority | Requirements | Tests / mitigation | Current disposition |
|---|---|---|---|---|---|---|---|
| RISK-T01 | Sensor fault is interpreted as a cold room and requests heating | 3 | 3 | 9 critical | RTH-07/11/12 | TT-07/08; SDA disconnect + recovery, Serial/TFT/output evidence | OPEN, BUG-T03 live-reconfirmed November 1; [capture](evidence/live-2026-11-01/live-serial.log) |
| RISK-T02 | Incorrect hysteresis causes chatter or unnecessary heating | 3 | 2 | 6 high | RTH-02/03/12 | TT-02/03/04; boundary/state history + repeated crossings | PASS in simulated 20-cycle/80-state campaign with transition counts and device timing. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RISK-T03 | Thresholds or the gap become invalid after encoder adjustment | 3 | 2 | 6 high | RTH-04/05 | TT-05/13; lower/upper min/max, reversal, VIEW rotation | PASS for full GPIO encoder boundary, clamp/reversal and VIEW controls. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RISK-T04 | Missed/double button events or encoder counts alter settings | 2 | 2 | 4 high | RTH-06/12 | TT-06; bounce/hold/rapid inputs, logical count accounting | OPEN T04: reproduced on input-observer Wokwi variant; clean-hold control PASS |
| RISK-T05 | Display shows an incorrect mode/value or conceals a fault | 2 | 3 | 6 high | RTH-07/08 | TT-07/09; compare input/Serial/TFT | OPEN T03/T05: dynamic false-zero fault and 1024 ms completed-frame feedback on identified Wokwi variants |
| RISK-T06 | Startup ISR errors disrupt control | 3 | 2 | 6 high | RTH-01/09 | TT-01/06; deferred initialization, boot capture, input regression | Startup and encoder/30-press/rapid-train controls executed; T01 fixed history retained. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RISK-T07 | Reset state/settings do not match expectations | 2 | 2 | 4 high | RTH-01; RAM defaults policy | TT-10; startup and warm resets from active/edit states | PASS for all four warm-reset states; defaults policy, no persistence defect claimed. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RISK-T08 | GPIO request and relay contacts have opposite semantics | 3 | 2 | 6 high | RTH-10 | TT-11; GPIO/contact traces, physical bench follow-up | Settled simulated contact polarity PASS; early boot HIGH and physical load behavior remain qualified. [live campaign](evidence/campaign-live-2026-11-01/README.md) |

## Impact × Probability

| Impact / Probability | 1 Low | 2 Medium | 3 High |
|---|---|---|---|
| 3 High | 3 normal | 6: T02/T03/T06/T08 | 9: T01 |
| 2 Medium | 2 normal | 4: T04/T07 | 6: T05 |
| 1 Low | 1 normal | 2 normal | 3 normal |

T01–T08 in this table identify quality-risk ID suffixes, not test IDs TT-xx. Critical RISK-T01 is traced to fault/recovery test types and the [raw sensor-failure log](evidence/sensor-failure-runtime.log). The product defect has not been fixed. Only an assigned reviewer/owner can accept residual risk; no such acceptance is currently recorded.

Update 2026-10-30: RISK-T04 and RISK-T05 now have component evidence for BUG-T04/T05; see [negative testing](docs/negative-testing.md). Priority scores remain planning estimates and do not imply measured physical failure probability.

Current disposition: sensor faults remain unacceptable; restoring valid data recovered control in the observed high/low cases. Device input/timing findings are confirmed on separate instrumented variants. Stress/reset/contact simulation work is executed in the complete campaign.

## Completed simulation campaign — 2026-11-01

The [live campaign](evidence/campaign-live-2026-11-01/README.md) closes the planned simulation execution gaps: encoder/setpoints, input repetitions, four-state warm reset, 20 control cycles, settled contact polarity, complete fault/recovery timing and stable display-call fields. Result: 19 passed/2 T03 failures; no errors or skips. Open product defects T03/T04/T05 still prevent acceptance. Production fixes/retests and physical-bench validation are separate work, not unexecuted checks in this captured simulation campaign.

[Debounce-boundary/fault-contact follow-up](evidence/campaign-debounce-2026-11-01/README.md): 4 passed; requested 199/200/201 ms short-pulse trains and settled fault/reset contacts executed. Combined live campaign: 25 cases, 23 passed/2 T03 failures, no errors or skips.
