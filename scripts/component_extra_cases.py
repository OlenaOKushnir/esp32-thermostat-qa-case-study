"""Additional boundary, valid-zero and recovery controls for unchanged functions."""
SCENARIOS = {}
for initial in (0, 1):
    for temperature in (19.9, 20.0, 20.1, 24.9, 25.0, 25.1):
        expected = 1 if temperature < 20 else 0 if temperature >= 25 else initial
        name = f'boundary_{temperature:.1f}_prior_{initial}'
        SCENARIOS[name] = f'''
 relayState={initial}; output_level={initial}; sensor_value={temperature}f;
 loop();
 sprintf(result,"{{\\"actual_output\\":%d,\\"expected_output\\":{expected},\\"temperature\\":{temperature},\\"prior_output\\":{initial}}}",output_level);
'''
    SCENARIOS[f'valid_zero_prior_{initial}'] = f'''
 relayState={initial}; output_level={initial}; sensor_value=0.0f;
 loop();
 sprintf(result,"{{\\"actual_output\\":%d,\\"expected_output\\":1,\\"reading\\":%.1f}}",output_level,readTemperature());
'''
    for restored in (19.0, 25.0):
        expected = 1 if restored < 20 else 0
        SCENARIOS[f'recovery_prior_{initial}_restored_{int(restored)}'] = f'''
 relayState={initial}; output_level={initial}; sensor_value=0.0f/0.0f;
 loop(); int fault_output=output_level; float fault_reading=readTemperature();
 sensor_value={restored}f; fake_time=3000; loop();
 sprintf(result,"{{\\"actual_output\\":%d,\\"expected_output\\":{expected},\\"fault_output\\":%d,\\"fault_reading\\":%.1f,\\"restored_temperature\\":{restored}}}",output_level,fault_output,fault_reading);
'''
