# BUG-T03 — Sensor failure creates a heat request

**OPEN · Severity High · Priority High**. RISK-T01/T05. Environment: identified main ESP32 image and separate Wokwi sensor/campaign variants; defaults 20/25 C. [Build](../evidence/support/tested-build.json).

## Steps to Reproduce

1. Stop Wokwi; run `python scripts/select_fixture.py fault`.
2. Reopen/start root `wokwi.toml`, connect Serial, then restart.
3. Observe the read error, displayed value and output request. Stop and restore with `python scripts/select_fixture.py normal`.

**Expected:** identify invalid sensor data, distinguish it from valid 0 C, and create no new heat request under proposed RTH-07.

**Actual:** failed read becomes 0 C and requests HIGH. The [main log](../evidence/bugs/sensor-fault/live-serial.log) records reboot at host 24.407 s, error and Relay Activated at 29.625 s. Earlier TFT false-zero observation accompanies the [preceding practice log](../evidence/support/previous-sensor-fault.log). Host times do not measure device latency.

Dynamic reproduction: start OFF at 25 C, disconnect data and observe a new heat request. All four ON/OFF × restored-low/high combinations ran; recovery controls passed, while both OFF-state fault cases failed. [Campaign](../evidence/runs/campaign/README.md). A subsequent held fault closed modeled COM-NO; [contact/reset evidence](../evidence/runs/inputs/README.md). Valid zero/negative controls pass.

## Cause, impact and disposition

`readTemperature()` replaces NaN with zero; `updateRelay()` treats it as a cold valid reading. Missing fault indication and unintended heat request share one root cause. Reproduced at startup and dynamically on identified images; no physical heater/overheating consequence was tested.

Suggested fix: preserve invalid state, display an error and apply an explicit fault/recovery policy. Retest startup/dynamic faults, both histories, valid zero/negative values, recovery and contacts. Fix is deliberately not applied to the defect-study baseline. **Release blocker: critical RISK-T01.**
