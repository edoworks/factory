Issue #102 browser authority reconciliation (2026-09-25)

The owner explicitly authorizes Chrome Guest for issue #102, superseding the
2026-09-25 Safari-only scope comment. Safari's unsupported private-mode launch
argument reused authenticated profile state and therefore could not satisfy the
existing no-credential boundary. The approved correction may request one new
Chrome Guest instance through fixed argv for one validated public
`edoworks/factory` review URL.

All other boundaries remain unchanged: no authentication, browser automation,
page interaction, downloads, credential inspection, GitHub mutation, arbitrary
URLs, persistent captures, provider or route changes, product or release
changes, storage-tolerance changes, or deletion authority. A successful launcher
receipt proves only that LaunchServices accepted the request. Fresh-session
screenshots must separately confirm Guest mode, signed-out rendering, no
normal-profile reuse, and no private account chrome before integration.
