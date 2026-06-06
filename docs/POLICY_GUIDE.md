# MXC Security Policy Guide

## Overview

MXC provides policy-driven sandboxing through a JSON configuration schema. This guide explains how to configure security policies effectively.

## Policy Components

### 1. Filesystem Policy

Controls file system access within the sandbox.

```json
{
  "filesystem": {
    "readonlyPaths": ["/usr/bin", "/usr/lib", "/bin", "/lib"],
    "readwritePaths": ["/tmp", "/var/tmp"],
    "deniedPaths": []
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `readonlyPaths` | string[] | Paths that can be read but not modified |
| `readwritePaths` | string[] | Paths that can be read and written |
| `deniedPaths` | string[] | Paths that are completely inaccessible |

**Best Practices:**
- Grant only necessary read permissions
- Use `/tmp` for all temporary files
- Never grant access to `/etc`, `/root`, or system directories

### 2. Network Policy

Controls network access from within the sandbox.

```json
{
  "network": {
    "allowOutbound": false,
    "proxy": null,
    "allowedHosts": [],
    "blockedHosts": []
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `allowOutbound` | boolean | Allow outbound connections |
| `proxy` | string | Proxy server URL (if needed) |
| `allowedHosts` | string[] | Whitelist of allowed host patterns |
| `blockedHosts` | string[] | Blacklist of blocked host patterns |

**Best Practices:**
- Default to `allowOutbound: false`
- Use host whitelisting for required network access
- Avoid proxy unless necessary for corporate networks

### 3. UI Policy

Controls access to user interface resources.

```json
{
  "ui": {
    "clipboard": "deny",
    "display": "deny",
    "gui": "deny"
  }
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `clipboard` | `allow`, `deny` | Access to system clipboard |
| `display` | `allow`, `deny` | Access to display/GUI |
| `gui` | `allow`, `deny` | GUI application access |

**Best Practices:**
- Always deny for untrusted code
- Only allow when absolutely necessary

### 4. Timeout Policy

Limits execution time to prevent resource exhaustion.

```json
{
  "timeoutMs": 30000
}
```

**Recommended Values:**
- Simple commands: 5,000-10,000 ms
- General execution: 30,000 ms
- Complex operations: 60,000-300,000 ms
- Never use unlimited timeout

## Sandbox Backend Selection

MXC supports multiple containment backends with varying security levels:

| Backend | Platform | Security Level | Performance |
|---------|----------|---------------|-------------|
| `processcontainer` | Windows | Medium | High |
| `windows_sandbox` | Windows | High | Medium |
| `bubblewrap` | Linux | High | High |
| `lxc` | Linux | High | Medium |
| `seatbelt` | macOS | High | High |
| `microvm` | All | Very High | Lower |

**Recommendation:** Use the default backend for your platform unless you have specific security requirements.

## Security Checklist

Before deploying MXC in production:

- [ ] Filesystem access is minimal (read-only for system dirs)
- [ ] Network is disabled unless required
- [ ] UI access is denied
- [ ] Timeout is set appropriately
- [ ] Sandbox backend is appropriate for security needs
- [ ] Logging is configured for audit trail
- [ ] Resource limits are in place

## Known Limitations

⚠️ **Current MXC policies may be overly permissive** — this is being addressed in ongoing development. Do not treat MXC as a production-grade security boundary in its current state.

Known issues:
- Denied paths not fully enforced on Windows
- Host filtering not yet supported on Windows
- Some experimental backends may have additional limitations

## Reporting Security Issues

For security issues in MXC itself, please contact Microsoft through their responsible disclosure process at https://github.com/microsoft/mxc/security