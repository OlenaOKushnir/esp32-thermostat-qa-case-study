# Master Test Plan - ESP32 Thermostat

Owner: Olena | Release recommendation: **NO-GO**

## 1. Document Purpose

Plan and record risk-based testing of the thermostat. The plan covers normal operation, failures, recovery and the conditions needed for release.

## 2. System Overview

The ESP32 reads a DHT22 and switches a relay using lower and upper temperature limits. Below the lower limit it requests heat; at or above the upper limit it switches off. Between the limits it keeps the previous state.

| Component | Connection / behavior |
|---|---|
| DHT22 | Single-wire data on GPIO16 |
| Relay | Heat request on GPIO5 |
| ILI9341 display | SPI; CS14, RST17, DC4, MOSI23, SCK18, MISO19 |
| KY-040 encoder | CLK25, DT26, SW27 |
| Settings | VIEW / SET LOWER / SET UPPER; 0.5 C steps |
| Defaults | Lower 20 C, upper 25 C; stored in RAM |

The test circuit includes a switch in the sensor data line. Additional test images provide logging and GPIO inputs.

## 3. Quality Objectives

Check correct temperature control, valid setpoint limits, reliable input handling, clear display feedback and recovery after faults or resets. A sensor failure must not create a new heat request. [Acceptance Criteria](requirements.md) defines the expected results, including the proposed 5 s control/recovery and 500 ms feedback limits.

## 4. Scope

Startup, temperature boundaries, hysteresis, encoder settings, button handling, display feedback, sensor faults, recovery, reset, relay contacts and response times. The [Test Matrix](test-matrix.md) contains the individual cases and results.

## 5. Out of Scope

Physical heater safety, supply faults, real sensor accuracy, EMI/EMC and long-term hardware reliability. The firmware has no network features. Settings reset to defaults; persistence is not required in this case study.

## 6. Assumptions / Constraints

Testing uses Wokwi. Logging and test inputs can affect timing, so each run records its test image. Device clocks measure response times; host timestamps show when data was received. Display measurements end when drawing calls complete.

Boot measurements start after Serial initialization. GPIO5 can be HIGH before output setup; these tests do not establish safe behavior throughout power-on.

## 7. Quality Risks

The [Risk Matrix](risk-matrix.md) ranks eight risks. The highest is RISK-T01: invalid sensor data can start heating. It links RTH-07/11/12 to fault/recovery tests TT-07/08, [sensor-fault evidence](evidence/bugs/sensor-fault/README.md) and BUG-T03. Other risks cover control logic, settings, inputs, display, startup, reset and relay polarity.

## 8. Test Levels

- Component: firmware functions with controlled inputs and a simulated clock.
- Interface: sensor data, encoder/button signals, display output and relay contacts.
- System: end-to-end thermostat operation in Wokwi.

Offline Pytest checks saved evidence separately from live simulator tests.

## 9. Test Types

Functional, boundary, negative, state-transition, input repetition, fault injection, recovery, reset, UI consistency and timing. Twenty control cycles provide a short repeatability check.

## 10. Test Environment

VS Code, Wokwi 4.1.0, PlatformIO IDE 3.3.4 and espressif32 7.1.3. Python tests use Pytest and pyserial. Library versions are in [dependencies](docs/dependencies.json); build details are in the [evidence records](evidence/README.md).

RFC2217 runs at 115200 baud: port 4000 for the main image, 4001 for input tests, 4002 for sensor observation and 4003 for the full campaign. Wiring and commands for test images are in the [test guide](automation/README.md).

## 11. Entry Criteria

- Source, build, dependencies and test circuit are recorded.
- The build succeeds and Wokwi starts.
- Initial temperature, settings, mode and output state are known.
- Inputs, Serial output and expected results are available.

These conditions were met for the recorded runs.

## 12. Exit Criteria

1. All planned cases are executed and linked to evidence.
2. Boundaries, hysteresis, settings, inputs, reset and recovery meet their criteria.
3. Twenty cycles show the expected states and transitions.
4. Temperature/fault/recovery response meets 5 s; mode feedback meets 500 ms.
5. GPIO requests match the modeled relay contacts.
6. No unresolved Critical/High control defect or failing mandatory criterion remains.

Testing is complete, but acceptance fails because T03/T04/T05 remain open.

## 13. Regression Strategy

| Change | Required tests |
|---|---|
| Source, library or configuration | Build, startup and control smoke test, then affected cases |
| Sensor/control logic | Boundaries, hysteresis, valid zero/negative readings, faults and recovery |
| Encoder/button/display | Settings, bounce, repeated input and feedback timing |
| Wiring or relay setup | Startup and GPIO/contact checks |
| Release candidate | Full test set |

Save new results after fixes and keep the original failure evidence.

## 14. Evidence Strategy

Keep Serial logs, the [UART waveform](evidence/runs/uart/README.md), input events, expected/actual results and build details for each run. Use device timestamps for timing checks. The [evidence index](evidence/README.md) links each bug and test run; file hashes check that recorded files have not changed.

## 15. Defect Management

Reports include preconditions, reproduction steps, expected/actual behavior, impact, severity, priority and evidence. Retest a fix before closing its report. Current open bugs: [T03 sensor failure](bug-reports/BUG-T03.md), [T04 release bounce](bug-reports/BUG-T04.md) and [T05 mode feedback](bug-reports/BUG-T05.md).

## 16. Residual Risks

The three bugs, pre-setup GPIO behavior and differences between simulation and hardware remain. Test instrumentation may affect timing. Physical safety and sensor accuracy need hardware tests.

## 17. Release Recommendation

**NO-GO.** Sensor failure can create a heat request, and input/UI failures remain. Fix the bugs and rerun regression before reconsidering release. [Release Decision](release-decision.md) / [QA Conclusion](qa-conclusion.md).
