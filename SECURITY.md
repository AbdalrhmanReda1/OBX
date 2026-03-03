# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅        |

## Privacy Guarantees

OBX is designed with privacy as a first principle:

- **No telemetry**: OBX never sends data to external servers
- **No network calls**: All intelligence is computed locally
- **Sensitive data redaction**: Keys containing `password`, `token`, `secret`, `key`, or `auth` are automatically redacted in production mode
- **No persistent storage**: Session data exists only in memory during runtime

## Reporting a Vulnerability

To report a security vulnerability, contact:

- GitHub: [@AbdalrhmanReda1](https://github.com/AbdalrhmanReda1)
- Telegram: [@o7_4l](https://t.me/o7_4l)

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

We will respond within 48 hours and aim to release a patch within 7 days for critical issues.

Do not open public GitHub issues for security vulnerabilities.
