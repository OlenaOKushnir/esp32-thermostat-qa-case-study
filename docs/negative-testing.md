# Negative Testing

| Condition | Oracle | Result / evidence |
|---|---|---|
| Sensor absent at startup | Explicit invalid state; no new heat request | FAIL T03; [main capture](../evidence/bugs/sensor-fault/live-serial.log) |
| Sensor lost while OFF/ON | No new heat request; recover with valid low/high data | OFF-state fault FAIL; four recovery controls PASS; [campaign](../evidence/runs/campaign/README.md) |
| Valid zero / negative temperature | Remain valid; heat below lower | PASS; [sensor](../evidence/runs/sensor/README.md), [campaign](../evidence/runs/campaign/README.md) |
| Below -50 / above 100 / crossing thresholds | Clamp, preserve gap, reverse correctly | PASS with GPIO encoder; [campaign](../evidence/runs/campaign/README.md) |
| Rotation in VIEW | Leave thresholds unchanged | PASS; [campaign](../evidence/runs/campaign/README.md) |
| Long hold / release rebound | One transition per intended press | Clean hold PASS; rebound FAIL T04; [input run](../evidence/bugs/input-feedback/README.md) |
| Thirty deliberate presses / rapid short pulses | Correct mode cycle; bounded state | PASS; [campaign](../evidence/runs/campaign/README.md) |
| Requested 199/200/201 ms pulse periods | At most one mode event per injected LOW; preserve settings | PASS; [actual intervals](../evidence/runs/inputs/README.md) |
| Exact decision spacing 199/200/201 ms | Reject at <=200; accept at 201 | Three component checks PASS; [results](../evidence/components/current/debounce.json) |
| Accepted input after refresh | Complete matching frame within proposed 500 ms | FAIL T05: 1024 device ms; [input run](../evidence/bugs/input-feedback/README.md) |
| Reset from ON/OFF/edit/fault | Restore VIEW/20/25 and configured LOW | PASS; [campaign](../evidence/runs/campaign/README.md), [fault/reset](../evidence/runs/inputs/README.md) |

Component hardware/time doubles do not measure ESP32 scheduling or TFT pixels. Live tests drive GPIO and capture fresh data on separate identified images. Fault stimulus does not assign product mode, thresholds or relay state.

A deliberate press is 350 ms LOW/350 ms release. Short 30 ms pulses are filtering/state-integrity checks, without a one-action-per-short-pulse promise. MODE logs follow Serial output and cannot resolve exact decision spacing; the component clock test checks that boundary.
