const fs = require('fs');

let code = fs.readFileSync('static/js/app.js', 'utf8');

// 1. Add escapeHtml at top of file if not present near line 10
if (!code.slice(0, 500).includes('function escapeHtml')) {
  const topDeclaration = `// Global HTML Sanitizer
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
window.escapeHtml = escapeHtml;

`;
  code = topDeclaration + code;
  console.log('✓ Added escapeHtml to top of app.js');
}

// 2. Safe showToast using textContent
const oldShowToast = `function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = \`pointer-events-auto px-5 py-3.5 rounded-2xl border shadow-2xl flex items-center gap-3 text-sm font-bold transition-all duration-300 tactical-badge \${
        type === 'success' ? 'bg-cyber-card/95 border-cyan-400/50 text-cyan-400 glow-cyan' : 'bg-cyber-card/95 border-violet-500/50 text-violet-300 glow-violet'
    }\`;
    toast.innerHTML = \`<i class="fa-solid \${type === 'success' ? 'fa-circle-check text-cyan-400' : 'fa-circle-info text-violet-400'}"></i> \${message}\`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}`;

const newShowToast = `function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = \`pointer-events-auto px-5 py-3.5 rounded-2xl border shadow-2xl flex items-center gap-3 text-sm font-bold transition-all duration-300 tactical-badge \${
        type === 'success' ? 'bg-cyber-card/95 border-cyan-400/50 text-cyan-400 glow-cyan' : 'bg-cyber-card/95 border-violet-500/50 text-violet-300 glow-violet'
    }\`;
    const icon = document.createElement('i');
    icon.className = \`fa-solid \${type === 'success' ? 'fa-circle-check text-cyan-400' : 'fa-circle-info text-violet-400'}\`;
    toast.appendChild(icon);
    const textSpan = document.createElement('span');
    textSpan.textContent = String(message || '');
    toast.appendChild(textSpan);
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}`;

if (code.includes(oldShowToast)) {
  code = code.replace(oldShowToast, newShowToast);
  console.log('✓ Patched showToast for XSS immunity');
} else {
  console.log('⚠ oldShowToast not matched exactly, checking CRLF');
  const normCode = code.replace(/\r\n/g, '\n');
  const normOld = oldShowToast.replace(/\r\n/g, '\n');
  const normNew = newShowToast.replace(/\r\n/g, '\n');
  if (normCode.includes(normOld)) {
    code = normCode.replace(normOld, normNew);
    console.log('✓ Patched showToast with normalized line breaks');
  }
}

// 3. Tournament card escaping
code = code.replace(
  'alt="${t.title}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 opacity-90">',
  'alt="${escapeHtml(t.title)}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 opacity-90">'
);
code = code.replace(
  '<h3 class="font-orbitron font-extrabold text-lg text-white group-hover:text-cyan-400 transition-colors drop-shadow-[0_0_8px_rgba(0,242,254,0.3)]">${t.title}</h3>',
  '<h3 class="font-orbitron font-extrabold text-lg text-white group-hover:text-cyan-400 transition-colors drop-shadow-[0_0_8px_rgba(0,242,254,0.3)]">${escapeHtml(t.title)}</h3>'
);

// 4. Leaderboard podium & table escaping
code = code.replace(
  '<h4 class="font-orbitron font-extrabold text-white text-lg">${p.username}</h4>',
  '<h4 class="font-orbitron font-extrabold text-white text-lg">${escapeHtml(p.username)}</h4>'
);
code = code.replace(
  '<p class="font-extrabold text-white text-base">${p.username}</p>',
  '<p class="font-extrabold text-white text-base">${escapeHtml(p.username)}</p>'
);

// 5. Roster escaping
code = code.replace(
  '<h6 class="font-bold text-white">${p.username}</h6>',
  '<h6 class="font-bold text-white">${escapeHtml(p.username)}</h6>'
);

// 6. Banner username escaping
code = code.replace(
  '<span class="text-xs font-mono font-bold text-cyan-300">@${state.user.username}</span>',
  '<span class="text-xs font-mono font-bold text-cyan-300">@${escapeHtml(state.user.username)}</span>'
);

fs.writeFileSync('static/js/app.js', code, 'utf8');
console.log('✓ XSS protections written to static/js/app.js');
