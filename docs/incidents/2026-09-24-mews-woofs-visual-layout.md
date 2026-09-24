# Mews & Woofs Visual Layout Failure

Date: 2026-09-24
Issue: [#63](https://github.com/edoworks/factory/issues/63)
Status: correction verified locally; merged verification pending

## Observation

The final iPhone and iPad XCTest suites passed, but screenshot review failed.
The iPhone editor exceeded the viewport and clipped headings and controls. On
both devices the thought bubble collapsed into a thin strip, clipping its text.

## Root-Cause Analysis

1. Important content was visually clipped despite semantic UI tests passing.
2. The mobile root expanded beyond the viewport because a single-line header
   and seven-button control row imposed excessive intrinsic width.
3. The thought bubble collapsed because its shape had a width but no explicit
   height and inherited only the overlay text's compressed layout.
4. UI tests verified existence and actions but did not assert rendered geometry
   or text containment.
5. The root cause was treating semantic operability as sufficient evidence for
   responsive visual composition.

Boundary review found a related edge state after the default screenshots passed:
the center-point clamp did not account for bubble scale, so a maximally scaled
bubble could cross the media edge. The immediate cause was fixed center limits;
the deeper cause was testing center coordinates rather than the composed
rectangle. Position bounds are now derived from the bubble's maximum normalized
width and height at its current scale, resize re-clamps position, and unit tests
exercise a moved bubble at maximum scale.

## Corrections

- Stack the mobile header vertically.
- Wrap accessible bubble controls into a four-column grid.
- Give the thought bubble a deliberate composition height.
- Clamp movement and resize using scale-aware bubble extents.
- Top-align regular-width editor and preview surfaces rather than centering
  phone-shaped content in unused vertical space.
- Repeat iPhone and iPad screenshot extraction and independent vision review.

## Recurrence Guard

The UI suite retains editor and preview screenshots for both form factors.
Issue #63 cannot close unless visual review reports no clipping, fully readable
bubble text, and intentional device fit in addition to passing UI tests.

## Evidence

Fresh editor and preview screenshots from both passing all-target suites were
reviewed independently on 2026-09-24. All four surfaces passed the render,
clipping, bubble readability, hierarchy, premise, contrast, device-fit, and
originality checks. The iPhone and iPad suites each passed 11 of 11 tests,
including the accessibility text-size journey.
