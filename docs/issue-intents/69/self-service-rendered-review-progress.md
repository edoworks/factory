Local issue #102 update (2026-09-25): the first Bash-carried URL design was
rejected by independent trust review because shell expansion could precede URL
validation. The corrected implementation is a structured OpenCode custom tool
with one URL field, no Bash browser permission, fixed Chrome Guest argv, strict
public Factory path/query/fragment validation, and no reuse of the normal Chrome
session. Follow-up review corrected the OpenCode 1.18.19 discovery extension and
duplicate tool-shaped export risk; final independent review found no material
issue. The corrected head passes 81 Python tests and 20 pinned Node tests,
`git diff --check`, and launch-ready Factory doctor with valid policy and no
routing contradiction. The currently loaded session retained the old permission
map and refused its interactive opener, as expected because OpenCode does not
hot-reload configuration. A fresh `bin/factory-dev launch`, autonomous issue/PR
opening, bounded Chrome screenshots, hosted checks, integration, and closeout
remain pending. No final rendered-review claim is made from this session.
