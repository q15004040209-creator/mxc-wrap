# MXC-Wrap 微软政策驱动隔离容器封装

[English](#english-section) | [中文](#中文-section)

---

## English Section

### 🎯 What is MXC-Wrap?

**MXC-Wrap** is a production-ready wrapper for [Microsoft MXC (Microsoft eXecution Container)](https://github.com/microsoft/mxc) — a policy-driven, layered isolation and containment system for running untrusted code safely.

MXC provides sandboxed code execution across **Windows, Linux, and macOS**, with support for multiple containment backends from OS-native process sandboxes to full VMs, all behind a unified JSON configuration schema and TypeScript SDK.

> ⭐ **Stars:** 460+ | **Weekly growth:** +57  
> 🛡️ **Note:** This is an **early-stage** project. MXC is under active development — do not treat current policies as production-grade security boundaries yet.

---

### 🔥 Key Features

| Feature | Description |
|---------|-------------|
| **🌐 Cross-Platform** | Windows 11, Linux (x64/ARM64), macOS (Apple Silicon/Intel) |
| **📄 JSON-Based Config** | Versioned schema for execution parameters & security policies |
| **🔒 Multiple Backends** | ProcessContainer, Windows Sandbox, LXC, Bubblewrap, Seatbelt (macOS), MicroVM, Hyperlight, IsolationSession, WSLC |
| **📋 Policy-Driven Sandboxing** | Filesystem (read-only/read-write paths), Network (proxy/allow/block), UI (clipboard/display/GUI) |
| **🔄 State-Aware Lifecycle** | Multi-step: provision → start → exec → stop → deprovision |
| **📦 TypeScript SDK** | `@microsoft/mxc-sdk` npm package with one-shot & state-aware APIs |
| **🔍 Diagnostics** | Debug logging + ETW (Event Tracing for Windows) |

---

### 🚀 Quick Start

#### 1. Install the SDK

```bash
npm install @microsoft/mxc-sdk
```

#### 2. TypeScript Demo

```typescript
import {
  spawnSandboxFromConfig,
  createConfigFromPolicy,
  getAvailableToolsPolicy,
  getTemporaryFilesPolicy,
  getPlatformSupport,
} from '@microsoft/mxc-sdk';

// Check platform support
if (!getPlatformSupport().isSupported) {
  throw new Error('MXC not available on this host');
}

// Build sandbox config from policies
const tools = getAvailableToolsPolicy(process.env);
const temp  = getTemporaryFilesPolicy();

const config = createConfigFromPolicy({
  version: '0.6.0-alpha',
  filesystem: {
    readonlyPaths:  tools.readonlyPaths,
    readwritePaths: temp.readwritePaths,
  },
  network: { allowOutbound: false },
  timeoutMs: 30_000,
});

// Execute untrusted code in sandbox
config.process!.commandLine = 'python -c "print(\'hello from sandbox\')"';

const child = spawnSandboxFromConfig(config, { usePty: false });
child.stdout!.on('data', (d) => process.stdout.write(d));
child.on('close', (code) => console.log('exit:', code));
```

#### 3. Rust Demo

```rust
// See examples/rust_demo/src/main.rs
use std::process::Command;

fn main() {
    // Build and run the MXC native binary
    let output = Command::new("./wxc-exec.exe")
        .args(&["--config", "config.json"])
        .output()
        .expect("Failed to execute MXC");

    println!("stdout: {}", String::from_utf8_lossy(&output.stdout));
    println!("stderr: {}", String::from_utf8_lossy(&output.stderr));
}
```

#### 4. Python Demo

```python
# See examples/python_demo/mxc_sandbox.py
import subprocess
import json

def run_in_sandbox(command: str, config: dict) -> subprocess.CompletedProcess:
    """Run a command inside an MXC sandbox."""
    result = subprocess.run(
        ["./wxc-exec.exe", "--config-base64", base64_encode(config)],
        capture_output=True,
        text=True
    )
    return result

# Example: Run Python in a read-only sandbox
config = {
    "version": "0.6.0-alpha",
    "process": {
        "commandLine": "python -c \"print('hello from sandbox')\""
    },
    "filesystem": {
        "readonlyPaths": ["/usr"],
        "readwritePaths": ["/tmp"]
    },
    "network": {"allowOutbound": False},
    "timeoutMs": 30_000
}
```

---

### 📁 Project Structure

```
mxc-wrap/
├── README.md              # This file (bilingual)
├── LICENSE                # MIT License
├── examples/
│   ├── rust_demo/          # Rust sandbox demo
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── main.rs
│   ├── python_demo/        # Python sandbox demo
│   │   └── mxc_sandbox.py
│   └── typescript_demo/    # TypeScript SDK demo
│       └── index.ts
├── config_examples/        # Sample MXC JSON configs
│   ├── basic_sandbox.json
│   ├── network_isolated.json
│   └── stateful_session.json
└── docs/
    ├── QUICKSTART.md       # Quick start guide
    └── POLICY_GUIDE.md     # Security policy reference
```

---

### 🔧 Configuration Schema (v0.6.0-alpha)

```json
{
  "version": "0.6.0-alpha",
  "process": {
    "commandLine": "python -c \"print('hello')\"",
    "cwd": "/tmp"
  },
  "filesystem": {
    "readonlyPaths": ["/usr/bin", "/lib"],
    "readwritePaths": ["/tmp", "/var/tmp"]
  },
  "network": {
    "allowOutbound": false,
    "proxy": "http://proxy:8080"
  },
  "ui": {
    "clipboard": "deny",
    "display": "deny"
  },
  "timeoutMs": 30_000
}
```

---

### 🌟 Why MXC-Wrap?

| Aspect | MXC-Wrap Benefit |
|--------|------------------|
| **Abstraction** | Clean high-level APIs for Rust/Python/TypeScript |
| **Examples** | Ready-to-run demos for all supported languages |
| **Documentation** | Bilingual (EN/CN) guides and configuration references |
| **Safety** | Multi-layered isolation: process → container → VM |
| **Flexibility** | 9+ containment backends across 3 platforms |

---

### 📚 Resources

- 🔗 [Original MXC Repository](https://github.com/microsoft/mxc)
- 📦 [npm SDK](https://www.npmjs.com/package/@microsoft/mxc-sdk)
- 📖 [MXC Schema Docs](./docs/)
- 🛡️ [Security Policy Guide](./docs/POLICY_GUIDE.md)

---

### ⚖️ License

MIT License — see [LICENSE](./LICENSE)

---

## 中文 section

### 🎯 什么是 MXC-Wrap？

**MXC-Wrap** 是 [微软 MXC (Microsoft eXecution Container)](https://github.com/microsoft/mxc) 的生产级封装库。MXC 是一个**政策驱动的分层隔离与 containment 系统**，用于安全运行不受信任的代码（模型输出、插件、工具）。

MXC 支持在 **Windows、Linux 和 macOS** 上运行沙盒代码，提供从 OS 原生进程沙箱到完整虚拟机的多种 containment 后端，全部通过统一的 JSON 配置模式和 TypeScript SDK 进行管理。

> ⭐ **星标:** 460+ | **本周增长:** +57  
> 🛡️ **注意:** MXC 仍处于**早期开发阶段**，请勿将当前策略作为生产级安全边界使用。

---

### 🔥 核心特性

| 特性 | 说明 |
|------|------|
| **🌐 跨平台** | Windows 11、Linux (x64/ARM64)、macOS (Apple Silicon/Intel) |
| **📄 JSON 配置** | 版本化模式定义执行参数和安全策略 |
| **🔒 多后端支持** | ProcessContainer、Windows Sandbox、LXC、Bubblewrap、Seatbelt (macOS)、MicroVM、Hyperlight、IsolationSession、WSLC |
| **📋 政策驱动沙箱** | 文件系统（只读/读写路径）、网络（代理/允许/阻止）、UI（剪贴板/显示/GUI） |
| **🔄 状态感知生命周期** | 多步骤：provision → start → exec → stop → deprovision |
| **📦 TypeScript SDK** | `@microsoft/mxc-sdk` npm 包，提供单次和状态感知 API |
| **🔍 诊断支持** | 调试日志 + ETW（Windows 事件追踪） |

---

### 🚀 快速开始

#### 1. 安装 SDK

```bash
npm install @microsoft/mxc-sdk
```

#### 2. TypeScript 示例

```typescript
import {
  spawnSandboxFromConfig,
  createConfigFromPolicy,
  getAvailableToolsPolicy,
  getTemporaryFilesPolicy,
  getPlatformSupport,
} from '@microsoft/mxc-sdk';

// 检查平台支持
if (!getPlatformSupport().isSupported) {
  throw new Error('当前平台不支持 MXC');
}

// 从策略构建沙箱配置
const tools = getAvailableToolsPolicy(process.env);
const temp  = getTemporaryFilesPolicy();

const config = createConfigFromPolicy({
  version: '0.6.0-alpha',
  filesystem: {
    readonlyPaths:  tools.readonlyPaths,
    readwritePaths: temp.readwritePaths,
  },
  network: { allowOutbound: false },
  timeoutMs: 30_000,
});

// 在沙箱中执行不受信任的代码
config.process!.commandLine = 'python -c "print(\'hello from sandbox\')"';

const child = spawnSandboxFromConfig(config, { usePty: false });
child.stdout!.on('data', (d) => process.stdout.write(d));
child.on('close', (code) => console.log('exit:', code));
```

#### 3. Rust 示例

```rust
// 参见 examples/rust_demo/src/main.rs
use std::process::Command;

fn main() {
    // 构建并运行 MXC 原生二进制
    let output = Command::new("./wxc-exec.exe")
        .args(&["--config", "config.json"])
        .output()
        .expect("Failed to execute MXC");

    println!("stdout: {}", String::from_utf8_lossy(&output.stdout));
    println!("stderr: {}", String::from_utf8_lossy(&output.stderr));
}
```

#### 4. Python 示例

```python
# 参见 examples/python_demo/mxc_sandbox.py
import subprocess
import json
import base64

def run_in_sandbox(command: str, config: dict) -> subprocess.CompletedProcess:
    """在 MXC 沙箱中运行命令。"""
    config_json = json.dumps(config)
    encoded = base64.b64encode(config_json.encode()).decode()

    result = subprocess.run(
        ["./wxc-exec.exe", "--config-base64", encoded],
        capture_output=True,
        text=True
    )
    return result

# 示例：在一个只读沙箱中运行 Python
config = {
    "version": "0.6.0-alpha",
    "process": {
        "commandLine": 'python -c "print(\'hello from sandbox\')"'
    },
    "filesystem": {
        "readonlyPaths": ["/usr/bin", "/lib"],
        "readwritePaths": ["/tmp", "/var/tmp"]
    },
    "network": {"allowOutbound": False},
    "timeoutMs": 30_000
}

result = run_in_sandbox("python test", config)
print(result.stdout)
print(result.stderr)
```

---

### 📁 项目结构

```
mxc-wrap/
├── README.md              # 本文件（双语）
├── LICENSE                # MIT 许可证
├── examples/
│   ├── rust_demo/          # Rust 沙箱示例
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── main.rs
│   ├── python_demo/        # Python 沙箱示例
│   │   └── mxc_sandbox.py
│   └── typescript_demo/    # TypeScript SDK 示例
│       └── index.ts
├── config_examples/        # MXC JSON 配置示例
│   ├── basic_sandbox.json
│   ├── network_isolated.json
│   └── stateful_session.json
└── docs/
    ├── QUICKSTART.md       # 快速开始指南
    └── POLICY_GUIDE.md     # 安全策略参考
```

---

### 🔧 配置模式 (v0.6.0-alpha)

```json
{
  "version": "0.6.0-alpha",
  "process": {
    "commandLine": "python -c \"print('hello')\"",
    "cwd": "/tmp"
  },
  "filesystem": {
    "readonlyPaths": ["/usr/bin", "/lib"],
    "readwritePaths": ["/tmp", "/var/tmp"]
  },
  "network": {
    "allowOutbound": false,
    "proxy": "http://proxy:8080"
  },
  "ui": {
    "clipboard": "deny",
    "display": "deny"
  },
  "timeoutMs": 30_000
}
```

---

### 🌟 为什么选择 MXC-Wrap？

| 方面 | MXC-Wrap 优势 |
|------|-------------|
| **抽象层** | 为 Rust/Python/TypeScript 提供简洁的高级 API |
| **示例** | 支持所有语言的开箱即用演示 |
| **文档** | 双语（英/中）指南和配置参考 |
| **安全性** | 多层隔离：进程 → 容器 → 虚拟机 |
| **灵活性** | 3 大平台 9+ 种 containment 后端 |

---

### 📚 相关资源

- 🔗 [原始 MXC 仓库](https://github.com/microsoft/mxc)
- 📦 [npm SDK](https://www.npmjs.com/package/@microsoft/mxc-sdk)
- 📖 [MXC 模式文档](./docs/)
- 🛡️ [安全策略指南](./docs/POLICY_GUIDE.md)

---

### ⚖️ 许可证

MIT License — 参见 [LICENSE](./LICENSE)