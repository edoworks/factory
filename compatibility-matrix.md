# Compatibility Matrix

Edoworks Factory is tested against the following versions:

| Component | Supported versions | Notes |
|---|---|---|
| macOS | 26.x | Current and previous major |
| Xcode | 26.x | Current and previous major |
| Swift | 6.x | Bundled with Xcode |
| iOS (deployment target) | 18.0+ | Set in template project.yml |
| iPadOS (deployment target) | 18.0+ | Same as iOS |
| Git | 2.x | Any recent version |
| xcodegen | 2.x+ | Required for factory init |

## Verification

The factory is verified on:
- macOS 26.6.2 (Build 25G83)
- Xcode 26.6 (Build 17F113)
- Swift 6.3.3
- xcodegen (latest via Homebrew)

Older versions may work but are not guaranteed. The `factory doctor` command
checks for compatibility at runtime.