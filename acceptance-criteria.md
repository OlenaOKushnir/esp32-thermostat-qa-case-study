# Acceptance Criteria — Thermostat

Acceptance criteria for the ESP32 thermostat simulation.

**Basis:** D = expected behavior derived from the firmware; P = proposed criterion used for this case study. The scope is simulation.

| ID | Basis | Expected behavior | Current coverage |
|---|---|---|---|
| RTH-01 | D | After restart: VIEW, lower=20 C, upper=25 C, initial GPIO5 LOW. With a valid initial reading of 24 C, LOW is retained | PASS for configured-output initialization and complete four-state warm-reset matrix; pre-application power-on waveform is not certified. [live campaign](evidence/runs/campaign/README.md) |
| RTH-02 | D | With valid T < lower, output HIGH; with T >= upper, LOW. Check 19.9/20.0/20.1 and 24.9/25.0/25.1 at default thresholds with a controlled previous state | PASS for 19.9/20/20.1 and 24.9/25/25.1 C in identified sensor-observer Wokwi variant; ON/OFF histories recorded; [sensor evidence](evidence/runs/sensor/README.md) |
| RTH-03 | D | When lower <= T < upper, retain the previous output state; the same 22 C produces HIGH after 19 C and LOW after 25 C | PASS: both ON/OFF deadband histories; [sensor evidence](evidence/runs/sensor/README.md) |
| RTH-04 | D | SET LOWER: one logical encoder count changes lower by 0.5 C; -50 <= lower <= upper-0.5; rotation in VIEW does not change thresholds | PASS: live encoder direction/half-step, lower minimum/gap clamp/reversal and VIEW rotation. [live campaign](evidence/runs/campaign/README.md) |
| RTH-05 | D | SET UPPER: one logical count changes upper by 0.5 C; lower+0.5 <= upper <=100; the minimum gap is preserved | PASS: live upper maximum/gap clamp/reversal and 0.5 C steps. [live campaign](evidence/runs/campaign/README.md) |
| RTH-06 | D/P | D: button cycle VIEW→SET LOWER→SET UPPER→VIEW. P: one valid press produces one transition; hold/bounce produces no extra transitions; the deliberate case-study press is 350 ms LOW/350 ms release | FAIL: clean long-hold control PASS, release rebound advances twice on device-observer variant (T04); [device input evidence](evidence/bugs/input-feedback/README.md) |
| RTH-07 | P | Distinguish an invalid/absent reading from valid 0 C; a fault must not create a new heat request; show SENSOR ERROR or an equivalent indication | FAIL: BUG-T03; [capture](evidence/bugs/sensor-fault/live-serial.log) |
| RTH-08 | D/P | TFT shows the current valid temperature, mode and thresholds; P: text is readable in the normal orientation and an invalid reading is not disguised as 0 C | Stable normal/edit field consistency PASS at completed drawing-call level; invalid-sensor false zero FAIL T03; mode-delay FAIL T05. [live campaign](evidence/runs/campaign/README.md) |
| RTH-09 | P | Startup contains no GPIO/IPC/ISR installation errors; UI and temperature control operate after startup | PASS for captured startup and executed encoder/30-press/rapid-train controls. [live campaign](evidence/runs/campaign/README.md) |
| RTH-10 | P | HIGH/LOW heat-request semantics agree with relay transistor configuration and COM/NO/NC; initial/restart/fault contact behavior is checked separately | Settled simulated HIGH/LOW contact semantics PASS; early boot GPIO HIGH is recorded without a glitch-free power-on claim. Physical bench excluded. [live campaign](evidence/runs/campaign/README.md) |
| RTH-11 | P | After sensor data is restored, valid readings return and control follows the agreed recovery policy, without remaining latched on because of the previous fault | PASS for recovery in all four initial ON/OFF × restored low/high combinations and proposed 5 s recovery gate. [live campaign](evidence/runs/campaign/README.md) |
| RTH-12 | P | Temperature/fault response within 5 s of simulated time; button-to-mode feedback within 500 ms of simulated time | Temperature/fault/recovery 5 s gates executed; 20-cycle maximum 1890 device ms PASS. UI 500 ms gate remains FAIL T05 (1024 ms). [live campaign](evidence/runs/campaign/README.md) |

## Assessment assumptions

This educational assessment adopts: sensor faults must not create a new heat request; reset restores RAM defaults; setpoint source limits are -50/100 C with a 0.5 C gap; a deliberate input is 350 ms LOW followed by 350 ms release. Short 30 ms trains are negative filtering/state-integrity tests, not required one-action-per-pulse inputs. Temperature/fault/recovery use a proposed 5000 ms device-time budget and mode feedback uses 500 ms. Physical operating range and heater safety require separate hardware requirements.

## Acceptance gate

All mandatory criteria must pass before acceptance. T03/T04/T05 remain open, so the recommendation is NO-GO. See [Release Decision](release-decision.md).
