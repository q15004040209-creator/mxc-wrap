#!/usr/bin/env python3
"""
MXC Python Sandbox Wrapper
==========================

A Python wrapper for Microsoft eXecution Container (MXC) that provides
a simple interface to run untrusted code in isolated sandbox environments.

Usage:
    from mxc_sandbox import MxcSandbox, MxcConfig
    
    config = MxcConfig(command="python -c 'print(1+1)'")
    sandbox = MxcSandbox(config)
    result = sandbox.run()
    print(result.stdout)
"""

import subprocess
import json
import base64
import os
import tempfile
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from enum import Enum


class SandboxBackend(Enum):
    """MXC supported sandbox backends"""
    PROCESS_CONTAINER = "processcontainer"
    WINDOWS_SANDBOX = "windows_sandbox"
    LXC = "lxc"
    BUBBLEWRAP = "bubblewrap"
    SEATBELT = "seatbelt"  # macOS
    MICROVM = "microvm"
    HYPERLIGHT = "hyperlight"
    ISOLATION_SESSION = "isolation_session"
    WSLC = "wslc"


@dataclass
class FilesystemPolicy:
    """Filesystem access policy for sandbox"""
    readonly_paths: List[str] = field(default_factory=lambda: ["/usr", "/bin", "/lib"])
    readwrite_paths: List[str] = field(default_factory=lambda: ["/tmp", "/var/tmp"])
    denied_paths: List[str] = field(default_factory=list)


@dataclass
class NetworkPolicy:
    """Network access policy for sandbox"""
    allow_outbound: bool = False
    proxy: Optional[str] = None
    allowed_hosts: List[str] = field(default_factory=list)
    blocked_hosts: List[str] = field(default_factory=list)


@dataclass
class UiPolicy:
    """UI access policy for sandbox"""
    clipboard: str = "deny"  # allow, deny
    display: str = "deny"   # allow, deny
    gui: str = "deny"        # allow, deny


@dataclass
class MxcConfig:
    """MXC Sandbox Configuration (v0.6.0-alpha schema)"""
    version: str = "0.6.0-alpha"
    command: str = "echo 'Hello from MXC sandbox'"
    cwd: Optional[str] = "/tmp"
    filesystem: FilesystemPolicy = field(default_factory=FilesystemPolicy)
    network: NetworkPolicy = field(default_factory=NetworkPolicy)
    ui: UiPolicy = field(default_factory=UiPolicy)
    timeout_ms: int = 30_000
    experimental: bool = False
    
    def to_dict(self) -> dict:
        """Convert config to MXC JSON schema format"""
        return {
            "version": self.version,
            "process": {
                "commandLine": self.command,
                "cwd": self.cwd
            },
            "filesystem": {
                "readonlyPaths": self.filesystem.readonly_paths,
                "readwritePaths": self.filesystem.readwrite_paths,
                "deniedPaths": self.filesystem.denied_paths
            },
            "network": {
                "allowOutbound": self.network.allow_outbound,
                "proxy": self.network.proxy,
                "allowedHosts": self.network.allowed_hosts,
                "blockedHosts": self.network.blocked_hosts
            },
            "ui": {
                "clipboard": self.ui.clipboard,
                "display": self.ui.display,
                "gui": self.ui.gui
            },
            "timeoutMs": self.timeout_ms,
            "experimental": self.experimental
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_base64(self) -> str:
        """Encode config as base64 (for CLI --config-base64)"""
        return base64.b64encode(self.to_json().encode()).decode()


class MxcSandbox:
    """
    MXC Sandbox wrapper for running untrusted code safely.
    
    Example:
        >>> config = MxcConfig(command="python -c 'print(1+1)'")
        >>> sandbox = MxcSandbox(config, mxc_path="./wxc-exec.exe")
        >>> result = sandbox.run()
        >>> print(result.stdout)
    """
    
    def __init__(
        self,
        config: MxcConfig,
        mxc_path: str = "./wxc-exec.exe",
        use_base64: bool = False
    ):
        """
        Initialize MXC sandbox.
        
        Args:
            config: MxcConfig instance
            mxc_path: Path to MXC binary (wxc-exec.exe on Windows)
            use_base64: Use base64 encoding for config (default: False)
        """
        self.config = config
        self.mxc_path = mxc_path
        self.use_base64 = use_base64
        self._temp_files: List[str] = []
    
    def run(self, debug: bool = False) -> "SandboxResult":
        """
        Run command in sandbox.
        
        Args:
            debug: Enable debug output
            
        Returns:
            SandboxResult with stdout, stderr, and return code
        """
        # Write config to temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False,
            encoding='utf-8'
        ) as f:
            json.dump(self.config.to_dict(), f, indent=2)
            config_path = f.name
            self._temp_files.append(config_path)
        
        try:
            # Build command
            if self.use_base64:
                cmd = [
                    self.mxc_path,
                    "--config-base64",
                    self.config.to_base64()
                ]
            else:
                cmd = [self.mxc_path, config_path]
            
            if debug:
                cmd.append("--debug")
            
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout_ms / 1000
            )
            
            return SandboxResult(
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                success=result.returncode == 0
            )
            
        except subprocess.TimeoutExpired:
            return SandboxResult(
                stdout="",
                stderr=f"Timeout after {self.config.timeout_ms}ms",
                returncode=-1,
                success=False,
                timed_out=True
            )
        except FileNotFoundError:
            return SandboxResult(
                stdout="",
                stderr=f"MXC binary not found: {self.mxc_path}",
                returncode=-1,
                success=False
            )
        finally:
            # Cleanup temp files
            for path in self._temp_files:
                try:
                    os.unlink(path)
                except OSError:
                    pass
            self._temp_files.clear()
    
    def run_interactive(self) -> "SandboxResult":
        """Run sandbox with PTY (for interactive commands)"""
        # Note: PTY support requires usePty=True in spawn options
        # This is a simplified version - full PTY support needs pty module
        return self.run()


@dataclass
class SandboxResult:
    """Result from sandbox execution"""
    stdout: str
    stderr: str
    returncode: int
    success: bool
    timed_out: bool = False
    
    def __repr__(self) -> str:
        status = "✓ Success" if self.success else "✗ Failed"
        if self.timed_out:
            status = "⏱ Timeout"
        return f"SandboxResult({status}, returncode={self.returncode})"


# Convenience functions

def create_read_only_sandbox(command: str, timeout_ms: int = 30_000) -> MxcSandbox:
    """Create a read-only sandbox (no network, minimal filesystem access)"""
    config = MxcConfig(
        command=command,
        timeout_ms=timeout_ms,
        filesystem=FilesystemPolicy(
            readonly_paths=["/usr", "/bin", "/lib", "/opt"],
            readwrite_paths=["/tmp"]
        ),
        network=NetworkPolicy(allow_outbound=False),
        ui=UiPolicy(clipboard="deny", display="deny", gui="deny")
    )
    return MxcSandbox(config)


def create_network_isolated_sandbox(command: str, timeout_ms: int = 30_000) -> MxcSandbox:
    """Create a sandbox with network access"""
    config = MxcConfig(
        command=command,
        timeout_ms=timeout_ms,
        filesystem=FilesystemPolicy(
            readonly_paths=["/usr", "/bin", "/lib"],
            readwrite_paths=["/tmp"]
        ),
        network=NetworkPolicy(allow_outbound=True),
        ui=UiPolicy(clipboard="deny", display="deny", gui="deny")
    )
    return MxcSandbox(config)


# Demo function
def demo():
    """Run demonstration"""
    print("=" * 50)
    print("  MXC Python Sandbox Demo")
    print("=" * 50)
    
    # Demo 1: Simple echo command
    print("\n[1] Running simple echo command...")
    config = MxcConfig(command="echo 'Hello from MXC sandbox!'")
    sandbox = MxcSandbox(config)
    print(f"Config:\n{config.to_json()}\n")
    print("Note: Run with actual MXC binary to execute")
    
    # Demo 2: Python execution
    print("\n[2] Python execution sandbox config:")
    py_config = MxcConfig(
        command='python3 -c "print(\'Python running in sandbox!\')"',
        timeout_ms=30_000,
        filesystem=FilesystemPolicy(
            readonly_paths=["/usr/bin", "/usr/lib", "/bin", "/lib"],
            readwrite_paths=["/tmp"]
        ),
        network=NetworkPolicy(allow_outbound=False)
    )
    print(py_config.to_json())
    
    # Demo 3: Using convenience function
    print("\n[3] Using create_read_only_sandbox()...")
    sandbox = create_read_only_sandbox("python3 --version")
    print(f"Sandbox config:\n{sandbox.config.to_json()}")


if __name__ == "__main__":
    demo()