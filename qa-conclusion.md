# QA Conclusion — ESP32 Thermostat

The simulated thermostat was tested using a risk-based approach. All in-scope simulation categories have executed results: startup, exact temperature boundaries, hysteresis, 20 repeated cycles, encoder/setpoint limits and reversal, deliberate/rapid/bouncing inputs, display fields and feedback, sensor faults and recovery, warm reset, and modeled relay contacts. Source, binary, fixture and instrumentation identities accompany the evidence. Physical hardware qualification is outside this assessment.

The completed live campaign has **25 cases: 23 passed, 2 failed, no errors or skips**. Both failures reproduce T03 from an initially OFF state. Twenty hysteresis cycles passed all 80 states with exactly 40 request edges, including 20 rising; maximum response was 1890 device ms against the proposed 5000 ms gate. Three additional controlled-clock component scenarios passed the exact 199/200/201 ms debounce boundaries. Live short-pulse logs establish input-to-mode consistency, not precise debounce-decision timing.

Three product findings remain OPEN: T03 converts invalid sensor data to 0 C and can create a heat request; T04 release bounce advances two modes; T05 completed matching feedback took 1024 device ms against the proposed 500 ms case-study budget. T03 is confirmed on the unmodified main image and instrumented variants; T04/T05 have separate component and live input-variant evidence. Fixed T01/T02 are integration history. No artificial firmware defects were inserted.

The offline baseline/extended/sensor evaluation remains 54 passed/4 failures, with repeated assertions about the same three findings. These counts are distinct from the newly executed live campaign and do not represent additional bugs.

**Release recommendation: NO-GO.** Critical risk RISK-T01 remains unresolved. The decision follows defect impact and failed acceptance criteria, not the number of passing tests. Production fixes require fresh regression; simulation results cannot establish physical heater safety or an approved industrial SLA.

[Release Decision](release-decision.md) · [Risk Matrix](risk-matrix.md) · [Test Matrix](test-matrix.md) · [Campaign](evidence/campaign-live-2026-11-01/README.md) · [Follow-up](evidence/campaign-debounce-2026-11-01/README.md)
