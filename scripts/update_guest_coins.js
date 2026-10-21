const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const htmlPath = path.join(root, 'nexus_gaming_arena.html');
const appJsPath = path.join(root, 'static', 'js', 'app.js');
const swPath = path.join(root, 'sw.js');

console.log('--- Updating Guest Coins from 500 to 100 ---');

// 1. UPDATE static/js/app.js
let appJs = fs.readFileSync(appJsPath, 'utf8');

// In handleLandingPlayAsGuest:
const oldLandingGuestCoins = `    const guestUser = {
        id: guestId,
        username: guestUsername,
        email: \`\${guestUsername.toLowerCase()}@guest.nexusarena.gg\`,
        phone: "+91 9000000000",
        role: "GUEST",
        is_guest: true,
        wallet_balance: 0.00,
        nexus_coins: 500, // Starter Welcome Coins!
        elo_rating: 1000,
        rank_tier: "BRONZE_RECRUIT",
        daily_streak: 1,
        referral_code: \`GUEST_\${randomTag}\`,
        avatar_url: \`https://api.dicebear.com/7.x/bottts/svg?seed=\${guestUsername}\`,
        created_at: new Date().toISOString()
    };

    state.user = guestUser;
    state.walletBalance = 0.00;
    state.nexusCoins = 500;
    state.dailyStreak = 1;
    state.referralCode = guestUser.referral_code;

    localStorage.setItem("nexus_user", JSON.stringify(guestUser));
    sessionStorage.setItem("nexus_active_session", "true");

    enterArenaApp();
    if (typeof playCyberSound === 'function') playCyberSound('success');
    showToast(\`⚡ Guest Pass Activated: Welcome \${guestUsername}! +500 Starter Welcome Coins credited.\`, "success");`;

const newLandingGuestCoins = `    const guestUser = {
        id: guestId,
        username: guestUsername,
        email: \`\${guestUsername.toLowerCase()}@guest.nexusarena.gg\`,
        phone: "+91 9000000000",
        role: "GUEST",
        is_guest: true,
        wallet_balance: 0.00,
        nexus_coins: 100, // Starter Welcome Coins!
        elo_rating: 1000,
        rank_tier: "BRONZE_RECRUIT",
        daily_streak: 1,
        referral_code: \`GUEST_\${randomTag}\`,
        avatar_url: \`https://api.dicebear.com/7.x/bottts/svg?seed=\${guestUsername}\`,
        created_at: new Date().toISOString()
    };

    state.user = guestUser;
    state.walletBalance = 0.00;
    state.nexusCoins = 100;
    state.dailyStreak = 1;
    state.referralCode = guestUser.referral_code;

    localStorage.setItem("nexus_user", JSON.stringify(guestUser));
    sessionStorage.setItem("nexus_active_session", "true");

    enterArenaApp();
    if (typeof playCyberSound === 'function') playCyberSound('success');
    showToast(\`⚡ Guest Pass Activated: Welcome \${guestUsername}! +100 Starter Welcome Coins credited.\`, "success");`;

if (appJs.includes(oldLandingGuestCoins)) {
    appJs = appJs.replace(oldLandingGuestCoins, newLandingGuestCoins);
    console.log('✓ Updated handleLandingPlayAsGuest coins to 100');
} else {
    console.warn('Could not match oldLandingGuestCoins in app.js');
}

// In handlePlayAsGuest:
const oldModalGuestCoins = `    const guestUser = {
        id: guestId,
        username: guestUsername,
        email: \`\${guestUsername.toLowerCase()}@guest.nexusarena.gg\`,
        phone: "+91 9000000000",
        role: "GUEST",
        is_guest: true,
        wallet_balance: 0.00,
        nexus_coins: 500, // Starter Welcome Coins!
        elo_rating: 1000,
        rank_tier: "BRONZE_RECRUIT",
        daily_streak: 1,
        referral_code: \`GUEST_\${randomTag}\`,
        avatar_url: \`https://api.dicebear.com/7.x/bottts/svg?seed=\${guestUsername}\`,
        created_at: new Date().toISOString()
    };

    state.user = guestUser;
    state.walletBalance = 0.00;
    state.nexusCoins = 500;
    state.dailyStreak = 1;
    state.referralCode = guestUser.referral_code;

    localStorage.setItem("nexus_user", JSON.stringify(guestUser));
    sessionStorage.setItem("nexus_active_session", "true");

    // Remove gatekeeper lock
    const loginModal = document.getElementById("modal-login");
    if (loginModal) {
        delete loginModal.dataset.gatekeeper;
        const closeBtn = document.getElementById("modal-login-close-btn");
        if (closeBtn) closeBtn.style.display = "";
    }

    closeModal("modal-login");
    enterArenaApp();
    if (typeof playCyberSound === 'function') playCyberSound('success');
    showToast(\`⚡ Guest Pass Activated: Welcome \${guestUsername}! +500 Starter Welcome Coins credited.\`, "success");`;

const newModalGuestCoins = `    const guestUser = {
        id: guestId,
        username: guestUsername,
        email: \`\${guestUsername.toLowerCase()}@guest.nexusarena.gg\`,
        phone: "+91 9000000000",
        role: "GUEST",
        is_guest: true,
        wallet_balance: 0.00,
        nexus_coins: 100, // Starter Welcome Coins!
        elo_rating: 1000,
        rank_tier: "BRONZE_RECRUIT",
        daily_streak: 1,
        referral_code: \`GUEST_\${randomTag}\`,
        avatar_url: \`https://api.dicebear.com/7.x/bottts/svg?seed=\${guestUsername}\`,
        created_at: new Date().toISOString()
    };

    state.user = guestUser;
    state.walletBalance = 0.00;
    state.nexusCoins = 100;
    state.dailyStreak = 1;
    state.referralCode = guestUser.referral_code;

    localStorage.setItem("nexus_user", JSON.stringify(guestUser));
    sessionStorage.setItem("nexus_active_session", "true");

    // Remove gatekeeper lock
    const loginModal = document.getElementById("modal-login");
    if (loginModal) {
        delete loginModal.dataset.gatekeeper;
        const closeBtn = document.getElementById("modal-login-close-btn");
        if (closeBtn) closeBtn.style.display = "";
    }

    closeModal("modal-login");
    enterArenaApp();
    if (typeof playCyberSound === 'function') playCyberSound('success');
    showToast(\`⚡ Guest Pass Activated: Welcome \${guestUsername}! +100 Starter Welcome Coins credited.\`, "success");`;

if (appJs.includes(oldModalGuestCoins)) {
    appJs = appJs.replace(oldModalGuestCoins, newModalGuestCoins);
    console.log('✓ Updated handlePlayAsGuest coins to 100');
} else {
    console.warn('Could not match oldModalGuestCoins in app.js');
}

fs.writeFileSync(appJsPath, appJs, 'utf8');

// 2. UPDATE nexus_gaming_arena.html
let html = fs.readFileSync(htmlPath, 'utf8');

// A. Landing Page Guest Button badge
html = html.replace(
    `<span class="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-mono font-bold">+500 COINS</span>`,
    `<span class="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-mono font-bold">+100 COINS</span>`
);

// B. Modal Login Guest Button badge
html = html.replace(
    `<span class="text-[9px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono font-bold">+500 COINS</span>`,
    `<span class="text-[9px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono font-bold">+100 COINS</span>`
);

// C. Header fast bootstrap script
html = html.replace(
    `u.is_guest?500:1000`,
    `u.is_guest?100:1000`
);

// D. Session fast bootstrap script
html = html.replace(
    `u.is_guest ? 500 : 1000`,
    `u.is_guest ? 100 : 1000`
);

// E. Guest active top sticky banner
html = html.replace(
    `Starter <span class="text-cyan-400 font-bold font-mono">500 Nexus Coins</span> active.`,
    `Starter <span class="text-cyan-400 font-bold font-mono">100 Nexus Coins</span> active.`
);

// F. Guest upgrade modal text
html = html.replace(
    `Keep your <strong class="text-cyan-400">500 Coins</strong>`,
    `Keep your <strong class="text-cyan-400">100 Coins</strong>`
);

// Bump version in HTML to v7.0.2
html = html.replace(/v=7\.0\.1/g, 'v=7.0.2');

fs.writeFileSync(htmlPath, html, 'utf8');
console.log('✓ nexus_gaming_arena.html updated with 100 coins for guests and bumped to v7.0.2');

// 3. UPDATE sw.js version cache
let sw = fs.readFileSync(swPath, 'utf8');
sw = sw.replace(/nexus-arena-v[0-9.]+/g, 'nexus-arena-v7.0.2');
sw = sw.replace(/v=[0-9.]+/g, 'v=7.0.2');
fs.writeFileSync(swPath, sw, 'utf8');
console.log('✓ sw.js updated to v7.0.2');

console.log('--- Guest Coins Update Completed ---');
