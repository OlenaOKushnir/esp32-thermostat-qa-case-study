# Release Decision — Thermostat

**NO-GO.** T03 fails the fault-handling criterion: invalid sensor data becomes 0 C and can create a heat request. This leaves critical risk RISK-T01 open.

T04 (release bounce) and T05 (delayed mode feedback) also remain open. Passing control, reset and recovery tests do not resolve these failures.

## Evidence

- [Sensor fault](evidence/bugs/sensor-fault/README.md): read failure followed by a heat request.
- [Input and feedback tests](evidence/bugs/input-feedback/README.md): two mode transitions after release bounce; matching display frame after 1024 ms, exceeding the proposed 500 ms limit.
- [Test Matrix](test-matrix.md): results and evidence for all planned tests.

## Before reconsidering release

1. Fix invalid-sensor handling, button debounce and mode feedback.
2. Build the new firmware and rerun the affected tests and regression suite.
3. Confirm the [exit criteria](master-test-plan.md) pass and save the new results without replacing the original failure evidence.

This recommendation covers the simulation. A physical product also needs hardware testing.
