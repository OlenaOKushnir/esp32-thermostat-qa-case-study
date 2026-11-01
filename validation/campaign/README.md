# Complete acceptance campaign

This separate ESP32 image preserves production functions and adds GPIO stimulus and measurements. Main firmware is unchanged. The final adapter build succeeded in VS Code on 2026-11-01 in 14.33 seconds.

**Execution status: COMPLETE.** 19 passed/2 failures, no errors or skips. Both failures reproduce T03. [Raw evidence and verdicts](../../evidence/campaign-live-2026-11-01/README.md).

## Run

1. Build with **Thermostat: Build complete campaign** in VS Code.
2. Use **Wokwi: Select Config File** to select `validation/campaign/wokwi.toml`, then **Wokwi: Start Simulator**. Keep the simulator tab visible and desktop available. Wait for `[QA_READY]` and a valid 24 C sample.
3. Install both Python requirement files in the same test environment. From the project root run:

```powershell
python -m pip install -r requirements-test.txt -r requirements-live.txt
python -m pytest campaign_tests -v -s --campaign-output runs/campaign-001 --junitxml runs/campaign-001.xml
```

Use a new output directory each time. The client saves raw Serial, commands, observations and source/config/binary hashes. Default transport: `rfc2217://localhost:4003`. A timeout or incomplete capture is an execution blocker, not a product verdict.

## Coverage and limits

Startup defaults; both encoder directions and half steps; four threshold limits/clamping/reversal; VIEW rotation; 30 deliberate presses (350 ms LOW/350 ms release); rapid 20-press train; reset from four states; 20 hysteresis cycles; settled contacts; four fault/recovery combinations; stable display fields; valid zero/negative temperature.

GPIO33 emits DHT22 wire data to GPIO16. GPIO13/12 drive quadrature on GPIO25/26; GPIO32 drives button GPIO27. A task on the other core supplies signals without assigning production thresholds, mode, encoder counts or relay state. Device acknowledgment/sample timestamps measure response; host receipt times do not.

GPIO36 independently observes GPIO5. Grounded COM and pulled-up GPIO34/35 observe NO/NC. Contact assertions wait for a subsequent sample after switching; early boot and configured-output readings are separate. These simulated levels do not certify a physical load. Display hooks record completed drawing calls and fields, not optical pixels.

Fault injection suppresses DHT responses, unlike the normal fixture's data switch. Retain fixture identity and source differences with eventual results. Policy/timing criteria remain proposed case-study oracles.

[Instrumentation difference](instrumentation.diff) · [Live suite](../../campaign_tests/test_acceptance_campaign.py) · [Existing evidence](../../evidence/README.md)

[Debounce-boundary/fault-contact follow-up](../../evidence/campaign-debounce-2026-11-01/README.md): 4 passed; requested 199/200/201 ms short-pulse trains and settled fault/reset contacts executed. Combined live campaign: 25 cases, 23 passed/2 T03 failures, no errors or skips.
