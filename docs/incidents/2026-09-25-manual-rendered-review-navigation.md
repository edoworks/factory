# Manual Rendered-Review Navigation

Date: 2026-09-25

Tracker: `edoworks/factory#102`

Status: owner-authorized correction rendered locally, pending hosted verification and integration

## Impact

Factory policy allowed the fixed screenshot utility but required interactive
approval before opening each rendered `edoworks/factory` GitHub page. The owner
then had to open exact links manually when the loaded session could not obtain
that approval. This delayed issue, PR, and exact-revision documentation review,
including the still-pending post-merge review of PR #76's final PRD.

## Evidence-Based 5-Whys

1. Why did rendered review require owner navigation? The only admitted Factory
   page opener was an `ask` command.
2. Why could the screenshot permission not remove that dependency? It captures
   an existing window but does not choose or validate the page shown in it.
3. Why was read-only navigation grouped with interactive operations? The first
   policy bounded the host and repository but did not provide an argv-validating
   transport comparable to the issue and push helpers.
4. Why is changing `ask` to `allow` insufficient? A shell wildcard cannot prove
   that expansion still produces exactly one URL argument or that the default
   browser is Safari or Chrome.
5. Root cause supported by the policy and contract tests: rendered review had a
   capture guard but no repository-owned, executable-pinned navigation guard or
   fresh-session self-service acceptance test.

## Correction

`tools/open_factory_page.js` exposes one structured URL field, rejects unsafe
raw characters and encoded paths, parses the authority, and allowlists only
public Factory repository, issue, PR, commit, action, and revision-bound
document paths. It invokes `/usr/bin/open` with the fixed Chrome bundle and
Guest argument through an argv array and no shell. OpenCode admits the custom tool
directly; no Bash browser command is allowed.

The helper does not click, type, execute browser automation, download, submit
forms, inspect or export credentials, or mutate GitHub. The fixed launch argv
requests a new Chrome Guest instance rather than normal-profile reuse; the
launch receipt does not prove that Chrome honored those arguments. Screenshots
use the existing fixed utility, remain temporary, must confirm Guest mode and
signed-out rendering, must be inspected for private state, and are not repository evidence unless
separately reduced to a public-safe textual review record.

## Recurrence Guard

Pinned Node tests cover accepted review paths, alternate authorities, sibling
and lookalike repositories, settings and branch-relative document paths,
encoded escapes, the one-field tool schema, exact Chrome Guest argv, and launch
failure. Python contract tests require the structured tool permission and reject
every Bash opener. Full suites, Factory doctor, independent trust review, and a
fresh-session autonomous Chrome Guest capture is required before closeout.

## Initial Verification Failure 5-Whys

1. Why did the first full suite fail? The new helper omitted the closing brace
   for a template interpolation, and the PRD contract test did not find a phrase
   split by Markdown wrapping.
2. Why did one edit produce two failures? The implementation and prose were
   patched together before the pinned suite parsed the new module and normalized
   the changed documentation.
3. Why was the prose assertion sensitive to wrapping? It compared raw Markdown
   even though the repository already uses normalized prose for semantic PRD
   contracts.
4. Why did neither failure reach a browser launch? The full Python suite invokes
   the exact pinned Node suite and the PRD contract before integration or use.
5. Root cause supported by the receipts: a syntax edit and a presentation-level
   assertion lacked focused prechecks, while the existing full-suite gate failed
   closed as designed.

The correction closes the template interpolation and normalizes PRD whitespace
before its semantic assertion. The pinned Node import test and full Python suite
remain the mechanical recurrence guards.

## Default-Port Normalization 5-Whys

1. Why did the second full suite fail? The explicit `github.com:443` rejection
   vector was accepted.
2. Why did the port check not reject it? The URL parser normalizes the default
   HTTPS port and reports an empty parsed port.
3. Why did validation lose that distinction? It checked only normalized URL
   fields after parsing.
4. Why does the distinction matter? The contract rejects any caller-supplied
   authority variation instead of deciding that a normalized equivalent is
   authorized.
5. Root cause supported by the failing vector: authority intent was inspected
   only after a lossy normalization step.

The correction requires the raw URL to begin with the exact lowercase
`https://github.com/` origin before parsing and retains the normalized authority
checks afterward. The explicit default-port vector is the recurrence guard.

## Independent Review Trust-Gap 5-Whys

1. Why could the first permission design expose local environment text? A URL
   was carried through a Bash command whose wildcard could match quote-breaking
   parameter expansion before helper validation.
2. Why did a single-quoted example not prevent expansion? OpenCode matches the
   command string but does not prove that the shell parses it as one literal
   argument.
3. Why could nested encoded path text remain ambiguous? The first blob-path
   pattern allowed percent characters after rejecting only selected direct
   encodings.
4. Why did the documentation understate privacy risk? It described helper
   behavior without distinguishing it from Safari's existing profile, cookies,
   page JavaScript, and account chrome.
5. Root cause supported by independent review: structured URL data crossed a
   shell boundary, path validation was not closed over repeated decoding, and
   browser-context behavior was not stated separately from helper authority.

The correction replaces the Bash permission with a one-field custom OpenCode
tool, rejects every percent-bearing path and all but the exact `plain=1` query,
constrains fragments, and launches a new Chrome Guest instance. The tool calls
`/usr/bin/open` directly with `shell: false`; no quoting convention is part of
the authority boundary.

## Bash-Absence Assertion 5-Whys

1. Why did the first post-redesign suite fail? The Bash-absence assertion also
   matched the allowed pinned test filename `open-factory-page.test.mjs`.
2. Why was a test interpreted as a production opener? The assertion searched a
   broad name fragment instead of the removed production script path.
3. Why did the policy itself remain valid? The only matching Bash permission was
   the exact Node suite, while the custom tool permission is outside Bash.
4. Why was the distinction caught before integration? The full policy contract
   enumerates every allowed and interactive Bash pattern.
5. Root cause supported by the failure: a negative test encoded a filename
   convention rather than the authority boundary it intended to guard.

The assertion now rejects the exact removed `/scripts/open-factory-page.mjs`
production path while retaining the checksum-bound test in the pinned suite.

## Custom-Tool Discovery 5-Whys

1. Why would the first structured tool not appear in a fresh session? Its file
   used `.mjs`, while OpenCode 1.18.19 discovers custom tools only as `.js` or
   `.ts`.
2. Why did direct tests still pass? Node imported the explicit `.mjs` path
   without exercising OpenCode's discovery glob.
3. Why would a simple rename still widen authority? The module exported the same
   tool definition by both a named and default export, which would register two
   tool names while policy explicitly allowed only one.
4. Why were those runtime details missing? The first correction validated the
   plugin helper API and filesystem location but not the installed registry's
   extension and export-name behavior.
5. Root cause supported by independent review: module validity was treated as
   equivalent to OpenCode discovery and registration.

The tool now uses the discovered `.js` extension and exports only one tool-shaped
object as default. Named exports are plain validator and launcher functions for
tests. Node tests pin the exact export set, and Python policy tests require the
`.js` file while rejecting the undiscoverable `.mjs` path.

## Isolated Review Hardening

The isolated branch review found three non-material contract weaknesses. First,
the URL parser can normalize encoded dot segments before a parsed-path percent
check. Raw input now rejects every percent character before parsing, with a
direct encoded-dot-segment vector. Second, seven-character commit prefixes are
not durable exact revisions; commit, blob, and tree paths now require full
40-character object IDs, with short commit and blob vectors. Third, the earlier
negative policy assertion covered only the removed wildcard and former helper
path; the recurrence guard now rejects any allowed or interactive Bash command
that starts with `open` or invokes `/usr/bin/open` or `osascript`. These changes
do not widen the accepted host, repository, operation, or browser authority.

## Isolated-Worktree Verification 5-Whys

1. Why did the pinned full suite fail in the issue #102 worktree? The push-helper
   test required the checkout path to end in `/factory`.
2. Why was a valid isolated checkout rejected? Its repository root is named
   `factory-issue102`, while the helper correctly derives that root from its own
   module location.
3. Why did the assertion encode the basename? The original test approximated
   the expected working directory with a naming convention instead of deriving
   the same invariant independently.
4. Why did this not indicate a transport defect? The captured push argv,
   environment cleanup, identity check, remote, and refspec remained unchanged;
   only the test's path matcher failed.
5. Root cause supported by the isolated receipt: the recurrence guard coupled
   repository identity to one checkout basename and therefore did not support
   the repository's isolated-worktree verification requirement.

The test now derives the exact expected repository root from the test module's
location and compares it to the helper's captured working directory. This keeps
the root-pinning assertion while allowing independently named worktrees.

## Authenticated-Profile Review 5-Whys

1. Why did final trust review reject the existing launch argv? Opening the
   normal Safari profile could send existing GitHub session cookies.
2. Why did that exceed the frozen issue authority? Issue #102 permits public
   Factory pages but explicitly excludes credentials and authenticated browser
   actions.
3. Why did privacy review not close the gap? Reviewing a screenshot can detect
   private account chrome after navigation, but it cannot prevent the browser
   request from carrying an existing authenticated session.
4. Why was the normal profile initially retained? The correction separated the
   helper's lack of credential APIs from Safari's ambient profile behavior
   instead of enforcing the boundary in launch argv.
5. Root cause supported by independent review: the transport constrained the
   destination but did not isolate ambient browser authentication.

The first attempted correction requested a new Safari instance with a fixed
`-Private` argument before the validated URL. Fresh-session capture proved that
the installed Safari ignored that argument, reused authenticated state, and
displayed account chrome, so the acceptance gate failed closed.

Apple documents Private Browsing as a UI operation rather than a supported
launch argument. The owner provenance for issue #102 permits Chrome or Safari,
and Chrome is installed. The launcher therefore uses a new Chrome Guest instance
with fixed argv. The exact argv test is the mechanical guard; fresh-session
capture must confirm Guest mode and signed-out rendering before integration.

## Browser Authority Reconciliation

The canonical issue body and a later issue comment retained Safari-specific
acceptance language after the Safari private-mode launch attempt failed closed.
Independent isolated review correctly treated that later comment as controlling
and rejected Chrome integration without explicit reconciliation. On 2026-09-25,
the owner explicitly authorized the recommended Chrome Guest option for issue
#102, superseding the Safari-only comment while retaining the frozen public
`edoworks/factory` URL, no-interaction, no-credential-access, no-GitHub-mutation,
and temporary-capture boundaries. The tracked authority comment records that
decision verbatim for canonical issue readback before integration.

The mechanical recurrence guard is both process and code based: browser changes
must have an explicit canonical authority record, the launcher pins Chrome Guest
argv without a shell, its receipt reports requested rather than observed mode,
and fresh-session screenshots remain the acceptance evidence that Chrome honored
the isolation request.

## Fresh-Session Rendered Acceptance

After the authority reconciliation was posted to canonical issue #102, the
fresh Factory session discovered the admitted `open_factory_page` tool and
opened issue #102, PR #76, and PR #76's exact 40-character PRD revision without
a Bash command or approval prompt. Temporary Chrome captures showed the Guest
badge, GitHub's signed-out `Sign in` and `Sign up` controls, the expected public
`edoworks/factory` pages, and no normal-profile account chrome or private content.

The exact `97e17b0883c6fdacd6ab2fd85ad3dfc70a7f8719` PRD rendered as 159 lines in
GitHub Preview mode. Bounded fragment navigation reviewed the top, Entry
Contract, Cutover States, and Acceptance sections. The rendered document had no
overlap, clipping, unreadable wrapping, or later-state overclaim. This is a
post-merge review of PR #76 and is not claimed to have preceded that merge.
Screenshots remained temporary and were not added to repository evidence.

## Push-Revision Transcription 5-Whys

1. Why did the first corrected-head push fail? The supplied expected commit did
   not equal `HEAD`.
2. Why was the expected commit wrong? A full identifier was manually completed
   from the abbreviated commit output instead of read from Git.
3. Why did no incorrect revision reach GitHub? The repository-owned push helper
   resolves `HEAD^{commit}` and rejects a mismatch before transport.
4. Why was manual completion unnecessary? `git show --format=%H HEAD` provides
   the exact required identifier under the admitted read-only command policy.
5. Root cause supported by the helper receipt: a deterministic identifier was
   transcribed rather than consumed from its authoritative Git output.

The failed push changed no remote state. The recurrence guard is to read the
full `HEAD` identifier immediately before every guarded push and pass that exact
value unchanged; the helper's mismatch check remains the mechanical backstop.
