# Security Policy

## Supported Versions

The following versions of cubrid-benchmark are currently supported for security updates:

| Version | Status |
|---------|--------|
| 0.1.x   | ✅ Supported |
| < 0.1   | ❌ Not Supported |

Security patches will be applied to supported versions only. Users are strongly encouraged to upgrade to the latest version.

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in cubrid-benchmark, please report it responsibly by emailing:

**Email:** paikend@gmail.com

**Do not** open a public GitHub issue for security vulnerabilities. Responsible disclosure allows us to address the issue before public disclosure.

### Response Timeline

- **48 hours:** Initial acknowledgment of your report
- **7 days:** Security assessment and initial response with remediation plan
- **Ongoing:** Regular updates on progress until resolution

## What Qualifies as a Security Issue

A security issue is any vulnerability that could:

- Allow unauthorized access to test databases
- Enable authentication bypass or privilege escalation
- Permit SQL injection or other code execution attacks
- Compromise confidentiality, integrity, or availability of test systems
- Allow denial of service (DoS) attacks
- Expose sensitive information (credentials, tokens, private data)
- Bypass security controls or safety mechanisms
- Affect the security posture of systems using cubrid-benchmark

Examples include:
- SQL injection vulnerabilities in benchmark queries
- Authentication/authorization flaws in connection setup
- Insecure credential handling in test fixtures
- Cryptographic weaknesses in wire protocol communication
- Input validation bypass in benchmark parameters

## What to Include in Your Report

Please provide the following information with your vulnerability report:

1. **Description:** Clear explanation of the vulnerability and its impact
2. **Affected Versions:** Which version(s) of cubrid-benchmark are vulnerable
3. **Steps to Reproduce:** Detailed instructions to reproduce the issue
4. **Proof of Concept:** Code sample, script, or test case demonstrating the vulnerability
5. **Impact Assessment:** Severity assessment (Critical, High, Medium, Low) and potential consequences
6. **Suggested Fix:** If you have a proposed patch or remediation strategy (optional but helpful)
7. **Your Contact Information:** Name, email, and PGP key (if applicable)

## Security Best Practices for Users

When using cubrid-benchmark, follow these security best practices:

- Always use parameterized queries in benchmark code
- Keep cubrid-benchmark updated to the latest version
- Use secure connection parameters for test databases
- Follow the principle of least privilege for test database credentials
- Regularly audit and monitor test database access logs
- Never hardcode credentials in benchmark code
- Use environment variables or secure credential management systems
- Restrict access to benchmark results and performance data

## Disclosure Policy

Once a security vulnerability is fixed:

1. A security patch will be released
2. The vulnerability will be disclosed in release notes
3. An advisory may be published on GitHub Security Advisories
4. Credit will be given to the reporter (if requested)

We appreciate your responsible disclosure and help in keeping cubrid-benchmark secure.
