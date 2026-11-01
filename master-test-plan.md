# Master Test Plan — ESP32 Thermostat

Version 1.3 | 2026-11-01 | QA portfolio: Olena | Recommendation: **NO-GO**

## 1. Document Purpose

Assess the simulated thermostat using risk-based tests, identifiable evidence and explicit acceptance oracles. The submission contains an executed baseline study with three open product findings. This plan applies only to this thermostat; no network/heap results from an earlier IoT project are reused.

## 2. System Overview

ESP32 DevKit C v4 reads a DHT22 over GPIO16, displays temperature/mode/setpoints on an SPI ILI9341 and controls a relay request on GPIO5. A KY-040 encoder uses CLK25/DT26/SW27. Modes are VIEW, SET LOWER and SET UPPER; defaults are 20/25 C. Settings are held in RAM.

Data path: DHT22 → readTemperature → updateRelay → GPIO5. T<lower requests HIGH; T>=upper requests LOW; the deadband retains the preceding state. Encoder counts change setpoints by 0.5 C. TFT pins: CS14/RST17/DC4/MOSI23/SCK18/MISO19. There is no network backend, real heater or room thermal model.

The original normal fixture includes the DHT model, encoder, display, relay and an inline sensor-data switch. Separate identified variants add observation and GPIO test stimulus. Validation instrumentation is separate from the main source.

## 3. Quality Objectives

Prevent invalid sensor data from creating an unintended heat request; preserve boundaries, hysteresis and valid setpoint gaps; handle deliberate inputs predictably; present truthful feedback; restore defined defaults after reset; identify output/contact semantics.

[Acceptance Criteria](acceptance-criteria.md) defines twelve source-derived (D) or proposed engineering (P) oracles. Proposed no-new-heat fault handling, 5000 ms temperature/fault/recovery and 500 ms mode-feedback budgets are explicit educational assessment assumptions, not certified industrial requirements.

## 4. Scope

Startup and configured-output defaults; exact temperature boundaries and both hysteresis histories; twenty control cycles; both encoder directions, setpoint limits/gaps/clamp/reversal and VIEW rotation; deliberate/held/rapid/bouncing button input; stable display fields; invalid sensor versus valid zero/negative readings; startup/dynamic faults; complete ON/OFF × low/high restoration matrix; four-state warm reset; settled simulated relay contacts; device-time response; evidence/provenance regression.

All planned simulation categories have executed results in the [Test Matrix](test-matrix.md). Acceptance failures remain failures; execution completion does not imply product acceptance.

## 5. Out of Scope

Physical mains/load/thermal safety, real sensor accuracy/calibration, electrical supply/brown-out/EMI/EMC qualification, hardware endurance, certification and physical-product release. No bench or heater exists in this project. Network and product command-parser testing do not apply. Firmware restores RAM defaults; persistence is not an acceptance requirement in this baseline.

## 6. Assumptions / Constraints

Wokwi models electrical behavior. Contact probes are not real load measurements. Instrumented variants may affect scheduling; their exact source differences and binary identities accompany results. DHT-model manual inputs and GPIO wire-protocol stimulus provide complementary evidence.

Host timestamps record receipt/request time; timing verdicts use device acknowledgments, samples and completed-frame timestamps. Stable drawing-call field checks do not establish optical pixel quality. Cold-boot observation starts after Serial initialization; early GPIO5 HIGH before application initialization is recorded and no glitch-free rail-to-reset guarantee is claimed.

## 7. Quality Risks

[Risk Matrix](risk-matrix.md) prioritizes eight risks with Impact×Probability scores. Critical RISK-T01 (score 9) is invalid sensor input creating a heat request. Its trace is RTH-07/11/12 → TT-07/08 → raw startup/dynamic fault captures → BUG-T03 → NO-GO. Other risks cover hysteresis, settings, inputs, display, startup, reset and polarity. Scores are expert priorities, not measured probabilities.

## 8. Test Levels

- Component: unchanged C-compatible function bodies with hardware doubles; 27 retained scenarios including boundary, clamping, zero and recovery controls, plus three newly executed exact debounce-clock scenarios.
- Interface/system: actual ESP32 firmware in Wokwi with GPIO stimulus, DHT22 wire protocol, encoder/button signals, display observers and independent output/contact inputs.
- Fault/recovery: normal-model data disconnect plus response suppression in a separately identified protocol fixture; four recovery combinations and four warm-reset states.
- Host regression: saved-evidence assertions and package identity/link checks, explicitly separate from live tests.

## 9. Test Types

Functional/state transition, boundary and negative inputs, hysteresis/history, input repetition/debounce, fault injection/recovery, warm reset, UI field/feedback consistency, simulated response timing, twenty-cycle repetition, GPIO/contact correlation and evidence provenance. Twenty cycles are a short control repetition, not lifetime endurance qualification.

## 10. Test Environment

VS Code, Wokwi 4.1.0 and PlatformIO IDE 3.3.4 were observed installed; the user activated the Wokwi license. Builds use espressif32 7.1.3 with vendored library sources recorded in [dependencies](docs/dependencies.json). Main firmware/config/diagram and build artifacts are identified in [tested-build.json](evidence/tested-build.json); variant identities are in [validation-builds.json](evidence/validation-builds.json).

RFC2217 uses localhost:4000 (main), 4001 (input variant), 4002 (sensor observer), 4003 (full campaign), 115200 baud. Host tooling uses Python, Pytest and pyserial. Campaign GPIO33→16 supplies DHT22 data; GPIO13/12→25/26 and GPIO32→27 drive controls. GPIO36 observes request5; pulled-up GPIO34/35 sense grounded COM through NO/NC. No external physical load is attached.

## 11. Entry Criteria

Source, executable, fixture and dependencies identified; assessment oracles documented; build SUCCESS; simulator operational; observable input/output and Serial; defined initial mode, thresholds, temperature and output history; known findings listed; no heater attached. These conditions were met for the completed runs. Incomplete fixture/debug attempts were excluded from product verdict evidence.

## 12. Exit Criteria

1. Execute all in-scope simulation categories on identified baseline/variant images and retain raw stimulus/output records.
2. Pass exact boundaries, hysteresis histories, setpoint/gap controls, deliberate inputs, reset and recovery controls.
3. Complete twenty cycles with correct state history and request transitions; satisfy adopted device-time budgets.
4. Correlate settled GPIO request and modeled contacts; qualify boot and physical limits separately.
5. Resolve or explicitly report every acceptance failure; retain failed evidence and bug traceability.
6. For a positive product recommendation, no open High safety/control defects and no failing mandatory acceptance oracles.

Execution and evidence gates are complete. **Product acceptance FAILS** because T03, T04 and T05 remain open. Physical qualification is excluded from this simulation assessment, not marked passed.

## 13. Regression Strategy

After source/config/library changes: build and startup/hysteresis smoke. Control/setpoint changes require TT-02–05 plus fault/recovery. Sensor fixes require startup/dynamic faults, valid zero/negative, all recovery combinations and response timing. Input/UI fixes require both encoder directions, boundaries, deliberate/rapid/bouncing inputs and feedback timing. Diagram/output changes require field and contact correlation. A new candidate requires fresh live evidence; historical failing logs remain immutable.

## 14. Evidence Strategy

[Evidence index](evidence/README.md) links raw Serial, command/input events, observed values, reports, source/config/binary identities and instrumentation differences. [Full campaign](evidence/campaign-live-2026-11-01/README.md): 21 cases, 19 passed/2 T03 failures, no errors/skips; twenty cycles give 80 states and 40 request edges including 20 rising. Maximum matching temperature sample response was 1890 device ms.

Earlier unmodified-main T03, device-input T04/T05 and manual DHT-model exact boundaries remain independently identified. Host replay counts repeat assertions about known findings; they do not count new bugs. Evidence manifest hashes protect all retained records.

## 15. Defect Management

Observed → reproduced/triaged → fix → fresh retest → closed/reopened. Reports contain build/fixture, preconditions, steps, expected/actual, evidence, impact, severity/priority and status. [T03](bug-reports/BUG-T03.md) invalid sensor handling, [T04](bug-reports/BUG-T04.md) release bounce and [T05](bug-reports/BUG-T05.md) delayed mode feedback remain OPEN. Fixed T01 startup and T02 orientation are separate integration history. No artificial firmware defects were inserted. QA documents and recommends; physical-product requirement/release approval is outside this educational assessment.

## 16. Residual Risks

Three open defects; early pre-initialization GPIO behavior; instrumentation scheduling effects; simulation fidelity and absence of a physical bench. The GPIO campaign does not prove physical sensor accuracy, safe heater power or lifetime reliability. Proposed policies are explicit study oracles. These limits are retained with results, not silently accepted as production readiness.

## 17. Release Recommendation

**NO-GO**, primarily because critical RISK-T01 remains: failed sensor reads become 0 C and can create heat requests. T04 and T05 add input/UI acceptance failures. Completed control/reset/contact tests and pass counts do not override defect impact. Reconsider after production fixes and fresh risk-based regression; any physical release additionally needs a separately scoped hardware qualification. [Release Decision](release-decision.md) · [QA Conclusion](qa-conclusion.md).

[Debounce-boundary/fault-contact follow-up](evidence/campaign-debounce-2026-11-01/README.md): 4 passed; requested 199/200/201 ms short-pulse trains and settled fault/reset contacts executed. Combined live campaign: 25 cases, 23 passed/2 T03 failures, no errors or skips.
