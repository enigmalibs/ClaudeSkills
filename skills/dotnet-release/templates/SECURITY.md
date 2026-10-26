<!--
  Security policy template. Copy into the target repo as the repository-root SECURITY.md
  (create only if missing — diff against an existing policy, never clobber it) and fill:
    {{PACKAGE_ID}}  NuGet package id / product name  e.g. Enigma.Core
    {{VERSION}}     the released X.Y.Z, for the supported-versions table row (as X.Y.x)

  Offered for any package published publicly. GitHub surfaces this file on the repository's
  Security tab and links it from the advisory form.

  Deliberately NO email address: private vulnerability reporting goes through GitHub, which keeps
  the report private, threaded and attached to the repo. Publishing an address here invites
  unfiltered mail and ages badly. Enable "Private vulnerability reporting" in the repository's
  Settings → Security so step 2 below actually works.
-->
# Security Policy

{{PACKAGE_ID}} is <what it is>, so <why its correctness matters to the applications that depend on
it — the concrete consequence of a defect>. Vulnerability reports are taken seriously and handled
with priority.

## Supported versions

Security fixes are provided for the latest released version. {{PACKAGE_ID}} follows
[Semantic Versioning](https://semver.org/), and users are encouraged to stay current with the
newest release.

| Version     | Supported          |
|-------------|--------------------|
| {{VERSION}} | :white_check_mark: |

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues, discussions, or pull
requests.** Public disclosure before a fix is available puts every user at risk.

Instead, use **GitHub's private vulnerability reporting**:

1. Go to the repository's **Security** tab.
2. Select **Report a vulnerability** to open a private advisory.
3. Include as much detail as you can — the affected version, the component involved, a description
   of the issue, and, where possible, a minimal reproduction and its impact.

This keeps the report private between you and the maintainers while it is triaged and fixed.

## What to expect

- Your report will be acknowledged and triaged as promptly as possible.
- The issue will be investigated and, once confirmed, a fix prepared and released.
- Coordinated disclosure is preferred: please allow a reasonable period for a fix to ship before
  any public discussion of the vulnerability.
- Your contribution will be credited in the resulting advisory unless you ask to remain anonymous.

## Scope

Reports concerning <the implementations, the data handling, and the public API surface of>
{{PACKAGE_ID}} are in scope. Because {{PACKAGE_ID}} builds on <upstream dependency>, issues rooted
in the underlying <upstream dependency> library should also be reported upstream to the
<upstream dependency> project.
