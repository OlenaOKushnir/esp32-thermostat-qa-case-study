# Source and adaptation

Based on [Simple Thermostat](https://wokwi.com/projects/411208319078814721), retrieved 2026-10-27. Original sketch/diagram are preserved in upstream/. Original diagram author: Anonymous maker. Original authorship is not claimed; upstream licensing was not established.

Adaptations: PlatformIO configuration and vendored dependencies; Arduino.h and C++ forward declarations; deferred Encoder construction in setup; TFT diagram rotation; 10k data pull-up to 3V3; normal and disconnected-data fixtures; RFC2217 and VS Code tasks. Temperature, relay, threshold and debounce decisions in the main source remain the baseline under investigation.

QA assets include acceptance criteria, risk/test matrices, manual and automated evidence, negative component tests, safe capture/fixture/run tooling and three open product reports. Three separate validation images add observers and, for input tests, a pin-waveform controller. Their complete source/config/binary identities and source differences accompany results. Instrumented images are not presented as the unmodified main firmware.

Pins: DHT22 data 16; relay request 5; TFT CS14/RST17/DC4/MOSI23/SCK18/MISO19; encoder CLK25/DT26/SW27. No physical heater, thermal room model, networking or command API is present in the main firmware.

Working sources remove inactive DS18B20 code, unused includes/global and comments. Captured sources remain in evidence/sources for provenance; source_identity.py verifies the transformation. Four cleaned builds have identical loadable sections. Third-party license notices and upstream originals remain intact. The unused OneWire dependency is removed.
