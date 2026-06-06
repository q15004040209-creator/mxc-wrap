/**
 * MXC TypeScript Demo
 * 
 * Demonstrates how to use @microsoft/mxc-sdk for sandboxed code execution.
 */

import {
  spawnSandboxFromConfig,
  createConfigFromPolicy,
  getAvailableToolsPolicy,
  getTemporaryFilesPolicy,
  getPlatformSupport,
  provisionSandbox,
  startSandbox,
  execInSandboxAsync,
  stopSandbox,
  deprovisionSandbox,
} from '@microsoft/mxc-sdk';

// ============================================================================
// Example 1: One-shot sandbox (simple use case)
// ============================================================================

async function oneShotSandboxDemo() {
  console.log('='.repeat(50));
  console.log('  MXC One-Shot Sandbox Demo');
  console.log('='.repeat(50));

  // Check if MXC is supported on this platform
  if (!getPlatformSupport().isSupported) {
    console.error('MXC is not available on this platform');
    return;
  }

  console.log(`Platform support: ${JSON.stringify(getPlatformSupport(), null, 2)}`);

  // Get sandbox policies based on environment
  const tools = getAvailableToolsPolicy(process.env);
  const temp  = getTemporaryFilesPolicy();

  console.log('\nAvailable tools (readonly paths):', tools.readonlyPaths);
  console.log('Temp files (readwrite paths):', temp.readwritePaths);

  // Create sandbox configuration from policies
  const config = createConfigFromPolicy({
    version: '0.6.0-alpha',
    filesystem: {
      readonlyPaths:  tools.readonlyPaths,
      readwritePaths: temp.readwritePaths,
    },
    network: { allowOutbound: false },
    timeoutMs: 30_000,
  });

  // Set the command to run
  config.process!.commandLine = 'python -c "print(\'Hello from MXC sandbox!\')"';

  console.log('\nSandbox config:', JSON.stringify(config, null, 2));

  // Spawn sandbox and run
  const child = spawnSandboxFromConfig(config, { usePty: false });

  child.stdout?.on('data', (data: Buffer) => {
    process.stdout.write(`[stdout] ${data.toString()}`);
  });

  child.stderr?.on('data', (data: Buffer) => {
    process.stderr.write(`[stderr] ${data.toString()}`);
  });

  child.on('close', (code: number | null) => {
    console.log(`\nProcess exited with code: ${code}`);
  });

  child.on('error', (err: Error) => {
    console.error('Sandbox error:', err);
  });
}

// ============================================================================
// Example 2: State-aware lifecycle (long-lived sandbox)
// ============================================================================

async function statefulSandboxDemo() {
  console.log('\n' + '='.repeat(50));
  console.log('  MXC Stateful Sandbox Demo');
  console.log('='.repeat(50));

  if (!getPlatformSupport().isSupported) {
    console.error('MXC is not available on this platform');
    return;
  }

  // Get policies
  const tools = getAvailableToolsPolicy(process.env);
  const temp  = getTemporaryFilesPolicy();

  // Create config for stateful sandbox
  const config = createConfigFromPolicy({
    version: '0.6.0-alpha',
    filesystem: {
      readonlyPaths:  tools.readonlyPaths,
      readwritePaths: temp.readwritePaths,
    },
    network: { allowOutbound: false },
    timeoutMs: 60_000,
  });

  try {
    console.log('\n[Step 1] Provisioning sandbox...');
    const sandboxId = await provisionSandbox(config);
    console.log(`Sandbox provisioned: ${sandboxId}`);

    console.log('\n[Step 2] Starting sandbox...');
    await startSandbox(sandboxId);
    console.log('Sandbox started');

    console.log('\n[Step 3] Executing commands in sandbox...');
    
    // Execute multiple commands in the same sandbox
    const commands = [
      'echo "First command"',
      'python -c "print(1 + 1)"',
      'echo "Last command"',
    ];

    for (const cmd of commands) {
      config.process!.commandLine = cmd;
      const result = await execInSandboxAsync(sandboxId, config);
      console.log(`Command "${cmd}" result: ${result}`);
    }

    console.log('\n[Step 4] Stopping sandbox...');
    await stopSandbox(sandboxId);
    console.log('Sandbox stopped');

    console.log('\n[Step 5] Deprovisioning sandbox...');
    await deprovisionSandbox(sandboxId);
    console.log('Sandbox deprovisioned');

    console.log('\n✓ Stateful sandbox lifecycle complete');
    
  } catch (error) {
    console.error('Stateful sandbox error:', error);
  }
}

// ============================================================================
// Example 3: Custom policy sandbox
// ============================================================================

async function customPolicyDemo() {
  console.log('\n' + '='.repeat(50));
  console.log('  MXC Custom Policy Sandbox Demo');
  console.log('='.repeat(50));

  if (!getPlatformSupport().isSupported) {
    console.error('MXC is not available on this platform');
    return;
  }

  // Create custom config with specific policies
  const config = createConfigFromPolicy({
    version: '0.6.0-alpha',
    filesystem: {
      readonlyPaths: ['/usr/bin', '/usr/lib', '/bin', '/lib'],
      readwritePaths: ['/tmp/sandbox'],
    },
    network: { allowOutbound: false },
    ui: {
      clipboard: 'deny',
      display: 'deny',
      gui: 'deny',
    },
    timeoutMs: 30_000,
  });

  // Run a Python script with numpy (if available)
  config.process!.commandLine = 'python -c "import sys; print(sys.version)"';

  console.log('\nRunning with custom policy (no network, limited filesystem)...');
  console.log('Config:', JSON.stringify(config, null, 2));

  const child = spawnSandboxFromConfig(config, { usePty: false });

  child.stdout?.on('data', (data: Buffer) => {
    process.stdout.write(`[stdout] ${data.toString()}`);
  });

  child.stderr?.on('data', (data: Buffer) => {
    process.stderr.write(`[stderr] ${data.toString()}`);
  });

  child.on('close', (code: number | null) => {
    console.log(`\nProcess exited with code: ${code}`);
  });
}

// ============================================================================
// Main: Run all demos
// ============================================================================

async function main() {
  console.log('\n🔷 MXC TypeScript SDK Demo');
  console.log('   Microsoft eXecution Container\n');

  await oneShotSandboxDemo();
  await statefulSandboxDemo();
  await customPolicyDemo();

  console.log('\n' + '='.repeat(50));
  console.log('  Demo complete!');
  console.log('='.repeat(50));
}

main().catch(console.error);