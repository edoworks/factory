# Security Policy

## Reporting a Vulnerability

Report security vulnerabilities by opening a private security advisory on
GitHub: https://github.com/edoworks/factory/security/advisories/new

Do not open a public issue for security vulnerabilities.

## Response Time

Best-effort. No SLA. We will acknowledge receipt and work with you to assess
and address the issue.

## Scope

This policy covers the Edoworks Factory codebase, lifecycle scripts, templates,
and validators. It does not cover apps produced using the factory — each app
has its own security posture.

## Security Posture

- The factory collects no telemetry and transmits no data
- The factory does not store or access Apple credentials
- All credential use is human-authorized and performed outside the factory
- The factory's lifecycle scripts run locally on the developer's machine
- Generated code executes in the developer's Xcode sandbox