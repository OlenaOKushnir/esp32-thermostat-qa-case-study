# Cleaned-source Build and Regression

All four working sources remove comments, inactive DS18B20 branches, unused DHT_U/OneWire includes and the unused oldPosition global. Exact captured sources/differences remain in `evidence/sources/`; `scripts/source_identity.py` checks the transformation.

The VS Code **Build all images** task completed successfully for main, device, sensor and campaign. [Build comparison](builds.json) records source hashes and loadable ELF section hashes. All loadable sections match the captured images byte-for-byte; ELF debug information and derived image metadata may differ. Supplied baseline binaries/ELFs preserve captured identities. Reproduce a comparison with `python scripts/compare_images.py BEFORE.elf AFTER.elf`.

[Fresh component results](results.json) execute the cleaned main function bodies: all 27 scenario values match the retained extended run (25 controls and two T04/T05 findings). [Fresh exact-clock results](debounce.json): three 199/200/201 ms boundary controls PASS. These runs do not reclassify historical captures as newly executed live tests.
