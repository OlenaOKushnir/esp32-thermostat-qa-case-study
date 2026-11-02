# Assignment Checklist

| Assignment requirement | Delivered artifact / status |
|---|---|
| Select an embedded/IoT device | ESP32/DHT22 thermostat with display, encoder and relay; Wokwi simulation. Physical hardware was not tested |
| System Overview and Scope | [Master Test Plan](../master-test-plan.md), sections 2, 4-6 |
| At least five justified quality risks | [Risk Matrix](../risk-matrix.md): eight risks, consequences, scores, tests and evidence |
| Test Matrix with goals, types, levels, priorities and expected results | [Test Matrix](../test-matrix.md): TT-01-13, P0/P1, requirement/risk links and test results |
| Evidence from preceding practice | [Hysteresis](../evidence/support/previous-hysteresis.log), [sensor fault](../evidence/support/previous-sensor-fault.log), plus [evidence package](../evidence/README.md) |
| Entry / Exit Criteria | Master Test Plan sections 11-12; execution complete, product acceptance fails |
| Case Study in GitHub/Markdown | [README](../README.md) and Markdown portfolio |
| Acceptance Criteria | [RTH-01-12](../requirements.md), firmware behavior and proposed criteria distinguished |
| Three Bug Reports | [T03](../bug-reports/BUG-T03.md), [T04](../bug-reports/BUG-T04.md), [T05](../bug-reports/BUG-T05.md), all OPEN |
| Protocol trace | [UART TX and heat-request waveform](../evidence/runs/uart/README.md); DHT22 uses single-wire data, not I2C |
| CV project entry | [Resume text](../resume/README.md) |
| Pytest suite | Recorded baseline, sensor/component assertions, live input and campaign suites; [commands](../README.md) |
| Release Decision / QA Conclusion | [NO-GO](../release-decision.md), [conclusion](../qa-conclusion.md), driven by critical risk |
| Technical decisions | [Three decisions](technical-decisions.md) with evidence and tradeoffs |

