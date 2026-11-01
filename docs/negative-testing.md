# Negative Testing

| Condition | Oracle | Result / evidence |
|---|---|---|
| Sensor absent at startup | Explicit invalid state; no new heat request | FAIL T03; [main capture](../evidence/live-2026-11-01/live-serial.log) |
| Sensor lost while OFF/ON | No new heat request; recover with valid low/high data | OFF-state fault FAIL; four recovery controls PASS; [campaign](../evidence/campaign-live-2026-11-01/README.md) |
| Valid zero / negative temperature | Remain valid; heat below lower | PASS; [sensor](../evidence/sensor-live-2026-11-01/README.md), [campaign](../evidence/campaign-live-2026-11-01/README.md) |
| Below -50 / above 100 / crossing thresholds | Clamp, preserve gap, reverse correctly | PASS with GPIO encoder; [campaign](../evidence/campaign-live-2026-11-01/README.md) |
| Rotation in VIEW | Leave thresholds unchanged | PASS; [campaign](../evidence/campaign-live-2026-11-01/README.md) |
| Long hold / release rebound | One transition per intended press | Clean hold PASS; rebound FAIL T04; [input run](../evidence/device-inputs-2026-11-01-run3/README.md) |
| Thirty deliberate presses / rapid short pulses | Correct mode cycle; bounded state | PASS; [campaign](../evidence/campaign-live-2026-11-01/README.md) |
| Requested 199/200/201 ms pulse periods | At most one mode event per injected LOW; preserve settings | PASS; [actual intervals](../evidence/campaign-debounce-2026-11-01/README.md) |
| Exact decision spacing 199/200/201 ms | Reject at <=200; accept at 201 | Three component checks PASS; [results](../evidence/component-current/debounce.json) |
| Accepted input after refresh | Complete matching frame within proposed 500 ms | FAIL T05: 1024 device ms; [input run](../evidence/device-inputs-2026-11-01-run3/README.md) |
| Reset from ON/OFF/edit/fault | Restore VIEW/20/25 and configured LOW | PASS; [campaign](../evidence/campaign-live-2026-11-01/README.md), [fault/reset](../evidence/campaign-debounce-2026-11-01/README.md) |

Component hardware/time doubles do not measure ESP32 scheduling or TFT pixels. Live tests drive GPIO and capture fresh data on separate identified images. Fault stimulus does not assign product mode, thresholds or relay state.

A deliberate press is 350 ms LOW/350 ms release. Short 30 ms pulses are filtering/state-integrity checks, without a one-action-per-short-pulse promise. MODE logs follow Serial output and cannot resolve exact decision spacing; that oracle belongs to the component clock test.

New execution commands are in the [README](../README.md). Retain ordinary failures and original captures after fixes.
