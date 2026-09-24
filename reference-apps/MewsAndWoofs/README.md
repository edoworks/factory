# Mews & Woofs Reference App

Internal Reference App 2 incubation surface. The canonical product contract is
[`docs/MewsAndWoofs-PRD.md`](../../docs/MewsAndWoofs-PRD.md).

This first increment uses a deterministic built-in moment. It requests no camera,
microphone, or Photos permission and does not save or share media.

## Generate And Test

```bash
xcodegen generate --spec reference-apps/MewsAndWoofs/project.yml
xcodebuild test \
  -project reference-apps/MewsAndWoofs/MewsAndWoofs.xcodeproj \
  -scheme MewsAndWoofs \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro,OS=26.5'
```
