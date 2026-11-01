# Release Decision — Thermostat

Updated 2026-11-01 | **QA recommendation: NO-GO** | Educational simulation assessment.

## Decision basis

Critical RISK-T01 remains open. Invalid DHT data is converted to 0 C and can create a new heat request. This fails the proposed RTH-07 fault oracle. The [unmodified main-image capture](evidence/live-2026-11-01/README.md) and [complete live campaign](evidence/campaign-live-2026-11-01/README.md) reproduce T03. The follow-up correlates the settled fault request with COM-NO closure in the model; no physical heater or overheating consequence is claimed.

T04 release bounce and T05 delayed mode feedback are also open, with [separate instrumented device evidence](evidence/device-inputs-2026-11-01-run3/README.md). Matching completed feedback took 1024 device ms versus the proposed 500 ms budget. These are three independent findings, separate from fixed startup/layout integration history. Product behavior was not altered to produce a report count.

All planned simulation categories have executed evidence. The live campaign and follow-up total **25 cases, 23 passed/2 T03 failures, no errors or skips**. Encoder limits, deliberate inputs, reset, twenty hysteresis cycles, restored-data recovery and settled polarity controls pass. The two campaign failures concern the same critical fault behavior; passing controls do not override their impact. Exact debounce decision boundaries additionally pass three controlled-clock component scenarios.

Twenty cycles give 80 correct states, 40 request edges and a maximum matching temperature-sample response of 1890 device ms. Device clocks establish timing; post-Serial MODE logs are not treated as exact debounce-decision timestamps. Warm-reset defaults and configured GPIO LOW pass. Early pre-initialization levels and physical rail/load safety remain explicitly qualified.

## Conditions to reconsider

1. Fix invalid-sensor handling and misleading zero display; address T04/T05 against the explicit case-study input/UI oracles.
2. Build an identified new candidate and rerun the affected risk suites plus the complete regression set. Retain the present failure history.
3. Evaluate fresh results against all product exit criteria. A positive recommendation requires the mandatory acceptance failures to be resolved.
4. Scope and execute a separate hardware qualification before physical-product claims, with approved operating, safety and persistence requirements.

## Scope of authority

This is a QA recommendation for a learning model, not an industrial release authorization. Proposed fault/timing policies are explicit assessment assumptions; external product approval and residual risk acceptance are not claimed. GPIO/protocol/contact measurements are simulated. The unmodified main build and additive validation images are separately identified in the [build manifest](evidence/tested-build.json) and [variant identities](evidence/validation-builds.json).

[Master Test Plan](master-test-plan.md) · [Acceptance Criteria](acceptance-criteria.md) · [QA Conclusion](qa-conclusion.md) · [Evidence](evidence/README.md)
