# Three Technical Decisions

## 1. Defer encoder construction until setup

The global Encoder constructor installed interrupts before the scheduler was ready. A function-static instance in `setup()` removes that blocker. Captured reboot and GPIO encoder boundary/reversal checks pass. The tradeoff is a small integration adaptation; upstream source remains available.

Interview point: clean boot alone is insufficient; input regression must pass. [Evidence](../evidence/campaign-live-2026-11-01/README.md).

## 2. Test hysteresis with state history

At 20/25 C thresholds, 19→22→25→22 must produce ON→ON→OFF→OFF. The same 22 C has two correct outputs depending on history. Exact boundaries and 20 cycles produced 80 correct states and 40 request edges. This is short repetition coverage, not lifetime endurance.

Interview point: stateful behavior needs both histories, equality cases and transition counts. [Evidence](../evidence/campaign-live-2026-11-01/README.md).

## 3. Separate stimulus, measurement and policy

Disconnect DHT data while retaining its pull-up. Separate identified variants provide GPIO/frame observations. Device clocks support response timing; host receipt times and post-Serial mode logs have different meanings. Exact debounce boundaries use a controlled component clock.

The invalid reading and false-zero display share T03's root cause. Critical risk remains open despite passing controls, so release is NO-GO. Simulation establishes modeled contacts, not real heater safety. [Fault](../bug-reports/BUG-T03.md) · [Timing](../evidence/device-inputs-2026-11-01-run3/README.md).
