# Portfolio Contract Assertion Failure

Date: 2026-09-25
Tracker: issue #78

## Impact

The first full Python suite for the canonical portfolio index failed one
documentation contract assertion. The implementation validator and all existing
tests remained green; no change had been published.

## Evidence-Based 5-Whys

1. Why did the assertion fail? The test required the exact phrase `does not
   establish preservation or deletion readiness`, while the cutover record used
   `does not replace that inventory, establish preservation or deletion
   readiness`.
2. Why did equivalent prose fail? The recurrence guard intentionally pins an
   explicit non-advancement statement rather than interpreting grammar.
3. Why did the edit miss that exact contract? The prose and test were authored
   in the same increment without first extracting one canonical sentence.
4. Why was no unsupported state published? The full local suite ran before
   commit or push and failed closed.
5. Root cause supported by the single assertion failure: the human-facing
   wording and its mechanical contract were semantically aligned but not
   textually bound.

## Correction And Recurrence Guard

The cutover record now states directly that the public index `does not establish
preservation or deletion readiness`. The existing full-suite test is the
mechanical guard and must pass before publication.
