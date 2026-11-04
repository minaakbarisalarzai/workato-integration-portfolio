# Security guidelines

- Do not commit tokens, credentials, customer data, internal configurations, or employer source code.
- Use environment variables or a secret manager for credentials.
- Check all exported recipe packages for sensitive values before publishing.
- Rotate credentials immediately if accidentally exposed.
