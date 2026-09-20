# Contributing to Edoworks Factory

## How to Contribute

1. Open an issue describing the problem or improvement
2. Fork the repository and create a feature branch
3. Make your changes with tests
4. Open a pull request referencing the issue

## Support

Best-effort community support via GitHub issues. No SLA. No guaranteed
response time.

## Code Style

- Shell scripts: `set -euo pipefail`, clear error messages, exit codes
- Swift: Follow Apple's Swift API Design Guidelines
- Python: Follow PEP 8

## Testing

All changes must pass the CI policy gate before merging. Run locally:

```bash
factory doctor && factory verify
```

## License

By contributing, you agree that your contributions are licensed under the MIT
license. The "edoworks" name and logo are trademarks of the owner and are not
covered by the MIT license.