# ⚡ Nexus Gaming Arena - Rajendran's Ultimate Gaming Platform (V2.0)

A high-concurrency, security-first competitive gaming platform featuring the custom **Cyberpunk Dark & Orbitron UI** seamlessly connected to an enterprise **Python FastAPI**, **Double-Entry Bookkeeping Ledger**, **RFC 6238 TOTP 2FA**, **Live Elimination Brackets**, and **Real-Time WebSockets**.

---

## 🎨 UI & Design Ideology Synthesis

The platform synthesizes the strengths of leading esports websites without trademark cloning:
* **PUBG ([pubg.com](https://pubg.com/en/main)):** Tactical rugged aesthetic, 45-degree angled polygon bevels (`.tactical-cut`), live countdown clocks to grand finals, and high-frequency scanline matrix overlays.
* **GamerConnect ([gamerconnect.in](https://gamerconnect.in/)):** High-energy RGB cyber glows, interactive community metrics banner (14,280+ active gamers, ₹25 Lakhs+ distributed, 12ms WebSocket latency), and light-sweep buttons (`.btn-sweep`).
* **GamerFlick ([gamerflick.in](https://www.gamerflick.in/)):**
  - **Dual-Currency Economy:** Seamless coexistence of **Real INR Cash (₹)** in double-entry escrow and **Nexus Coins (🪙)** for daily activity.
  - **Daily Quests & Check-in Streaks:** Day 4 streak multiplier (+50 to +150 Coins) with instant reward claims.
  - **Battleground Metadata:** Dedicated tags for game modes (`BGMI · Squad (TPP)`, `Valorant · 5v5 Comp`, `CS2 · Wingman 2v2`), maps (`Erangel`, `Bind`, `Mirage`), server locations (`Mumbai AWS`), and `🔥 FILLING FAST` animated slot capacity bars.
  - **Squad Referral Boost:** Clan invite code (`RAJENDRAN_PRO`) granting +150 bonus coins to both players.
  - **Coin Redeem Shop:** Exchange tokens for free tournament entry passes, ₹100 wallet credits, Valorant points, or BGMI UC.
* **Mobile-First Touch Architecture:** 5-button thumb-accessible bottom navigation bar (*Arenas, Coin Hub, Ranks, Shorts, Vault*).

---

## 🛡️ Internal Features Matrix (All 14 Core Requirements)

1. **Event Organising:** Organizers can host tournaments across PC & mobile games (*Valorant, PUBG Mobile, CS2, Free Fire, Apex, COD Mobile*), locking verified prize pool escrow.
2. **Tournament Engine:** Single-elimination binary tree bracket generator, match progression, live score reporting with screenshot evidence, and referee dispute freezes.
3. **Accounts & Security:** Salted PBKDF2-HMAC-SHA256 password hashing (600,000 rounds, OWASP standard) and stateless, tamper-proof HMAC-SHA256 session tokens.
4. **Top Players Showcase:** Podium highlights showcasing the top champions, tournament trophies, win rates, and Elo MMR ratings.
5. **Leaderboard:** Low-latency ranking engine with Elo rating progression ($K=32$) and Discord/Steam/Twitch tags.
6. **Gameplay Videos & Shorts:** Vertical swipe gameplay video player with volume toggle, live like counters, and clip uploader.
7. **Social Media Connections:** One-click integration with Discord, Steam ID64, Twitch channels, and Google Riot.
8. **Website Security:** Hardened with Content Security Policy (CSP), X-Frame-Options (Clickjacking defense), X-Content-Type-Options (MIME sniffing defense), and IP sliding-window rate limiting.
9. **Two-Factor Authentication (2FA):** Real RFC 6238 compliant TOTP using `pyotp` with scannable QR codes for Google Authenticator, Microsoft Authenticator, and Authy.
10. **OTP & Phone Verification:** Cryptographically secure 6-digit OTP verification system with expiration and attempt limiting.
11. **Mobile & PC Responsive (PWA):** Responsive CSS Grid & Flexbox with desktop widescreen brackets and mobile-first bottom navigation drawer. Includes PWA manifest.
12. **Payment Gateway Integration:** Multi-gateway support (UPI, GPay, Razorpay, Paytm, and Stripe) with instant deposit buttons (`₹500`, `₹1,000`, `₹5,000`).
13. **High-End Financial Security:** Immutable **Double-Entry Bookkeeping Ledger** where every transaction records matching debits and credits.
14. **Zero-Failure & Crash Prevention:**
    - Every financial mutation requires a unique **UUID Idempotency Key** to prevent duplicate charges from network retries.
    - Global exception shielding catches any unhandled errors gracefully without crashing the server process.

---

## ⚡ Launch Instructions

### 1. Launch with One Click
Double click:
```cmd
start_nexus_arena.bat
```

Or run via terminal:
```bash
cd "e:\OfficeServerSuite V2.0\NexusGamingArena"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8088
```

Open your browser at: **`http://127.0.0.1:8088`**

### 2. Default Seed Accounts
| Username | Password | Role | Starter Balance | 2FA Status |
| :--- | :--- | :--- | :--- | :--- |
| `Rajendran_God` | `password123` | Ranked #1 Champion (Rajendran Pro) | ₹35,000.00 | Active (Google Authenticator) |
| `admin` | `admin` | Platform Admin / Host | ₹10,00,000.00 | Ready to setup |
| `CyberPhoenix` | `password123` | Ranked #2 Champion | ₹5,000.00 | Active |
| `ShadowStriker`| `password123` | Ranked #3 Champion | ₹5,000.00 | Ready to setup |
