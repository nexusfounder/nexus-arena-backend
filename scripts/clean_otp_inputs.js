const fs = require('fs');

let html = fs.readFileSync('nexus_gaming_arena.html', 'utf8');

// Replace OTP inputs with values
const otpOld = `<div class="flex justify-center gap-2">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyan-500/50 text-center text-lg font-bold text-cyan-400 rounded-xl focus:outline-none" value="7">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" value="9">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" value="4">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" value="2">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" value="8">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" value="1">
            </div>`;

const otpNew = `<div class="flex justify-center gap-2">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyan-500/50 text-center text-lg font-bold text-cyan-400 rounded-xl focus:outline-none" placeholder="•">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" placeholder="•">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" placeholder="•">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" placeholder="•">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" placeholder="•">
                <input type="text" maxlength="1" class="otp-input w-11 h-12 bg-cyber-dark border border-cyber-border text-center text-lg font-bold text-gray-200 rounded-xl focus:outline-none" placeholder="•">
            </div>`;

// Normalize CRLF in search
const normalize = str => str.replace(/\r\n/g, '\n');
const isCRLF = html.includes('\r\n');

let normHtml = normalize(html);
let normOld = normalize(otpOld);
let normNew = normalize(otpNew);

if (normHtml.includes(normOld)) {
  normHtml = normHtml.replace(normOld, normNew);
  if (isCRLF) {
    normHtml = normHtml.replace(/\n/g, '\r\n');
  }
  fs.writeFileSync('nexus_gaming_arena.html', normHtml, 'utf8');
  console.log('OTP inputs updated successfully');
} else {
  console.log('OTP snippet not found');
}
