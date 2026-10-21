const fs = require('fs');

const appJs = fs.readFileSync('static/js/app.js', 'utf8');
const lines = appJs.split('\n');

console.log('=== AUDITING INNERHTML USAGE IN APP.JS ===');

const suspiciousPatterns = [];

lines.forEach((line, idx) => {
  if (line.includes('.innerHTML =') || line.includes('.innerHTML +=') || line.includes('.insertAdjacentHTML(')) {
    // Check next 10 lines for template literals or unescaped variables
    let snippet = line;
    for (let j = 1; j <= 8; j++) {
      if (lines[idx + j]) snippet += '\n' + lines[idx + j];
    }
    // Look for variables inside ${...} that don't have escapeHtml or sanitize
    const matches = snippet.match(/\$\{([^}]+)\}/g);
    if (matches) {
      const unescaped = matches.filter(m => {
        const inner = m.slice(2, -1).trim();
        return !inner.includes('escapeHtml') && 
               !inner.includes('encodeURIComponent') &&
               !inner.includes('Math.') &&
               !inner.includes('Date') &&
               !inner.includes('toLocaleString') &&
               !inner.includes('toFixed') &&
               !inner.includes('parseInt') &&
               !inner.includes('Number') &&
               !inner.includes('?') && // ternary often HTML structure
               !inner.startsWith('"') &&
               !inner.startsWith("'") &&
               (inner.includes('user') || inner.includes('name') || inner.includes('comment') || inner.includes('title') || inner.includes('text') || inner.includes('message') || inner.includes('reason'));
      });
      if (unescaped.length > 0) {
        suspiciousPatterns.push({
          line: idx + 1,
          code: line.trim(),
          unescaped: unescaped
        });
      }
    }
  }
});

console.log(`Found ${suspiciousPatterns.length} potential XSS points:`);
suspiciousPatterns.slice(0, 25).forEach(p => {
  console.log(`Line ${p.line}: ${p.code}`);
  console.log(`   Variables without escapeHtml: ${p.unescaped.join(', ')}`);
  console.log('-'.repeat(50));
});
