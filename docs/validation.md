# Validation Record

| Execution | Result | Evidence |
|---|---|---|
| Main-image absent sensor | T03 reproduced after reboot | [Raw capture](../evidence/live-2026-11-01/live-serial.log) |
| Device input/frame observer | Clean hold PASS; release bounce FAIL; feedback 1024 ms versus proposed 500 ms FAIL | [Run](../evidence/device-inputs-2026-11-01-run3/README.md) |
| DHT boundaries, zero and recovery | Boundaries/restored-data controls PASS; dynamic T03 FAIL | [Sensor](../evidence/sensor-live-2026-11-01/README.md), [recovery](../evidence/sensor-recovery-2026-11-01/README.md) |
| Full GPIO campaign | 19 passed/2 T03 failures; 20 cycles, 80 states, 40 edges; max response 1890 device ms | [Run](../evidence/campaign-live-2026-11-01/README.md) |
| Short pulses and fault/reset contacts | 4 passed; actual intervals retained | [Follow-up](../evidence/campaign-debounce-2026-11-01/README.md) |
| Exact debounce clock | 199/200 ms reject; 201 ms accepts | [Results](../evidence/component-current/README.md) |
| Cleaned sources | Four successful builds, identical loadable sections; 27 component values unchanged; three clock checks PASS | [Correspondence](../evidence/component-current/README.md) |

All planned simulation categories have executed results. T03/T04/T05 remain open; hardware qualification is outside scope. Raw logs remain unchanged. Derived observations omit duplicate progress snapshots and retain the complete final 80-state sequence.
