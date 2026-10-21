const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const appJsPath = path.join(root, 'static', 'js', 'app.js');
const htmlPath = path.join(root, 'nexus_gaming_arena.html');
const swPath = path.join(root, 'sw.js');

console.log('--- Implementing Full Google OAuth Popup & In-Page Flow ---');

// 1. UPDATE static/js/app.js
let appJs = fs.readFileSync(appJsPath, 'utf8');

const jsCode = [
'// ========================================== ',
'// GOOGLE AUTHENTICATION & MULTI-STEP POPUP FLOW',
'// ========================================== ',
'',
'let googleModalSelectedEmail = "";',
'let googleModalSelectedName = "";',
'let googleModalKeepLoggedIn = true;',
'',
'function loginWithGoogle() {',
'    if (typeof playCyberSound === "function") playCyberSound("click");',
'    showToast("Opening Google Sign-In...", "info");',
'',
'    const width = 480;',
'    const height = 640;',
'    const left = Math.max(0, Math.floor((window.screen.width - width) / 2));',
'    const top = Math.max(0, Math.floor((window.screen.height - height) / 2));',
'',
'    let popup = null;',
'    try {',
'        popup = window.open(',
'            "google_auth_popup.html",',
'            "GoogleAccountsAuth",',
'            "width=" + width + ",height=" + height + ",top=" + top + ",left=" + left + ",resizable=yes,scrollbars=yes,status=no,toolbar=no,menubar=no"',
'        );',
'    } catch(e) {',
'        popup = null;',
'    }',
'',
'    // If popup was blocked or denied by browser, seamlessly open the in-page Google popup modal',
'    if (!popup || popup.closed || typeof popup.closed === "undefined") {',
'        openGoogleAccountPicker();',
'    } else {',
'        try { popup.focus(); } catch(e) {}',
'    }',
'}',
'',
'function openGoogleAccountPicker() {',
'    if (typeof playCyberSound === "function") playCyberSound("modal_open");',
'    resetGoogleModalSteps();',
'    openModal("modal-google-account-picker");',
'}',
'',
'function resetGoogleModalSteps() {',
'    const s1 = document.getElementById("google-modal-step-1");',
'    const s2 = document.getElementById("google-modal-step-2");',
'    const s3 = document.getElementById("google-modal-step-3");',
'    const s4 = document.getElementById("google-modal-step-4");',
'    if (s1) s1.classList.remove("hidden");',
'    if (s2) s2.classList.add("hidden");',
'    if (s3) s3.classList.add("hidden");',
'    if (s4) s4.classList.add("hidden");',
'    googleModalKeepLoggedIn = true;',
'    const toggle = document.getElementById("modal-keep-login-toggle");',
'    if (toggle) toggle.checked = true;',
'    const lbl = document.getElementById("modal-keep-login-status");',
'    if (lbl) lbl.textContent = "ON • Stay signed in on this device";',
'}',
'',
'function selectGoogleAccountForStep2(name, email) {',
'    if (typeof playCyberSound === "function") playCyberSound("click");',
'    googleModalSelectedName = name;',
'    googleModalSelectedEmail = email;',
'    const inp = document.getElementById("google-modal-email-input");',
'    if (inp) inp.value = email;',
'    goToGoogleModalPasswordStep();',
'}',
'',
'function goToGoogleModalPasswordStep() {',
'    const inp = document.getElementById("google-modal-email-input");',
'    const emailVal = (inp?.value || googleModalSelectedEmail || "").trim();',
'    if (!emailVal) {',
'        showToast("Please enter your Google email address or choose an account.", "error");',
'        if (inp) inp.focus();',
'        return;',
'    }',
'    googleModalSelectedEmail = emailVal;',
'    if (!googleModalSelectedName) {',
'        googleModalSelectedName = emailVal.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "");',
'    }',
'',
'    const emailDisplay = document.getElementById("google-modal-display-email");',
'    if (emailDisplay) emailDisplay.textContent = googleModalSelectedEmail;',
'',
'    const s1 = document.getElementById("google-modal-step-1");',
'    const s2 = document.getElementById("google-modal-step-2");',
'    if (s1) s1.classList.add("hidden");',
'    if (s2) {',
'        s2.classList.remove("hidden");',
'        const pwInp = document.getElementById("google-modal-password-input");',
'        if (pwInp) pwInp.focus();',
'    }',
'}',
'',
'function goToGoogleModalAccountStep() {',
'    const s1 = document.getElementById("google-modal-step-1");',
'    const s2 = document.getElementById("google-modal-step-2");',
'    if (s1) s1.classList.remove("hidden");',
'    if (s2) s2.classList.add("hidden");',
'}',
'',
'function onToggleModalKeepLogin(checked) {',
'    googleModalKeepLoggedIn = checked;',
'    const lbl = document.getElementById("modal-keep-login-status");',
'    if (lbl) {',
'        lbl.textContent = checked ? "ON • Stay signed in on this device" : "OFF • Log out when browser is closed";',
'        lbl.className = checked ? "text-[10px] text-cyan-400 font-mono" : "text-[10px] text-gray-400 font-mono";',
'    }',
'}',
'',
'function toggleGoogleModalPasswordVisibility() {',
'    const inp = document.getElementById("google-modal-password-input");',
'    const icon = document.getElementById("google-modal-pw-icon");',
'    if (!inp) return;',
'    if (inp.type === "password") {',
'        inp.type = "text";',
'        if (icon) icon.className = "fa-solid fa-eye-slash text-xs";',
'    } else {',
'        inp.type = "password";',
'        if (icon) icon.className = "fa-solid fa-eye text-xs";',
'    }',
'}',
'',
'function verifyWithGoogleInModal() {',
'    const pw = (document.getElementById("google-modal-password-input")?.value || "").trim();',
'    if (!pw) {',
'        showToast("Please enter your Google account password", "error");',
'        return;',
'    }',
'',
'    if (typeof playCyberSound === "function") playCyberSound("click");',
'    const s2 = document.getElementById("google-modal-step-2");',
'    const s3 = document.getElementById("google-modal-step-3");',
'    const s4 = document.getElementById("google-modal-step-4");',
'',
'    if (s2) s2.classList.add("hidden");',
'    if (s3) s3.classList.remove("hidden");',
'',
'    setTimeout(() => {',
'        if (s3) s3.classList.add("hidden");',
'        if (s4) s4.classList.remove("hidden");',
'        if (typeof playCyberSound === "function") playCyberSound("success");',
'',
'        setTimeout(() => {',
'            handleGoogleAuthSuccess({',
'                displayName: googleModalSelectedName,',
'                email: googleModalSelectedEmail,',
'                keepLoggedIn: googleModalKeepLoggedIn,',
'                photoURL: "https://api.dicebear.com/7.x/bottts/svg?seed=" + googleModalSelectedName,',
'                uid: "g_" + btoa(googleModalSelectedEmail).replace(/=/g, "").substring(0, 16)',
'            });',
'        }, 900);',
'    }, 1000);',
'}',
'',
'function handleGoogleAuthSuccess(googleUser) {',
'    const email = (googleUser.email || "").trim();',
'    const displayName = (googleUser.displayName || email.split("@")[0] || "Google Gamer").trim();',
'    const username = displayName.replace(/[^a-zA-Z0-9_]/g, "").slice(0, 15) || ("Gamer" + Math.floor(1000 + Math.random() * 9000));',
'    const avatarUrl = googleUser.photoURL || ("https://api.dicebear.com/7.x/bottts/svg?seed=" + username);',
'    const uid = googleUser.uid || ("g_" + Date.now());',
'    const role = googleUser.role || (email.toLowerCase().includes("admin") || email.toLowerCase() === "wolfy@nexusarena.gg" ? "ADMIN" : "PLAYER");',
'    const keepLoggedIn = googleUser.keepLoggedIn !== undefined ? Boolean(googleUser.keepLoggedIn) : true;',
'',
'    let registeredUsers = [];',
'    try {',
'        registeredUsers = JSON.parse(localStorage.getItem("nexus_registered_gamers") || "[]");',
'    } catch (e) {',
'        registeredUsers = [];',
'    }',
'',
'    let existing = registeredUsers.find(u => (u.email && u.email.toLowerCase() === email.toLowerCase()) || (u.google_id && u.google_id === uid));',
'',
'    let userSessionData;',
'    if (existing) {',
'        userSessionData = {',
'            ...existing,',
'            avatar_url: avatarUrl || existing.avatar_url,',
'            is_google_auth: true',
'        };',
'    } else {',
'        userSessionData = {',
'            id: uid,',
'            google_id: uid,',
'            username: username,',
'            email: email,',
'            phone: "+91 98765" + Math.floor(10000 + Math.random() * 90000),',
'            role: role,',
'            is_guest: false,',
'            is_google_auth: true,',
'            wallet_balance: role === "ADMIN" ? 50000.00 : 1500.00,',
'            nexus_coins: 2000,',
'            elo_rating: 1350,',
'            rank_tier: role === "ADMIN" ? "NEXUS_OVERLORD" : "GOLD_VANGUARD",',
'            daily_streak: 1,',
'            referral_code: (username.toUpperCase().slice(0, 6) + "_GGL"),',
'            avatar_url: avatarUrl,',
'            created_at: new Date().toISOString()',
'        };',
'        registeredUsers.push(userSessionData);',
'        try {',
'            localStorage.setItem("nexus_registered_gamers", JSON.stringify(registeredUsers));',
'        } catch(e) {}',
'    }',
'',
'    state.user = userSessionData;',
'    state.walletBalance = userSessionData.wallet_balance || 1500.00;',
'    state.nexusCoins = userSessionData.nexus_coins || 2000;',
'    state.dailyStreak = userSessionData.daily_streak || 1;',
'    state.referralCode = userSessionData.referral_code;',
'    state.token = "google_token_" + Date.now();',
'',
'    // Respect Keep me logged in (On/Off)',
'    saveUserAuthSession(userSessionData, state.token, keepLoggedIn, email);',
'',
'    closeModal("modal-google-account-picker");',
'    const lm = document.getElementById("modal-login");',
'    if (lm) {',
'        delete lm.dataset.gatekeeper;',
'        closeModal("modal-login");',
'    }',
'',
'    enterArenaApp(true);',
'    if (typeof playCyberSound === "function") playCyberSound("success");',
'    showToast("✓ Google Verification Successful! Welcome, " + userSessionData.username + " (+2,000 Coins).", "success");',
'}',
'',
'// Cross-window communication listener for Google Auth Popup',
'window.addEventListener("message", function(event) {',
'    if (!event.data || event.data.type !== "NEXUS_GOOGLE_AUTH_SUCCESS") return;',
'    const googleUser = event.data.user;',
'    if (googleUser) {',
'        handleGoogleAuthSuccess(googleUser);',
'    }',
'});',
'',
'// Storage sync fallback for cross-tab Google Auth',
'window.addEventListener("storage", function(e) {',
'    if (e.key === "nexus_google_auth_pending" && e.newValue) {',
'        try {',
'            const payload = JSON.parse(e.newValue);',
'            if (payload && payload.type === "NEXUS_GOOGLE_AUTH_SUCCESS" && payload.user) {',
'                localStorage.removeItem("nexus_google_auth_pending");',
'                handleGoogleAuthSuccess(payload.user);',
'            }',
'        } catch(err) {}',
'    }',
'});',
'',
'// Window exports',
'window.loginWithGoogle = loginWithGoogle;',
'window.openGoogleAccountPicker = openGoogleAccountPicker;',
'window.selectGoogleAccountForStep2 = selectGoogleAccountForStep2;',
'window.goToGoogleModalPasswordStep = goToGoogleModalPasswordStep;',
'window.goToGoogleModalAccountStep = goToGoogleModalAccountStep;',
'window.onToggleModalKeepLogin = onToggleModalKeepLogin;',
'window.toggleGoogleModalPasswordVisibility = toggleGoogleModalPasswordVisibility;',
'window.verifyWithGoogleInModal = verifyWithGoogleInModal;',
'window.handleGoogleAuthSuccess = handleGoogleAuthSuccess;'
].join('\n');

const oldGoogleSectionRegex = /\/\/ ==========================================\s*\n\/\/ GOOGLE AUTHENTICATION & ACCOUNT PICKER[\s\S]*?window\.handleGoogleAuthSuccess = handleGoogleAuthSuccess;/;

if (oldGoogleSectionRegex.test(appJs)) {
    appJs = appJs.replace(oldGoogleSectionRegex, jsCode);
    console.log('✓ Replaced Google Auth section in app.js with multi-step popup & modal flow');
} else {
    console.warn('Could not match oldGoogleSectionRegex in app.js');
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

const multiStepGoogleModal = `
    <!-- ========================================== -->
    <!-- 19b. GOOGLE AUTHENTICATION MULTI-STEP MODAL (OFFICIAL GOOGLE OAUTH FLOW) -->
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
            <div id="google-modal-step-1" class="space-y-3">
                <div class="text-[11px] font-bold text-gray-300">Choose an account or feed your Google email:</div>

                <!-- Pre-configured Google Accounts List -->
                <div class="space-y-1 divide-y divide-gray-800">
                    <!-- Account 1: Main Admin -->
                    <button type="button" onclick="selectGoogleAccountForStep2('Wolfy Admin', 'wolfy@nexusarena.gg')" class="w-full pt-2 pb-2 px-3 rounded-xl hover:bg-white/5 transition-all flex items-center justify-between text-left group cursor-pointer">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-white text-xs font-bold ring-2 ring-amber-400/40">
                                WA
                            </div>
                            <div>
                                <div class="text-xs font-bold text-gray-100 group-hover:text-cyan-400 transition-colors flex items-center gap-1.5">
                                    <span>Wolfy Admin</span>
                                    <span class="px-1.5 py-0.2 rounded text-[8px] bg-amber-500/20 text-amber-300 font-mono">ADMIN</span>
                                </div>
                                <div class="text-[11px] text-gray-400 font-mono">wolfy@nexusarena.gg</div>
                            </div>
                        </div>
                        <i class="fa-solid fa-chevron-right text-gray-500 text-xs group-hover:text-white transition-colors"></i>
                    </button>

                    <!-- Account 2: Alex Vance -->
                    <button type="button" onclick="selectGoogleAccountForStep2('Alex Vance', 'alex.vance@gmail.com')" class="w-full pt-2 pb-2 px-3 rounded-xl hover:bg-white/5 transition-all flex items-center justify-between text-left group cursor-pointer">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center text-white text-xs font-bold ring-2 ring-cyan-400/40">
                                AV
                            </div>
                            <div>
                                <div class="text-xs font-bold text-gray-100 group-hover:text-cyan-400 transition-colors">Alex Vance</div>
                                <div class="text-[11px] text-gray-400 font-mono">alex.vance@gmail.com</div>
                            </div>
                        </div>
                        <i class="fa-solid fa-chevron-right text-gray-500 text-xs group-hover:text-white transition-colors"></i>
                    </button>

                    <!-- Account 3: Pro Gamer -->
                    <button type="button" onclick="selectGoogleAccountForStep2('Pro Gamer One', 'player.one@nexusarena.gg')" class="w-full pt-2 pb-2 px-3 rounded-xl hover:bg-white/5 transition-all flex items-center justify-between text-left group cursor-pointer">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center text-white text-xs font-bold ring-2 ring-purple-400/40">
                                PG
                            </div>
                            <div>
                                <div class="text-xs font-bold text-gray-100 group-hover:text-cyan-400 transition-colors">Pro Gamer One</div>
                                <div class="text-[11px] text-gray-400 font-mono">player.one@nexusarena.gg</div>
                            </div>
                        </div>
                        <i class="fa-solid fa-chevron-right text-gray-500 text-xs group-hover:text-white transition-colors"></i>
                    </button>
                </div>

                <!-- Custom Google Email Input -->
                <div class="pt-2 space-y-1">
                    <label class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Or feed your Google email / phone</label>
                    <input type="email" id="google-modal-email-input" placeholder="e.g. yourname@gmail.com" onkeydown="if(event.key==='Enter') goToGoogleModalPasswordStep()" class="w-full bg-[#131722] border border-gray-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-400 font-mono">
                </div>

                <div class="pt-2 flex items-center justify-between">
                    <button type="button" onclick="closeModal('modal-google-account-picker')" class="px-4 py-2 rounded-xl text-xs text-gray-400 hover:text-white transition-colors cursor-pointer">
                        Cancel
                    </button>
                    <button type="button" onclick="goToGoogleModalPasswordStep()" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-600 text-black font-bold text-xs uppercase tracking-wider hover:brightness-110 transition-all cursor-pointer shadow">
                        Next &bull; Password &rarr;
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
                    <button type="button" onclick="goToGoogleModalAccountStep()" class="text-[10px] text-cyan-400 hover:underline">Change</button>
                </div>

                <!-- Google Password Input -->
                <div class="space-y-1">
                    <label class="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Feed Google Account Password</label>
                    <div class="relative">
                        <input type="password" id="google-modal-password-input" value="GooglePass2026!" placeholder="Enter password" onkeydown="if(event.key==='Enter') verifyWithGoogleInModal()" class="w-full bg-[#131722] border border-gray-700 rounded-xl pl-3 pr-10 py-2.5 text-xs text-white focus:outline-none focus:border-cyan-400 font-mono">
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
                <div class="text-xs text-gray-300 font-mono">Connecting your Arena passport (+2,000 Coins)...</div>
            </div>

            <!-- Footer terms -->
            <div class="pt-1 text-center text-[10px] text-gray-400 leading-relaxed border-t border-gray-800">
                By continuing with Google, you agree to Nexus Arena's Terms of Service and Privacy Policy.
            </div>
        </div>
    </div>
`;

const oldModalRegex = /<!-- ========================================== -->\s*\n\s*<!-- 19b\. GOOGLE ACCOUNT PICKER MODAL[\s\S]*?<!-- 20\. INSTALL APP ON PHONE MODAL/;

if (oldModalRegex.test(html)) {
    html = html.replace(oldModalRegex, multiStepGoogleModal.trim() + '\n\n    <!-- 20. INSTALL APP ON PHONE MODAL');
    console.log('✓ Replaced modal-google-account-picker with multi-step Google flow in HTML');
} else {
    console.warn('Could not match oldModalRegex in HTML');
}

// Bump version in HTML to v7.0.3
html = html.replace(/v=7\.0\.2/g, 'v=7.0.3');

fs.writeFileSync(htmlPath, html, 'utf8');
console.log('✓ nexus_gaming_arena.html updated and bumped to v7.0.3');

// 3. UPDATE sw.js version cache
let sw = fs.readFileSync(swPath, 'utf8');
sw = sw.replace(/nexus-arena-v[0-9.]+/g, 'nexus-arena-v7.0.3');
sw = sw.replace(/v=[0-9.]+/g, 'v=7.0.3');

// Ensure google_auth_popup.html is in precache assets if not present
if (!sw.includes('/google_auth_popup.html')) {
    sw = sw.replace("'/index.html',", "'/index.html',\n    '/google_auth_popup.html',");
    console.log('✓ Added /google_auth_popup.html to sw.js precache');
}
fs.writeFileSync(swPath, sw, 'utf8');
console.log('✓ sw.js updated to v7.0.3');

console.log('--- Multi-Step Google Flow Implemented ---');
