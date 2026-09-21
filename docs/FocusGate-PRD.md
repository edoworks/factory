# FocusGate v0 PRD

Date: 2026-09-20
Status: OWNER APPROVED FOR REFERENCE APP 1
Factory: Edoworks Factory v0.1.0-rc1
Tracking: https://github.com/edoworks/factory/issues/8

## Product Premise

FocusGate protects the founder's attention when a new idea appears. It makes
the idea safe to forget, then returns the founder to the one activity already
chosen as important.

The first release is an offline iPhone and iPad app. It proves one loop:

```text
see NOW -> capture idea -> park locally -> confirm -> resume NOW
```

FocusGate is not a backlog manager, research agent, or general productivity
platform.

## Customer Zero

The founder is the only v0 customer. The observed pain is priority drift: a new
idea can displace an already approved outcome before the idea is safely
preserved.

Protected priorities, including family presence, are not rewards deferred until
later business success. The app optimizes for reduced cognitive load and a
trustworthy return to the chosen activity.

## Owner-Visible Acceptance Sentence

On an iPhone or iPad, the founder can see the current Project, Outcome, and
Next Action; enter an idea; park it locally; receive a brief confirmation; and
return to the same unchanged NOW context without seeing a backlog or research
feed.

## Product Laws

### NOW Authority

- NOW is `Project -> Outcome -> Next Action`.
- The app never changes Project or Outcome automatically.
- v0 never advances Next Action automatically.
- Capturing or reviewing an idea never changes NOW.

### Park Before Resume

- An idea must be durably persisted before success is shown.
- A parked item has an immutable creation date and explicit `PARKED` state.
- A failed save must be visible and must not claim success.

### No Interruption

- No notifications, badges, sounds, scheduled reminders, email, or background
  work.
- Confirmation is allowed only because the founder initiated capture.
- The default screen exposes no backlog count or recommendation.

### Local and Honest

- v0 has no network, accounts, cloud sync, analytics, or telemetry.
- Deleting the app may delete its data; the UI and release notes must not imply
  cloud backup.
- The app does not infer that attention returned. It records only completed
  interactions.

## v0 Scope

### NOW Screen

- Shows one Project, one approved Outcome, and one concrete Next Action.
- Offers unobtrusive controls to capture an idea, edit NOW, or open deliberate
  review.
- Shows no parked-item count.

### Capture

- Accepts a short unstructured text idea.
- Rejects empty input.
- Persists the idea locally with ID, creation date, and `PARKED` state.
- Shows `Parked. Back to <Next Action>.` only after persistence succeeds.
- Returns to NOW without opening review.

### Deliberate Review

- Lists all parked ideas newest first.
- Shows idea text, creation date, and PARKED state.
- Allows local deletion with confirmation.
- Does not rank, recommend, promote, research, or implement ideas.

### NOW Editing

- The founder can explicitly edit Project, Outcome, and Next Action.
- Empty values cannot replace the current values.
- Changes persist locally across restart.

## Explicitly Deferred

- GitHub issue creation or synchronization
- Local-to-GitHub retry queues
- ChatGPT history import or mining
- Webpage, issue, or document import
- Deduplication beyond exact local identity
- Investigation agents or research budgets
- Weekly review generation or ranking
- Automatic Next Action advancement
- Notifications, widgets, share extensions, shortcuts, or background tasks
- Accounts, sync, analytics, telemetry, purchases, or subscriptions

Deferred behavior is not implied by the FocusGate name and requires a new
owner-approved issue before implementation.

## Data Model

### NOW

- `project: String`
- `outcome: String`
- `nextAction: String`

### Parked Idea

- `id: UUID`
- `text: String`
- `createdAt: Date`
- `state: PARKED`

All data is app-local. No raw data leaves the device.

## Acceptance Criteria

1. Fresh launch presents editable seed NOW values without onboarding.
2. A non-empty idea can be parked and is present after app relaunch.
3. Empty or whitespace-only ideas cannot be parked.
4. Capture does not alter Project, Outcome, or Next Action.
5. Confirmation names the same Next Action that was visible before capture.
6. Confirmation does not navigate to review.
7. Review is reachable only through a deliberate user action.
8. Review contains every locally parked idea and no fabricated entries.
9. Deletion removes only the selected idea after confirmation.
10. NOW edits persist across relaunch and require explicit user action.
11. No notification entitlement, network client, analytics SDK, account flow,
    or background mode is present.
12. The app builds and tests on iPhone and iPad through the downloaded factory
    release.

## Evidence Gates

- Persistence and authority invariants: unit tests
- Capture, confirmation, review, deletion, and NOW editing: UI tests
- iPhone and iPad layouts: simulator builds and rendered review
- Persistence across process restart: UI test plus physical-device smoke test
- Privacy and no-interruption claims: source/entitlement inspection
- Archive and Apple processing: factory release lane, human-authorized

Simulated evidence must remain separate from physical-device and Apple
processing evidence.

## Success Measures

The first dogfood run records, without inferring mental state:

- whether the idea was retrievable later;
- wall-clock time from opening capture to restored NOW;
- whether NOW changed during capture;
- whether any unsolicited interruption occurred;
- founder-reported trust during deliberate review.

Initial continue gate: at least four of five real captures persist correctly,
restore unchanged NOW within five minutes, and create no interruption.

## Stop Rules

Stop or re-scope if:

- capture commonly takes longer than writing the idea elsewhere;
- local persistence loses or duplicates ideas;
- the review surface becomes a source of unsolicited attention;
- v0 requires network access or background execution;
- the app grows into ranking, research, or factory orchestration before the
  capture loop is proven;
- the founder reports that the main failure is investigation impulse rather
  than capture friction.

## App Review Readiness

- Distinctive utility: protects an approved NOW context rather than providing a
  generic notes list.
- No account or reviewer credentials required.
- Privacy manifest declares no tracking or collected data.
- No special permission purpose strings are required.
- iPhone and iPad screenshots must demonstrate NOW, capture confirmation, and
  deliberate review.
- Accessibility evidence must cover VoiceOver, Dynamic Type, and Reduce Motion.

## Self-Review

- It could still distract through easy access to review; review is secondary
  and hidden from the default screen.
- It could lose ideas if the app is deleted; v0 states local-only limitations
  and does not claim backup.
- It could exceed authority by changing NOW; automatic changes are prohibited
  and tested.
- GitHub sync, history mining, ranking, research, notifications, and automation
  are deliberately omitted.
