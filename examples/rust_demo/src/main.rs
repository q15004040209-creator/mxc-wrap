//! MXC Rust Sandbox Demo
//! 
//! This demo shows how to use MXC (Microsoft eXecution Container) from Rust
//! to run untrusted code in an isolated sandbox environment.

use std::process::{Command, Stdio};
use std::fs;
use std::path::Path;
use serde::{Deserialize, Serialize};

/// MXC Configuration structure (v0.6.0-alpha schema)
#[derive(Debug, Serialize, Deserialize)]
struct MxcConfig {
    version: String,
    #[serde(rename = "process")]
    process: ProcessConfig,
    #[serde(rename = "filesystem")]
    filesystem: FilesystemConfig,
    #[serde(rename = "network")]
    network: NetworkConfig,
    #[serde(rename = "timeoutMs")]
    timeout_ms: u32,
}

#[derive(Debug, Serialize, Deserialize)]
struct ProcessConfig {
    #[serde(rename = "commandLine")]
    command_line: String,
    cwd: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct FilesystemConfig {
    #[serde(rename = "readonlyPaths")]
    readonly_paths: Vec<String>,
    #[serde(rename = "readwritePaths")]
    readwrite_paths: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct NetworkConfig {
    #[serde(rename = "allowOutbound")]
    allow_outbound: bool,
}

impl Default for MxcConfig {
    fn default() -> Self {
        MxcConfig {
            version: "0.6.0-alpha".to_string(),
            process: ProcessConfig {
                command_line: "echo 'Hello from MXC sandbox!'".to_string(),
                cwd: Some("/tmp".to_string()),
            },
            filesystem: FilesystemConfig {
                readonly_paths: vec!["/usr".to_string(), "/bin".to_string()],
                readwrite_paths: vec!["/tmp".to_string()],
            },
            network: NetworkConfig {
                allow_outbound: false,
            },
            timeout_ms: 30_000,
        }
    }
}

impl MxcConfig {
    /// Create a config for running a command in a read-only sandbox
    pub fn read_only(command: &str) -> Self {
        let mut config = MxcConfig::default();
        config.process.command_line = command.to_string();
        config
    }

    /// Create a config for running with network access
    pub fn with_network(command: &str) -> Self {
        let mut config = MxcConfig::default();
        config.process.command_line = command.to_string();
        config.network.allow_outbound = true;
        config
    }

    /// Serialize config to JSON string
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(self)
    }

    /// Save config to a file
    pub fn save_to_file(&self, path: &Path) -> Result<(), std::io::Error> {
        let json = self.to_json().map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
        fs::write(path, json)
    }
}

/// Run a command in MXC sandbox
pub fn run_in_sandbox(mxc_path: &Path, config: &MxcConfig) -> Result<String, String> {
    // Save config to temp file
    let temp_config = std::env::temp_dir().join("mxc_temp_config.json");
    config.save_to_file(&temp_config).map_err(|e| e.to_string())?;

    // Execute MXC
    let output = Command::new(mxc_path)
        .arg(temp_config.as_os_str())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| e.to_string())?;

    // Cleanup
    let _ = fs::remove_file(&temp_config);

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

/// Run with base64-encoded config (useful for CLI)
pub fn run_with_base64(mxc_path: &Path, config: &MxcConfig) -> Result<String, String> {
    let temp_config = std::env::temp_dir().join("mxc_temp_config.json");
    config.save_to_file(&temp_config).map_err(|e| e.to_string())?;

    let output = Command::new(mxc_path)
        .arg("--config")
        .arg(temp_config.as_os_str())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .output()
        .map_err(|e| e.to_string())?;

    let _ = fs::remove_file(&temp_config);

    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).to_string())
    }
}

fn main() {
    println!("========================================");
    println!("  MXC Rust Sandbox Demo");
    println!("========================================\n");

    // Example 1: Run a simple command in sandbox
    println!("[1] Running simple echo command in sandbox...");
    let config = MxcConfig::read_only("echo 'Hello from MXC sandbox!'");
    println!("Config: {}\n", config.to_json().unwrap());

    // Example 2: Network-isolated sandbox
    println!("[2] Network-isolated sandbox config:");
    let net_config = MxcConfig::with_network("curl -s https://api.github.com");
    println!("{}\n", net_config.to_json().unwrap());

    // Example 3: Custom sandbox for Python
    println!("[3] Python execution sandbox:");
    let py_config = MxcConfig {
        version: "0.6.0-alpha".to_string(),
        process: ProcessConfig {
            command_line: "python3 -c \"import sys; print('Python:', sys.version)\"".to_string(),
            cwd: Some("/tmp".to_string()),
        },
        filesystem: FilesystemConfig {
            readonly_paths: vec![
                "/usr/bin".to_string(),
                "/usr/lib".to_string(),
                "/bin".to_string(),
                "/lib".to_string(),
            ],
            readwrite_paths: vec!["/tmp".to_string()],
        },
        network: NetworkConfig {
            allow_outbound: false,
        },
        timeout_ms: 30_000,
    };
    println!("{}\n", py_config.to_json().unwrap());

    println!("========================================");
    println!("  To run this demo:");
    println!("  1. Build MXC: cargo build --release");
    println!("  2. Run: ./target/release/mxc-rust-demo");
    println!("  3. Point to your MXC binary:");
    println!("     let result = run_in_sandbox(Path::new(\"./wxc-exec.exe\"), &config);");
    println!("========================================");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_serialization() {
        let config = MxcConfig::default();
        let json = config.to_json().unwrap();
        assert!(json.contains("0.6.0-alpha"));
        assert!(json.contains("process"));
        assert!(json.contains("filesystem"));
    }

    #[test]
    fn test_read_only_config() {
        let config = MxcConfig::read_only("echo test");
        assert_eq!(config.network.allow_outbound, false);
        assert!(config.filesystem.readonly_paths.len() > 0);
    }

    #[test]
    fn test_network_enabled_config() {
        let config = MxcConfig::with_network("curl https://example.com");
        assert_eq!(config.network.allow_outbound, true);
    }
}