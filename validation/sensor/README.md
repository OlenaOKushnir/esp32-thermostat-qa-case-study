# Sensor-observation validation image

The main firmware is copied with one additive Serial observer after updateRelay. [Source difference](instrumentation.diff) is included. The observer reports ESP32 millis, returned temperature and software request state; it does not replace DHT22 data or alter control decisions.

Build with the sensor-validation VS Code task, or PlatformIO `-d validation/sensor`. Select `validation/sensor/wokwi.toml`; RFC2217 is localhost:4002. The supplied image built successfully in VS Code in 51.84 seconds. The fixture uses the normal DHT circuit and its inline data switch.

Change temperature through the DHT panel. For dynamic fault injection, close the panel and operate the data switch; restore it before the next normal test. The documented keyboard Fit shortcut is Shift+F in the focused canvas on this setup. [Executed evidence](../../evidence/sensor-live-2026-11-01/README.md).
