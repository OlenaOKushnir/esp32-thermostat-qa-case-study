# Test Design Decisions

## Initialize the encoder in setup

The global Encoder constructor installed interrupts before the scheduler was ready. Moving construction into `setup()` removed that startup problem without changing temperature control. Reboot and encoder boundary/reversal tests pass. [Results](../evidence/runs/campaign/README.md).

## Check both hysteresis histories

At 20/25 C limits, 19→22→25→22 should produce ON→ON→OFF→OFF. The same 22 C must keep ON after a cold reading and OFF after a warm reading. Testing both histories caught the state dependency; twenty cycles then checked repeatability. [Results](../evidence/runs/campaign/README.md).

## Inject faults at the sensor connection

Disconnect the DHT data line while keeping its pull-up. This exercises the sensor-error path without assigning a fake product temperature or relay state. Separate test images log GPIO and display events.

Use device clocks for response timing. Mode logs written after Serial output cannot establish the exact debounce boundary, so that boundary is checked with a controlled component clock. [Sensor fault](../bug-reports/BUG-T03.md) · [Input/timing results](../evidence/bugs/input-feedback/README.md).
