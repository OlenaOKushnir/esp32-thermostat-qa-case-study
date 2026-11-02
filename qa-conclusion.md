# QA Conclusion — ESP32 Thermostat

The thermostat was tested in Wokwi using a risk-based approach. Testing covered temperature boundaries and hysteresis, encoder settings, button input, display feedback, sensor faults, recovery, reset and relay contacts.

The main campaign and follow-up contain **25 tests: 23 passed and 2 failed**. Both failures reproduce T03, where a sensor fault starts heating. Separate input tests reproduce T04 (release bounce advances two modes) and T05 (mode feedback takes 1024 ms against the proposed 500 ms limit). Offline checks report **54 passed and 4 failed assertions** about these same three bugs.

**Release recommendation: NO-GO.** The sensor-fault risk remains unresolved. Fix the three bugs and rerun regression tests before reconsidering release. This conclusion covers simulation; physical hardware was not tested.

[Release Decision](release-decision.md) · [Test Matrix](test-matrix.md) · [Evidence](evidence/README.md)
