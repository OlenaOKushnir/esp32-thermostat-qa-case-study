# Source and adaptation

Based on [Simple Thermostat](https://wokwi.com/projects/411208319078814721). Original sketch/diagram are preserved in upstream/. Original diagram author: Anonymous maker. 

The QA work includes the test plan, matrices, bug reports, automated checks and evidence. Three validation images add logging and GPIO test inputs; their source differences are included.

Pins: DHT22 data 16; relay request 5; TFT CS14/RST17/DC4/MOSI23/SCK18/MISO19; encoder CLK25/DT26/SW27. No physical heater, thermal room model, networking or command API is present in the main firmware.

Working sources remove inactive DS18B20 code, unused includes/global and comments. Captured sources remain in evidence/support/sources to match the recorded runs; source_identity.py verifies the transformation. Four cleaned builds have identical loadable sections. Third-party license notices and upstream originals remain intact. The unused OneWire dependency is removed.
