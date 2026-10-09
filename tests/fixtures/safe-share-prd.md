# Safe Share synthetic evidence example

A worked candidate declaration, not product implementation or permission to start
one. The owner-held evidence ZIP was rehashed during the 2026-10-09 assessment.
Its recorded results report 11/11 checks on one synthetic unrotated one-page PDF,
using PDFKit on an iPhone 17 Pro simulator running iOS 26.5. Those tests were not
rerun during the factory assessment. PDFKit was both renderer and text extractor.
The library evidence is intentionally not copied into this public-bound fixture.
No cloud export dependency or native source is adopted.

## Factory reuse and contribution

```json
{
  "schema_version": 1,
  "capabilities": [{
    "id": "synthetic-native-evidence-handoff",
    "status": "candidate",
    "source": {
      "reference": "Owner-held safe-share-ios-simulator-evidence.zip",
      "revision": "2026-10-09 synthetic validation package",
      "license": null,
      "attribution": null
    },
    "artifact_sha256": "6f8510ff9ca45716c9e466aed389bde4651225dc00ddb6e9fcea5f91cf904484",
    "scope": "Reported 11-check single-page synthetic iOS Simulator PDFKit experiment",
    "limitations": [
      "Receipt is not supplied here; this declaration cannot be promoted to verified",
      "No physical-device, independent-parser, adversarial-PDF or security validation",
      "No customer demand, delivery, general-PDF or accessibility-preservation evidence",
      "Raster output loses searchable text and semantic accessibility",
      "One failed disposable simulator cleanup remains unresolved; browser strict-focus limitation remains",
      "Cloud export dependencies are license-constrained experimental resources and are not adopted"
    ],
    "consumer": null,
    "interface": null,
    "evidence": null,
    "gap": "Identity and limitations must travel with a reported native test result; reusable native consumer remains unverified",
    "contribution": {
      "change": "Use this case to test the shared evidence gate; stop PDF-platform or native-runner adoption until a real consumer and license review exist",
      "behavior_test": "Candidate passes with explicit unknowns; changing only status to verified or reused fails"
    }
  }]
}
```

Separate browser artifact SHA-256:
`6666834c4dfe3ae7603a8f58e46e8fed51feb9c1deadadd88edcf4e6e4b4d5df`.
Its postpatch tests do not retroactively validate a previous artifact, nor does
this hash make browser evidence native evidence.
