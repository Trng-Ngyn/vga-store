const { spawnSync } = require('node:child_process');
const { dirname, resolve } = require('node:path');

const cli = resolve(dirname(require.resolve('codeceptjs')), '../bin/codecept.js');

const result = spawnSync(process.execPath, [
  cli,
  'run',
  '--steps',
  ...process.argv.slice(3)
], {
  stdio: 'inherit',
  env: { ...process.env, HEADLESS: String(process.argv[2] === 'headless') }
});

if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
