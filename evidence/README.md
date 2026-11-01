# Evidence Package

[Manifest](../evidence-manifest.csv) records sizes/SHA-256; [source inventory](source-hashes.json) covers maintained project files. Raw Serial and input events are preserved. Captured source snapshots retain the exact source/debug identities of supplied images; cleaned working sources are checked separately.

| Evidence | Purpose / result |
|---|---|
| [Main build identity](tested-build.json), [variant identities](validation-builds.json) | Source/config/firmware provenance |
| [Earlier hysteresis](hysteresis-runtime.log), [earlier sensor fault](sensor-failure-runtime.log) | Evidence from preceding thermostat practice; host-time limitations apply |
| [Main-image fault](live-2026-11-01/README.md) | T03 after reboot |
| [Extended components](extended-components/README.md) | Boundary/zero/recovery controls; 19 offline assertions PASS |
| [Device input/timing](device-inputs-2026-11-01-run3/README.md) | Clean hold PASS; bounce FAIL; completed frame 1024 ms versus proposed 500 ms FAIL |
| [DHT model inputs](sensor-live-2026-11-01/README.md), [recovery](sensor-recovery-2026-11-01/README.md) | Exact boundaries, zero and dynamic fault/reconnect histories |
| [Full campaign](campaign-live-2026-11-01/README.md) | 19 passed/2 T03 failures; 20 cycles, 80 states, 40 edges, max response 1890 device ms |
| [Short pulses/fault reset](campaign-debounce-2026-11-01/README.md) | Four passing electrical/state controls; combined live campaign 23 passed/2 failures |
| [Cleaned-source builds/regression](component-current/README.md) | Four builds with identical loadable sections; 27 component outcomes unchanged |
| [Combined offline JUnit](combined-offline.xml) | 54 passed/4 assertions failing on the same three known bugs |

Commands are in the [README](../README.md). Offline replay, fresh live input and component-clock execution are different test levels. Repeated T03 assertions do not create new bugs. Integrity PASS does not override product failures.

Record fixture, initial state, stimulus, device/host time basis, expected/actual and source/binary identity for every new run. Host receipt time cannot establish device latency. No physical heater or approved industrial SLA is claimed.
