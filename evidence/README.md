# Evidence

Start with the three bugs and the full test run:

| What to check | Evidence |
|---|---|
| T03: failed sensor requests heat | [Sensor-fault capture](bugs/sensor-fault/README.md), [UART waveform](runs/uart/README.md) |
| T04: release bounce advances twice | [Input test results and raw log](bugs/input-feedback/README.md) |
| T05: mode feedback takes 1024 ms | [The same input/timing run](bugs/input-feedback/README.md) |
| Control, limits, reset and recovery | [Full campaign](runs/campaign/README.md), [short-pulse/fault-reset follow-up](runs/inputs/README.md) |

## Folder guide

- **bugs/** â€” direct evidence for the three bug reports.
- **runs/** â€” campaign, sensor-boundary and recovery records. Each sensor run keeps its cases together in `cases.json`.
- **components/** â€” controlled-clock tests and cleaned-source build checks.
- **support/** â€” build identities, captured sources, earlier-practice logs and the combined offline report.

## Results

The live campaign and follow-up total **23 passed / 2 failed**; both failures reproduce T03. The separate input run has **1 passed / 2 failed**, reproducing T04/T05. [Offline assertions](support/offline.xml): **54 passed / 4 failed**, including two checks of T03. Several assertions check the same bug.

Each run includes Serial logs, input events, results and build details. [File hashes](../evidence-manifest.csv) verify the recorded files. Host timestamps are receipt times; device timing and component clocks are identified separately. Simulation does not validate a physical heater.

[Run instructions](../README.md) Â· [Test Matrix](../test-matrix.md) Â· [Release Decision](../release-decision.md)
