# Acceptance Criteria — Thermostat

Version 1.1, 2026-11-01. System: ESP32/DHT22/ILI9341/KY-040/relay in Wokwi. This is a QA baseline for an educational case study, not an approved industrial safety specification.

**Basis:** D = derived from current source behavior; P = proposed engineering acceptance criterion. D describes the expected function but does not establish its suitability for a future physical product. P states an explicit assessment assumption; external product approval is not claimed. Coverage statuses below reflect only checks actually performed.

| ID | Basis | Criterion / oracle | Current coverage |
|---|---|---|---|
| RTH-01 | D | After restart: VIEW, lower=20 C, upper=25 C, initial GPIO5 LOW. With a valid initial reading of 24 C, LOW is retained | PASS for configured-output initialization and complete four-state warm-reset matrix; pre-application power-on waveform is not certified. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RTH-02 | D | With valid T < lower, output HIGH; with T >= upper, LOW. Check 19.9/20.0/20.1 and 24.9/25.0/25.1 at default thresholds with a controlled previous state | PASS for 19.9/20/20.1 and 24.9/25/25.1 C in identified sensor-observer Wokwi variant; ON/OFF histories recorded; [sensor evidence](evidence/sensor-live-2026-11-01/README.md) |
| RTH-03 | D | When lower <= T < upper, retain the previous output state; the same 22 C produces HIGH after 19 C and LOW after 25 C | PASS for ON/OFF deadband histories in the sensor-observer variant; historical 19/22/25/22 smoke retained; [sensor evidence](evidence/sensor-live-2026-11-01/README.md) |
| RTH-04 | D | SET LOWER: one logical encoder count changes lower by 0.5 C; -50 <= lower <= upper-0.5; rotation in VIEW does not change thresholds | PASS: live encoder direction/half-step, lower minimum/gap clamp/reversal and VIEW rotation. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RTH-05 | D | SET UPPER: one logical count changes upper by 0.5 C; lower+0.5 <= upper <=100; the minimum gap is preserved | PASS: live upper maximum/gap clamp/reversal and 0.5 C steps. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RTH-06 | D/P | D: button cycle VIEW→SET LOWER→SET UPPER→VIEW. P: one valid press produces one transition; hold/bounce produces no extra transitions; the deliberate case-study press is 350 ms LOW/350 ms release | FAIL: clean long-hold control PASS, release rebound advances twice on device-observer variant (T04); [device input evidence](evidence/device-inputs-2026-11-01-run3/README.md) |
| RTH-07 | P | Distinguish an invalid/absent reading from valid 0 C; a fault must not create a new heat request; show SENSOR ERROR or an equivalent indication | FAIL: BUG-T03, live-reconfirmed 2026-11-01; [capture](evidence/live-2026-11-01/live-serial.log) |
| RTH-08 | D/P | TFT shows the current valid temperature, mode and thresholds; P: text is readable in the normal orientation and an invalid reading is not disguised as 0 C | Stable normal/edit field consistency PASS at completed drawing-call level; invalid-sensor false zero FAIL T03; mode-delay FAIL T05. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RTH-09 | P | Startup contains no GPIO/IPC/ISR installation errors; UI and temperature control operate after startup | PASS for captured startup and executed encoder/30-press/rapid-train controls. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RTH-10 | P | HIGH/LOW heat-request semantics agree with relay transistor configuration and COM/NO/NC; initial/restart/fault contact behavior is checked separately | Settled simulated HIGH/LOW contact semantics PASS; early boot GPIO HIGH is recorded without a glitch-free power-on claim. Physical bench excluded. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RTH-11 | P | After sensor data is restored, valid readings return and control follows the agreed recovery policy, without remaining latched on because of the previous fault | PASS for recovery in all four initial ON/OFF × restored low/high combinations and proposed 5 s recovery gate. [live campaign](evidence/campaign-live-2026-11-01/README.md) |
| RTH-12 | P | Temperature/fault response within 5 s of simulated time; button-to-mode feedback within 500 ms of simulated time | Temperature/fault/recovery 5 s gates executed; 20-cycle maximum 1890 device ms PASS. UI 500 ms gate remains FAIL T05 (1024 ms). [live campaign](evidence/campaign-live-2026-11-01/README.md) |

## Assessment assumptions

This educational assessment adopts: sensor faults must not create a new heat request; reset restores RAM defaults; setpoint source limits are -50/100 C with a 0.5 C gap; a deliberate input is 350 ms LOW followed by 350 ms release. Short 30 ms trains are negative filtering/state-integrity tests, not required one-action-per-pulse inputs. Temperature/fault/recovery use a proposed 5000 ms device-time budget and mode feedback uses 500 ms. These assumptions are explicit test oracles, not externally approved industrial policies. Physical operating range, heater safety, persistence and product approval require a separately scoped specification.

## Acceptance gate

All mandatory RTH-01–12 criteria require an agreed oracle, an executed test and evidence for an identified build. PARTIAL/NOT RUN/SKIPPED are not PASS. RTH-07 currently FAILS, so the product does not pass acceptance. Approval of the proposed criteria is not claimed. See [Release Decision](release-decision.md).


Validation levels: main firmware T03 startup fault is confirmed without instrumentation; separate identified Wokwi variants add device input/timing and sensor sampling evidence. Their source differences are included. The proposed 500 ms criterion remains a case-study assumption, not an approved industrial SLA.

[Debounce-boundary/fault-contact follow-up](evidence/campaign-debounce-2026-11-01/README.md): 4 passed; requested 199/200/201 ms short-pulse trains and settled fault/reset contacts executed. Combined live campaign: 25 cases, 23 passed/2 T03 failures, no errors or skips.
