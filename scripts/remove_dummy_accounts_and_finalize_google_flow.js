const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const htmlPath = path.join(root, 'nexus_gaming_arena.html');
const appJsPath = path.join(root, 'static', 'js', 'app.js');
const swPath = path.join(root, 'sw.js');

console.log('--- Removing All Dummy/Admin Accounts and Finalizing Clean Google Flow ---');

// 1. UPDATE static/js/app.js: Ensure enterArenaApp closes modal-google-account-picker completely
let appJs = fs.readFileSync(appJsPath, 'utf8');

const oldEnterArena = `    const lm = document.getElementById("modal-login");
    if (lm) {
        delete lm.dataset.gatekeeper;
        lm.removeAttribute("data-gatekeeper");
        const cb = document.getElementById("modal-login-close-btn");
        if (cb) cb.style.display = "";
        closeModal("modal-login");
    }`;

const newEnterArena = `    const lm = document.getElementById("modal-login");
    if (lm) {
        delete lm.dataset.gatekeeper;
        lm.removeAttribute("data-gatekeeper");
        const cb = document.getElementById("modal-login-close-btn");
        if (cb) cb.style.display = "";
        closeModal("modal-login");
    }
    const gp = document.getElementById("modal-google-account-picker");
    if (gp) {
        gp.classList.add("hidden");
        gp.classList.remove("flex");
        gp.style.display = "none";
    }`;

if (appJs.includes(oldEnterArena)) {
    appJs = appJs.replace(oldEnterArena, newEnterArena);
    console.log('✓ Updated enterArenaApp to guarantee modal-google-account-picker is closed on entry');
}

// In handleGoogleAuthSuccess: make sure role is "PLAYER" unless explicit superadmin login
const oldRoleLogic = `const role = googleUser.role || (email.toLowerCase().includes("admin") || email.toLowerCase() === "wolfy@nexusarena.gg" ? "ADMIN" : "PLAYER");`;
const newRoleLogic = `const role = "PLAYER";`;

if (appJs.includes(oldRoleLogic)) {
    appJs = appJs.replace(oldRoleLogic, newRoleLogic);
    console.log('✓ Set default Google auth role strictly to PLAYER');
}

fs.writeFileSync(appJsPath, appJs, 'utf8');
console.log('✓ static/js/app.js updated');

// 2. UPDATE nexus_gaming_arena.html
let html = fs.readFileSync(htmlPath, 'utf8');

const googleSvgIcon = `<svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24">
    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
</svg>`;

const cleanMultiStepGoogleModal = `
    <!-- ========================================== -->
    <!-- 19b. GOOGLE AUTHENTICATION MULTI-STEP MODAL (OFFICIAL GOOGLE FLOW - ZERO DUMMY ACCOUNTS) -->
    <!-- ========================================== -->
    <div id="modal-google-account-picker" class="fixed inset-0 z-50 bg-black/85 backdrop-blur-md hidden items-center justify-center p-4 animate-fade-in" onclick="if(event.target === this) closeModal('modal-google-account-picker')">
        <div class="bg-[#1e1f20] border border-gray-700/80 w-full max-w-sm rounded-3xl p-6 sm:p-7 space-y-4 relative shadow-2xl text-gray-100">
            <!-- Close Button -->
            <button onclick="closeModal('modal-google-account-picker')" class="modal-close-btn absolute top-5 right-5 text-gray-400 hover:text-white transition-colors cursor-pointer" title="Cancel" aria-label="Cancel">
                <i class="fa-solid fa-xmark text-lg"></i>
            </button>

            <!-- Google Branding Header -->
            <div class="space-y-1.5 text-center pb-1">
                <div class="w-12 h-12 rounded-full bg-white flex items-center justify-center mx-auto shadow-md">
                    ${googleSvgIcon}
                </div>
                <h3 class="text-lg font-semibold text-white">Sign in with Google</h3>
                <p class="text-xs text-gray-400">to continue to <span class="text-cyan-400 font-bold">Nexus Gaming Arena</span></p>
            </div>

            <!-- STEP 1: FEED GOOGLE ACCOUNT DETAILS -->
            <div id="google-modal-step-1" class="space-y-4">
                <div class="space-y-1.5">
                    <label class="text-[11px] font-bold text-gray-300">Email or phone</label>
                    <input type="email" id="google-modal-email-input" placeholder="Enter your Google email" autofocus onkeydown="if(event.key==='Enter') goToGoogleModalPasswordStep()" class="w-full bg-[#131722] border border-gray-700 rounded-xl px-3.5 py-3 text-sm text-white focus:outline-none focus:border-cyan-400 font-mono transition-colors">
                </div>

                <div class="text-[11px] text-gray-400 leading-relaxed">
                    To continue, Google will share your name, email address, and profile picture with Nexus Gaming Arena.
                </div>

                <div class="pt-2 flex items-center justify-between">
                    <button type="button" onclick="closeModal('modal-google-account-picker')" class="px-4 py-2 rounded-xl text-xs text-gray-400 hover:text-white transition-colors cursor-pointer">
                        Cancel
                    </button>
                    <button type="button" onclick="goToGoogleModalPasswordStep()" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-600 text-black font-bold text-xs uppercase tracking-wider hover:brightness-110 transition-all cursor-pointer shadow">
                        Next &rarr;
                    </button>
                </div>
            </div>

            <!-- STEP 2: FEED PASSWORD & KEEP ME LOGGED IN (ON/OFF) TOGGLE -->
            <div id="google-modal-step-2" class="space-y-3.5 hidden">
                <!-- Selected account chip -->
                <div class="p-2.5 rounded-xl bg-black/40 border border-gray-700/80 flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <i class="fa-solid fa-circle-user text-cyan-400 text-lg"></i>
                        <span id="google-modal-display-email" class="text-xs font-mono text-gray-200 font-bold truncate max-w-[200px]">user@gmail.com</span>
                    </div>
                    <button type="button" onclick="goToGoogleModalAccountStep()" class="text-[10px] text-cyan-400 hover:underline cursor-pointer">Change</button>
                </div>

                <!-- Google Password Input -->
                <div class="space-y-1.5">
                    <label class="text-[11px] font-bold text-gray-300">Enter your password</label>
                    <div class="relative">
                        <input type="password" id="google-modal-password-input" placeholder="Password" onkeydown="if(event.key==='Enter') verifyWithGoogleInModal()" class="w-full bg-[#131722] border border-gray-700 rounded-xl pl-3.5 pr-10 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-400 font-mono transition-colors">
                        <button type="button" onclick="toggleGoogleModalPasswordVisibility()" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-cyan-400 transition-colors" title="Toggle password visibility">
                            <i class="fa-solid fa-eye text-xs" id="google-modal-pw-icon"></i>
                        </button>
                    </div>
                </div>

                <!-- KEEP ME LOGGED IN (ON / OFF) TOGGLE -->
                <div class="p-3 rounded-xl bg-black/40 border border-gray-700 flex items-center justify-between">
                    <div>
                        <div class="text-xs font-bold text-gray-200">Keep me logged in</div>
                        <div class="text-[10px] text-cyan-400 font-mono" id="modal-keep-login-status">ON &bull; Stay signed in on this device</div>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" id="modal-keep-login-toggle" checked onchange="onToggleModalKeepLogin(this.checked)" class="sr-only peer">
                        <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
                    </label>
                </div>

                <div class="pt-2 flex items-center justify-between">
                    <button type="button" onclick="goToGoogleModalAccountStep()" class="px-4 py-2 rounded-xl text-xs text-gray-400 hover:text-white transition-colors cursor-pointer">
                        &larr; Back
                    </button>
                    <button type="button" onclick="verifyWithGoogleInModal()" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 text-black font-bold text-xs uppercase tracking-wider hover:brightness-110 transition-all cursor-pointer shadow">
                        Verify &bull; Sign In &rarr;
                    </button>
                </div>
            </div>

            <!-- STEP 3: VERIFYING IN PROGRESS -->
            <div id="google-modal-step-3" class="p-6 text-center space-y-3 hidden">
                <div class="w-10 h-10 border-4 border-gray-700 border-t-cyan-400 rounded-full animate-spin mx-auto"></div>
                <div class="text-sm font-bold text-white">Verifying with Google...</div>
                <div class="text-xs text-gray-400 font-mono">Checking account credentials &amp; security policy</div>
            </div>

            <!-- STEP 4: VERIFICATION SUCCESSFUL FROM GOOGLE -->
            <div id="google-modal-step-4" class="p-6 text-center space-y-3 hidden">
                <div class="w-12 h-12 rounded-full bg-green-500/20 text-green-400 border border-green-500/40 flex items-center justify-center text-xl mx-auto">
                    <i class="fa-solid fa-check"></i>
                </div>
                <div class="text-sm font-bold text-green-400">Verification successful from Google</div>
                <div class="text-xs text-gray-300 font-mono">Signing you into Nexus Gaming Arena...</div>
            </div>

            <!-- Footer terms -->
            <div class="pt-1 text-center text-[10px] text-gray-400 leading-relaxed border-t border-gray-800">
                By continuing with Google, you agree to Nexus Arena's Terms of Service and Privacy Policy.
            </div>
        </div>
    </div>
`;

const oldModalSearchRegex = /<!-- ========================================== -->\s*\n\s*<!-- 19b\. GOOGLE AUTHENTICATION[\s\S]*?<!-- 20\. INSTALL APP ON PHONE MODAL/;

if (oldModalSearchRegex.test(html)) {
    html = html.replace(oldModalSearchRegex, cleanMultiStepGoogleModal.trim() + '\n\n    <!-- 20. INSTALL APP ON PHONE MODAL');
    console.log('✓ Cleaned modal-google-account-picker in HTML: 0 dummy accounts');
} else {
    console.warn('Could not match oldModalSearchRegex in HTML');
}

// Bump version in HTML to v7.0.4
html = html.replace(/v=7\.0\.3/g, 'v=7.0.4');

fs.writeFileSync(htmlPath, html, 'utf8');
console.log('✓ nexus_gaming_arena.html updated to v7.0.4');

// 3. UPDATE sw.js version cache
let sw = fs.readFileSync(swPath, 'utf8');
sw = sw.replace(/nexus-arena-v[0-9.]+/g, 'nexus-arena-v7.0.4');
sw = sw.replace(/v=[0-9.]+/g, 'v=7.0.4');
fs.writeFileSync(swPath, sw, 'utf8');
console.log('✓ sw.js updated to v7.0.4');

console.log('--- Completed Clean Update ---');
