# Device input/timing validation image

This separate ESP32 image retains the thermostat control decisions and adds frame/mode observers plus a GPIO32→GPIO27 test stimulus. The encoder push switch is disconnected in this fixture to avoid competing drivers. The controller applies real simulated pin transitions; it does not call toggleMode or assign production mode/threshold/output state.

Build from the parent project with the named VS Code device-validation task, or run PlatformIO with `-d validation/device`. Select `validation/device/wokwi.toml` in Wokwi; Serial is localhost:4001. The supplied binary was built successfully in VS Code (53.98 seconds).

Test order: mode feedback after a completed frame, clean 1100 ms hold, then 1100 ms hold with HIGH 5 ms / LOW 20 ms release rebound. GPIO and observer timestamps use ESP32 millis. [Instrumentation diff](instrumentation.diff) shows every additive source change. Hardware simulation uses the normal sensor fixture plus the stimulus wire; this is not the unmodified production binary.

[Executed results](../../evidence/device-inputs-2026-11-01-run3/README.md) · [Live Pytest suite](../../live_tests/test_device_inputs.py).
