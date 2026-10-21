const fs = require('fs');

console.log('=== AUDITING STATIC/JS/APP.JS FOR SECURITY ISSUES ===');
const appJs = fs.readFileSync('static/js/app.js', 'utf8');
const appLines = appJs.split('\n');

// 1. Check addEventListener('message')
appLines.forEach((l, i) => {
  if (l.includes("addEventListener('message'") || l.includes('addEventListener("message"')) {
    console.log(`[POSTMESSAGE LISTENER] Line ${i + 1}: ${l.trim()}`);
    for (let j = 1; j <= 25; j++) {
      if (appLines[i + j]) console.log(`  Line ${i + 1 + j}: ${appLines[i + j]}`);
    }
  }
});

// 2. Check eval, Function, innerHTML
let evalCount = 0;
let innerHTMLCount = 0;
appLines.forEach((l, i) => {
  if (/\beval\s*\(/.test(l)) {
    console.log(`[EVAL USAGE] Line ${i + 1}: ${l.trim()}`);
    evalCount++;
  }
  if (l.includes('.innerHTML =') || l.includes('.innerHTML+=')) {
    innerHTMLCount++;
  }
});
console.log(`[SUMMARY] Total innerHTML assignments: ${innerHTMLCount}`);

// 3. Check for hardcoded secrets, tokens, master passwords
const secretPatterns = [
  /password\s*===/i,
  /token\s*===/i,
  /secret/i,
  /admin/i,
  /recovery_code/i
];

appLines.forEach((l, i) => {
  if (l.includes('=== "admin"') || l.includes('=== "wolfy"') || l.includes('demo_') || l.includes('Master Admin')) {
    if (i < 6500) { // sample around interesting parts
      // console.log(`[AUTH/ADMIN CHECK] Line ${i + 1}: ${l.trim()}`);
    }
  }
});
