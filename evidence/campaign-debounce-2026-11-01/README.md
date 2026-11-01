# Debounce-boundary and fault-contact follow-up — 2026-11-01

**4 passed, no failures/errors/skips.** This supplements the 21-case full campaign; together they contain 25 executed cases, 23 passed/2 T03 failures. Counts repeat checks of existing findings.

Ten 30 ms pulses were injected at each requested period of 199, 200 and 201 device ms, in two groups of five to fit the UART receive buffer. Within-group actual intervals, acknowledgments, accepted mode events and final state are saved in observations.json. Inter-group host transport gaps are not treated as the target interval. Each observed transition matches one injected LOW window, no clean pulse creates multiple transitions, final mode agrees with accepted-event count and setpoints remain unchanged. MODE timestamps follow Serial logging and are not precise debounce-decision timestamps. Exact 199/200/201 ms source boundaries are separately executed with a controlled component clock. This is negative short-pulse filtering/state-integrity evidence, not a promise that every short pulse must be accepted. The separate 30-press control defines deliberate inputs as 350 ms LOW/350 ms release.

The fourth check holds the sensor fault through a subsequent sample, observes settled GPIO HIGH/COM-NO closure, then resets from fault and confirms valid 24 C, configured LOW and COM-NC. The HIGH fault contact is electrical correlation with known T03, not a safety acceptance PASS. No physical heater or rail-to-reset waveform is certified.

[Raw Serial](serial.log) · [Input events](commands.jsonl) · [Observations](observations.json) · [Identity](identity.json) · [JUnit](pytest.xml)
