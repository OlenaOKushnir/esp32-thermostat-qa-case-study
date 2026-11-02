# Extended component execution

[Results](results.json) contain 27 actual isolated scenarios: the original nine plus twelve exact-boundary/history cases, two valid-zero controls and four restored-data cases. The original control function bodies are extracted unchanged and compiled with hardware doubles. [Additional scenario definitions](../../../scripts/component_extra_cases.py) are hashed in the report.

[JUnit](pytest.xml): 19 passed, covering eighteen added controls plus provenance. Fault-stage NaN still becomes 0 C/HIGH (T03); passing restored-data controls do not mark fault handling acceptable. The original two input/UI component findings remain in the baseline suite.

Run a new execution with `python scripts/run_component_checks.py --extended --tcc-root PATH --output runs/new-run/results.json`. The safe runner refuses an existing output and does not replace historical evidence.
