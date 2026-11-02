# Live acceptance campaign — 2026-11-01

Result: **19 passed, 2 failed**, no errors or skips. Both failures reproduce BUG-T03 from an initially OFF state; they are not two new bugs. Full raw Serial, command events, observations, JUnit and source/config/binary identities are included.

## Executed controls

- Startup configured-output defaults and valid 24 C; warm reset from OFF, ON, SET LOWER and SET UPPER.
- Encoder both directions, 0.5 C steps, lower -50 C / upper 100 C, both minimum-gap edges, beyond-limit clamping and reversal; VIEW rotation leaves thresholds unchanged.
- Thirty deliberate button presses (350 ms LOW/350 ms release); rapid 20-press train checks bounded mode state and preserved gap, without claiming every 30 ms pulse is a valid press.
- Twenty hysteresis cycles (19→22→25→22 C), 80 measured states, 40 GPIO request edges including 20 rising edges. Maximum stimulus-ACK-to-matching-sample delay: **1890 device ms**, within the proposed 5000 ms gate.
- Settled GPIO5 LOW: NO open/NC closed; HIGH: NO closed/NC open. COM is grounded and contact probes use pull-ups. No physical load is present.
- All four initial ON/OFF × restored 19/25 C fault/recovery combinations executed, including device-time response gates. Recovery controls passed; OFF-to-fault creates a new heat request (T03 FAIL).
- Stable completed display-call fields match mode, temperature and thresholds in VIEW and both edit modes. Valid zero and negative temperature remain valid cold readings.

## Interpretation

This is an explicitly instrumented variant, not the unmodified main image. GPIO signals feed the unchanged production functions; adapter source and differences are identified. Timing measures device clocks, not host receipt gaps. Completed drawing-call fields do not prove optical pixel quality. Cold-start observation begins after Serial initialization; it does not establish a glitch-free rail-to-reset waveform. Early GPIO5 can be HIGH before application output initialization; physical boot/load safety remains outside this simulation claim.

The earlier main-image T03, input-variant T04/T05 and DHT-model exact boundaries remain separate evidence. The full campaign supplements them. Three product findings remain open and the release recommendation remains NO-GO. Proposed safety/timing policies are case-study oracles, not approved industrial requirements.

[Fixture and commands](../../../validation/campaign/README.md) · [Summary](summary.json) · [Identity](identity.json) · [JUnit](pytest.xml) · [Raw Serial](serial.log) · [Stimuli](commands.jsonl) · [Observations](observations.json)
