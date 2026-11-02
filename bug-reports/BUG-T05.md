# BUG-T05 — Mode feedback exceeds the proposed deadline

**OPEN · Severity Low · Priority Medium**. RISK-T05/T04. Environment: identified Wokwi input/frame-observer image. The 500 ms deadline is a proposed case-study oracle, not an approved industrial SLA.

## Steps to Reproduce

1. Build/select `validation/device/wokwi.toml` and run the [live input suite](../README.md).
2. Restart after capture connects. The controller presses immediately after a completed display frame.
3. Compare accepted mode time with the next completed matching frame.

**Expected:** complete matching mode feedback within 500 device ms.

**Actual:** acceptance at 3793 ms; matching frame at 4817 ms; **1024 ms** elapsed. [Raw Serial](../evidence/bugs/input-feedback/serial.log), [JUnit](../evidence/bugs/input-feedback/pytest.xml). The live assertion fails. A [component control](../evidence/components/baseline/results.json) independently shows VIEW still rendered 510 fake-clock ms after mode changed; the next refresh corrects it.

## Cause, impact and disposition

`loop()` refreshes at 1000 ms intervals before handling input. `toggleMode()` changes mode without requesting a redraw. An encoder movement can affect a setting while the screen names the preceding mode.

Suggested fix: mark display state dirty on mode changes and refresh promptly without blocking control. Retest cycles, threshold feedback, repeated inputs and the adopted deadline. Stable display fields pass after refresh, but this does not satisfy response timing. The measured endpoint is a completed drawing call, not optical pixels or physical TFT latency. No fix is applied to the captured baseline.
