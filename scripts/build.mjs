import { cp, mkdir, rm } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';

await rm('dist', { recursive: true, force: true });
await mkdir('dist', { recursive: true });
await cp('index.html', 'dist/index.html');
await cp('src/app.js', 'dist/app.js');
await cp('src/styles.css', 'dist/styles.css');
execFileSync(process.execPath, ['--check', 'src/app.js'], { stdio: 'inherit' });
console.log('Frontend build complete: dist/');
