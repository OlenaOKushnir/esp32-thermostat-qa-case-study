# Assignment Checklist

| Assignment requirement | Delivered artifact / status |
|---|---|
| Select an embedded/IoT device | ESP32/DHT22 thermostat with display, encoder and relay; Wokwi simulation. **Physical-device evidence is outside scope**, so the literal physical-device condition is not claimed fulfilled |
| System Overview and Scope | [Master Test Plan](../master-test-plan.md), sections 2, 4–6 |
| At least five justified quality risks | [Risk Matrix](../risk-matrix.md): eight risks, consequences, scores, tests and evidence |
| Test Matrix with goals, types, levels, priorities and expected results | [Test Matrix](../test-matrix.md): TT-01–13, P0/P1, requirement/risk links and executed verdicts |
| Evidence from preceding practice | [Hysteresis](../evidence/hysteresis-runtime.log), [sensor fault](../evidence/sensor-failure-runtime.log), plus identified current [evidence package](../evidence/README.md) |
| Entry / Exit Criteria | Master Test Plan sections 11–12; execution complete, product acceptance fails |
| Case Study in GitHub/Markdown | [README](../README.md) and Markdown portfolio prepared locally; GitHub creation/upload is reserved for the student |
| Acceptance Criteria | [RTH-01–12](../acceptance-criteria.md), source-derived/proposed oracles distinguished |
| Three Bug Reports | [T03](../bug-reports/BUG-T03.md), [T04](../bug-reports/BUG-T04.md), [T05](../bug-reports/BUG-T05.md), all OPEN |
| Pytest suite | Recorded baseline, sensor/component assertions, live input and campaign suites; [commands](../README.md) |
| Release Decision / QA Conclusion | [NO-GO](../release-decision.md), [conclusion](../qa-conclusion.md), driven by critical risk |
| Defensible technical decisions | [Three decisions](technical-decisions.md) with evidence and tradeoffs |

No firmware bugs were inserted. All simulation categories have executed results; product fixes and physical qualification are separate work. A ready submission package is not a passing product verdict.
