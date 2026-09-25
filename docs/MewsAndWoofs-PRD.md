# Mews & Woofs MVP PRD

Date: 2026-09-24
Status: ACTIVE, IMPLEMENTATION BOUNDED BY CHILD ISSUES
Parent: [Reference App 2](https://github.com/edoworks/factory/issues/13)
Factory authority: `edoworks/factory`

## Product Promise

Mews & Woofs turns one short pet sound or video into an editable, shareable
piece of playful fiction:

`capture -> optional context -> imagined response -> thought bubble -> preview -> save or share`

The response is entertainment inspired by the recording and context the person
provides. It is not animal-language translation, emotional or behavioral
inference, veterinary guidance, or proof that a selected context is true.

## Product Value

The MVP is a creation tool, not a detector. Its repeat-use hypothesis is that
people enjoy turning fleeting pet moments into distinctive keepsakes with
enough contextual humor and controlled variation to create another one.

Commercial precedent reduces interaction-learning cost; it does not validate
this hypothesis. Repeat use and willingness to pay require separate evidence.

## Core Journey

1. The person starts a short video-with-audio capture, or chooses audio-only.
2. Capture stops explicitly or at the bounded limit.
3. Lightweight features are computed once after capture.
4. The person may select one context badge or skip the step.
5. A deterministic content selector returns one edited response.
6. The response appears in a manually positioned thought bubble.
7. The person can drag, resize, reset, or use accessible position and size controls.
8. Preview renders the same composition specification used by export.
9. The person explicitly saves to Photos or opens the system share sheet.

The bubble is fixed relative to the media frame. It does not track a pet.

## Product Laws

### Entertainment Law

- Use `imagined`, `playful`, or equivalent framing at first value and in About.
- Never claim translation, reliable thoughts, emotions, needs, intent, health,
  welfare, diagnosis, or automatic context recognition.
- Silence and unusably short input produce an honest retry state, not an
  invented interpretation.

### Local Moment Law

- Core capture, response selection, editing, preview, and export work locally.
- No account, analytics SDK, cloud inference, media upload, subscription, or
  paid runtime dependency belongs in the MVP.
- Temporary media exists only as needed for the active draft and export.
- Explicitly saved creations are not deleted by temporary-file cleanup.

### Coherent Artifact Law

- Preview and export share normalized geometry, crop, orientation, text, timing,
  and audio inputs.
- Speech heard in preview is included in export only when the exact rendered
  audio asset is mixed into the export.
- Export failure or cancellation preserves the editable draft.

### Accessible Creation Law

- Recording never requires press-and-hold.
- Emoji or symbols never serve as the only context label.
- Bubble drag and pinch have button-based position and size alternatives.
- VoiceOver, Dynamic Type, sufficient contrast, and Reduce Motion are verified
  rather than inferred from SwiftUI use.

## Content Model

### Context

Context is optional user-provided metadata, not recognized ground truth.

| Stable ID | Display label | Meaning |
|---|---|---|
| `greeting` | Saying hello | The person believes this may be a greeting moment. |
| `foodNearby` | Food nearby | Food is visibly or situationally nearby. |
| `playtime` | Playtime | The moment occurred during play. |
| `doorOrWindow` | Door or window | The pet is near a door or window. |
| `notSure` | Not sure | No specific context is supplied. |

### Response Inputs

- optional context ID;
- media kind;
- bounded duration band;
- relative loudness band;
- silence/activity band;
- explicit species when supplied;
- caller-controlled seed.

These inputs influence entertainment copy. They are not animal-state evidence.

### Response Record

Every response has a stable ID, eligible contexts, eligible activity bands,
display text, optional spoken text, and accessibility text. Display strings are
never used as identifiers. Identical controlled inputs and seed must select the
same response ID. A local recent-ID window may prevent immediate repetition
without changing seeded test behavior.

The initial reviewed library remains deliberately small. Content quality and
context fit outrank phrase count.

## Speech Decision

Do not bundle a custom or prerecorded speech model. Render system speech to a
temporary audio asset before preview, then use that exact asset in preview and
export. If rendering or a suitable voice is unavailable, retain a complete
text-only experience. If system speech does not meet the character-quality bar
in review, ship text-only rather than adding an unmaintained voice catalog.

## Capture Decision

- Default to explicit short video-with-audio capture.
- Offer audio-only capture when camera access is declined, unavailable, or not
  wanted.
- Perform no continuous frequency scan or continuous semantic inference.
- Compute duration, relative loudness, silence/activity, and simple temporal
  features once after stop.
- Stop and transition the audio session before response speech or replay so app
  output cannot become the next input.

Automated cat/dog classification is deferred. The experience must remain useful
without it.

## Composition Decision

Use one clip, one response bubble, and one optional spoken response. There is no
timeline, keyframing, tracking, effect catalog, or destination-specific editor.
Audio-only captures export as an original animated or still visual card with the
captured audio and optional rendered speech.

## Platform And Privacy

- iPhone and iPad, iOS/iPadOS 18 or later, Swift 6.
- Camera and microphone permissions are requested only from the relevant action.
- Photos add permission is requested only from Save.
- Import, if later needed, uses the system Photos picker.
- Sharing uses the native share presentation.
- No third-party runtime dependency is required.

## Proposed Internal Budgets

These are project targets, not platform limits or industry facts.

| Metric | Budget |
|---|---:|
| Compressed App Store download estimate | under 100 MB for every measured variant |
| Capture length | 2-15 seconds |
| Post-capture selection latency | under 750 ms, excluding speech rendering |
| Speech preparation | under 2 seconds |
| Export duration | at most 2x clip duration on representative hardware |
| Peak temporary storage | source media x3 plus 25 MB |
| Immediate response repetition | none within previous three eligible responses |
| Bubble bounds | fully inside exported frame |

Download estimates come from Xcode's all-compatible-variant
`App Thinning Size Report.txt`. App Store Connect provides final processed
variant sizes when an authorized uploaded build exists. `.app`, `.xcarchive`,
and upload `.ipa` sizes are not substitutes.

## Increment Boundaries

### Issue 63: Contract And Fixture Slice

- Canonical PRD and reference decision record.
- Fixture media surface.
- Optional context.
- Deterministic response selection.
- Bubble drag, resize, reset, and accessible alternatives.
- Preview and rendered iPhone/iPad evidence.

### Issue 64: Bounded Hardware Capture

- Camera, microphone, audio session, interruption, cancellation, and lifecycle.
- Audio-only fallback and one-shot post-capture metrics.
- Draft and temporary-file ownership.

### Issue 65: Speech And Export

- Rendered system speech with text fallback.
- Shared preview/export composition specification.
- Photos save and native share.

### Issue 66: Qualification

- Full regression, size, accessibility, performance, physical-device, visual,
  and product-value evidence matrix.

## Acceptance Matrix

| Gate | Required evidence |
|---|---|
| Build and regression | Clean-checkout build and all relevant tests |
| Size | App Thinning report by represented variant; App Store sizes only if available |
| Determinism | Controlled input/seed tests and valid content/audio IDs |
| Capture | Start, stop, cancel, silence, short clip, interruption, denial, repeated use |
| Editing | Drag, resize, reset, wrapping, bounds, orientation, accessible controls |
| Export | Preview agreement, audio mix, failure, cancellation, draft preservation |
| Performance | Configuration, device, OS, latency, frame behavior, peak memory, export duration, temp growth |
| Accessibility | VoiceOver, context, recording and editing alternatives, legibility, Reduce Motion |
| Product value | Moderated protocol; no invented feedback |

Every result is `PASS`, `FAIL`, or `NOT VERIFIED`. Simulator evidence is never
reported as physical-device evidence. A working build does not prove usability,
repeat use, commercial demand, or willingness to pay.

Hosted iPhone and iPad verification remains independently bounded and fail
closed. Issue #99 owns the CI evidence correction after PR #98 run `36184422124`
reached the former iPhone step bound while tests were still passing and then
failed to upload the live result directory. Hosted evidence must be packaged as
an immutable archive before upload; a missing or unpackageable archive fails the
job and cannot be reported as product qualification evidence.

## Usability Protocol

Give a representative participant a device without explaining the controls.
Ask them to create one fixture or live pet moment, then ask:

1. What does the response claim to know?
2. Was context optional, and did the app infer it?
3. Can you move, resize, and reset the bubble?
4. Can you reach preview and sharing without instruction?
5. Would a different moment plausibly produce enough variation to try again?

Record observed behavior and verbatim feedback. Do not infer retention or
willingness to pay from task completion.

## Stop Rules

Stop or materially re-scope when users understand the experience as literal
translation, cannot reach first value without instruction, context adds more
friction than value, fixed bubbles routinely fail on real clips, preview and
export cannot be made coherent, responses feel repetitive after a small sample,
or reliable operation requires cloud processing or continuous surveillance.

## Authority

The current owner instruction authorizes local design, implementation, tests,
issue tracking, and ordinary reviewed integration in `edoworks/factory`.
`Mews & Woofs` remains an internal product title. Public identity, creation of a
dedicated public repository, household-media fixtures, physical-device or
real-pet sessions, Apple credentials, upload, submission, release, pricing, and
public claims remain separately gated.

The single-factory repository strategy does not qualify this product, complete
issues 64-66, or authorize physical-device, household-media, Apple, release, or
commercial claims.
