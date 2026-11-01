# Dynamic sensor recovery and OFF-state fault — 2026-11-01

Continuation of the same running sensor-observer simulation; [build identity](../sensor-live-2026-11-01/identity.json). No reset occurs between the two captures. The recorder uses a fresh host elapsed clock. [Raw Serial](serial.log), [input requests](inputs.jsonl), [JUnit](pytest.xml).

- R01: after the ON-state fault, reconnect at 25 C. Repeated valid 25 C samples report LOW: restored-data control PASS.
- F02: disconnect from the established 25 C/LOW state. DHT errors and 0 C/HIGH follow: **FAIL**, dynamic BUG-T03. The UI-action request preceded the effective toggle; use the raw error/sample sequence, not request time, to establish the fault.
- R02: set the disconnected sensor model to 19 C, then reconnect. Repeated valid 19 C samples report HIGH: restored-data control PASS.

Combined checks of the two sensor captures: **18 passed/1 failed**. The failure is the known T03 under a dynamic precondition, not another independent bug. No recovery latency budget or complete repeated-fault matrix is claimed. Capture was stopped by the operator after R02; the simulator was subsequently stopped and the switch left connected. Request-state samples do not establish relay contact polarity or physical heater behavior.
