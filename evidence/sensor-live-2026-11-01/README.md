# Sensor boundary, valid-zero and dynamic fault execution — 2026-11-01

Image: [identity](identity.json); separate ESP32 sensor-observer build, VS Code SUCCESS in 51.84 s. [Instrumentation difference](../../validation/sensor/instrumentation.diff): one additive Serial sample observer after updateRelay. The real simulated DHT22 supplies values; no fake sensor returns are inserted into firmware.

[Raw Serial](serial.log) records returned temperature, device millis and request state. [Input requests](inputs.jsonl) record requested UI changes; request time is not an electrical edge or timing guarantee. Each Bxx/Z01 JSON binds expected output to at least two actual samples. F01 is an observation of retained HIGH during a confirmed fault, not a safety PASS. The capture ended at its 600-second limit; reconnection results are in the continuation capture below.

| Sequence | Observed request |
|---|---|
| B01: 19.9 C after initial 24 C/OFF | HIGH |
| B02/B03/B04: 20.0 / 20.1 / 24.9 after ON | HIGH retained |
| B05/B06/B07: 25.0 / 25.1 / 25.0 | LOW |
| B08/B09/B10: 24.9 / 20.1 / 20.0 after OFF | LOW retained |
| B11/B12: 19.9 then 25.1 | HIGH then LOW |
| Z01: valid 0 C after OFF | HIGH, no DHT error in the case window |
| F01: sensor data disconnected while ON | Repeated DHT errors; false 0 C/HIGH retained |

These device checks support control boundaries and both hysteresis histories. They are not 20-cycle endurance or physical GPIO/contact measurements. F01's initial action request preceded the effective switch action; the first confirmed fault is the raw DHT error at host 501.203 s, device sample ms=233577.

[Continuation: recovery and OFF-state fault](../sensor-recovery-2026-11-01/README.md). [Automated raw-sample checks](../../sensor_checks/test_sensor_evidence.py): combined sensor-capture evaluation reports 18 passed/1 failed (dynamic T03).
