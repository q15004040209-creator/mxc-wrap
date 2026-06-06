# MXC-Wrap Quick Start Guide

## Overview

MXC-Wrap provides production-ready wrappers for Microsoft MXC (eXecution Container), enabling safe execution of untrusted code across Windows, Linux, and macOS.

## Prerequisites

- Node.js ≥ 18 (for TypeScript SDK)
- Rust (for building MXC native binaries)
- Python 3.8+ (for Python examples)

## Installation

### 1. Install MXC Native Binary

Follow the [MXC build instructions](https://github.com/microsoft/mxc) for your platform:

**Windows:**
```bash
build.bat
```

**Linux:**
```bash
./build.sh
```

**macOS:**
```bash
./build-mac.sh
```

### 2. Install TypeScript SDK

```bash
npm install @microsoft/mxc-sdk
```

## Quick Examples

### TypeScript (One-Shot Sandbox)

```typescript
import { spawnSandboxFromConfig, createConfigFromPolicy } from '@microsoft/mxc-sdk';

const config = createConfigFromPolicy({
  version: '0.6.0-alpha',
  filesystem: { readonlyPaths: ['/usr'], readwritePaths: ['/tmp'] },
  network: { allowOutbound: false },
  timeoutMs: 30_000,
});

config.process!.commandLine = 'python -c "print(1+1)"';

const child = spawnSandboxFromConfig(config, { usePty: false });
child.stdout?.on('data', (d) => process.stdout.write(d));
child.on('close', (code) => console.log('exit:', code));
```

### Python

```python
from mxc_sandbox import MxcSandbox, MxcConfig

config = MxcConfig(command="python -c 'print(1+1)'")
sandbox = MxcSandbox(config)
result = sandbox.run()
print(result.stdout)
```

### Rust

```rust
use std::process::Command;

fn main() {
    let output = Command::new("./wxc-exec.exe")
        .arg("config.json")
        .output()
        .expect("Failed to execute MXC");
    
    println!("{}", String::from_utf8_lossy(&output.stdout));
}
```

## Configuration

See `config_examples/` directory for sample configurations:

- `basic_sandbox.json` - Simple read-only sandbox
- `network_isolated.json` - Network-enabled sandbox
- `stateful_session.json` - Long-lived stateful session

## Security Notes

⚠️ **MXC is under active development** — do not treat current policies as production-grade security boundaries.

For production use, always:
1. Run with minimal permissions
2. Disable network when not needed
3. Use shortest reasonable timeout
4. Monitor sandbox behavior