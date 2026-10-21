const fs = require('fs');
const html = fs.readFileSync('nexus_gaming_arena.html', 'utf8');
const lines = html.split('\n');
lines.forEach((line, idx) => {
  if (/<input[^>]+value=["'][^"']+["']/i.test(line)) {
    console.log(`Line ${idx + 1}: ${line.trim()}`);
  }
});
