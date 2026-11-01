# Live device input and feedback tests — 2026-11-01

Scope: TT-06/09/13; BUG-T04/T05; RTH-06 and proposed RTH-12. This run executes a separate instrumented ESP32 image in Wokwi, with original control decisions and additive observers/stimulus. It is not a new result from the unmodified main firmware binary. [Exact instrumentation](../../validation/device/instrumentation.diff).

Build: VS Code task SUCCESS, 53.98 s. Source/config/binary identities are in [identity.json](identity.json). Serial localhost:4001, 115200. The live Pytest fixture connected before a captured restart and recorded through VAL_END. It evaluates newly received results rather than replaying saved component JSON. GPIO32 drives the button input on GPIO27; no direct mode/threshold/output assignment is used by the stimulus controller.

| Case | Expected | Observed | Result |
|---|---|---|---|
| Clean long press | One transition, mode 1 | Mode 1 | PASS |
| Release rebound | One transition, mode 1 | Mode 2 after 1100 ms hold, HIGH 5 ms / LOW 20 ms release rebound | FAIL, T04 |
| Feedback | Completed matching mode frame within proposed 500 ms | Accepted at 3793 ms; matching frame completed at 4817 ms: 1024 ms | FAIL, T05 under proposed budget |

[Raw Serial](serial.log) · [Parsed results](results.json) · [JUnit](pytest.xml): **1 passed / 2 failed**, no collection/setup errors in this retained completed run. Host RX timestamps and device millis are distinct. The frame callback measures completed driver rendering in simulation; it does not measure physical TFT photons or approve the 500 ms requirement.

T04 is device-reproduced on this instrumented variant and remains OPEN. T05 is device-measured on this variant and remains OPEN against a proposed timing budget. Their earlier component cases remain preserved. Baseline source/binaries were not changed to introduce or fix product defects.
