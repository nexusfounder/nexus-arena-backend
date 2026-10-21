const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const dist = path.join(root, 'dist');
const templates = path.join(root, 'templates');

function copyDirRecursive(src, dest) {
    if (!fs.existsSync(src)) return;
    fs.mkdirSync(dest, { recursive: true });
    const entries = fs.readdirSync(src, { withFileTypes: true });
    for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        if (entry.isDirectory()) {
            copyDirRecursive(srcPath, destPath);
        } else {
            fs.copyFileSync(srcPath, destPath);
        }
    }
}

// 1. Sync nexus_gaming_arena.html -> dist/index.html
fs.mkdirSync(dist, { recursive: true });
fs.copyFileSync(path.join(root, 'nexus_gaming_arena.html'), path.join(dist, 'index.html'));
console.log('✓ Copied nexus_gaming_arena.html -> dist/index.html');

// 2. Remove obsolete mock files from dist if present
if (fs.existsSync(path.join(dist, 'google_auth_popup.html'))) {
    fs.unlinkSync(path.join(dist, 'google_auth_popup.html'));
    console.log('✓ Cleaned obsolete google_auth_popup.html from dist');
}

// 3. Sync nexus_gaming_arena.html -> templates/index.html
fs.mkdirSync(templates, { recursive: true });
fs.copyFileSync(path.join(root, 'nexus_gaming_arena.html'), path.join(templates, 'index.html'));
console.log('✓ Copied nexus_gaming_arena.html -> templates/index.html');

// 4. Sync sw.js -> dist/sw.js
if (fs.existsSync(path.join(root, 'sw.js'))) {
    fs.copyFileSync(path.join(root, 'sw.js'), path.join(dist, 'sw.js'));
    console.log('✓ Copied sw.js -> dist/sw.js');
}

// 5. Sync static/ -> dist/static/
copyDirRecursive(path.join(root, 'static'), path.join(dist, 'static'));
console.log('✓ Synchronized static/ -> dist/static/');

console.log('Synchronization complete!');
