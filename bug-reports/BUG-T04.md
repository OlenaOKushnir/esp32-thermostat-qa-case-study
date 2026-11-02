# BUG-T04 — Release rebound advances two modes

**OPEN · Severity Medium · Priority High**. RISK-T04. Environment: separate identified Wokwi input image, GPIO32→27 stimulus; defaults VIEW/20/25. [Identity and raw run](../evidence/bugs/input-feedback/README.md).

## Steps tovReproduce

1. Build/select `validation/device/wokwi.toml`.
2. Run `python -m pytest validation/tests/live -v -s --run-dir runs/new-input`.
3. After LIVE CAPTURE CONNECTED, restart. The controller generates the clean-hold control, then a 1100 ms hold followed by HIGH 5 ms / LOW 20 ms release rebound.

**Expected:** one intended press/release sequence leaves SET LOWER (mode 1).

**Actual:** clean long hold leaves mode 1; release rebound leaves SET UPPER (mode 2). The live result is an ordinary FAIL, not skipped/xfail. [Raw Serial](../evidence/bugs/input-feedback/serial.log), [JUnit](../evidence/bugs/input-feedback/pytest.xml).

Independent [component case](../evidence/components/baseline/results.json), `long_press_release_bounce`, uses a 1 ms rebound and also produces mode 2. Both levels reproduce the finding; the waveforms are explicitly different.

## Cause, impact and disposition

Any HIGH sample clears `swPressed`. After a long hold, time since the preceding accepted press exceeds 200 ms, so a LOW rebound is accepted again. A user can unintentionally enter the wrong threshold-edit mode.

Suggested fix: debounce stable press and release states, retaining one action while held. Retest clean holds, initial/release bounce, repeated deliberate presses and rapid inputs. Deliberate 350/350 ms presses and short-pulse state controls already pass; they do not override the rebound failure. No production mode or threshold is assigned by the stimulus controller; physical switch statistics are outside scope.
