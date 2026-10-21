"""
Cleans hardcoded demo/fake stats and mock 'Wolfy' references from HTML and JavaScript.
"""

def clean_html():
    with open('nexus_gaming_arena.html', 'r', encoding='utf-8') as f:
        text = f.read()

    replacements = [
        ("Nexus Gaming Arena | Wolfy's Ultimate Gaming Platform", "Nexus Gaming Arena | Premier Esports & Competitive Gaming Platform"),
        ("Wolfy's Ultimate Gaming Platform", "Premier Esports & Competitive Gaming Platform"),
        ("Wolfy Esports Tech", "Nexus Gaming Arena Tech"),
        ("Direct Chat with Admin Wolfy", "Direct Chat with Arena Administrator"),
        ("Direct WhatsApp Support with Admin Wolfy", "Direct WhatsApp Support with Arena Operations"),
        ("Instant VIP chat with Admin Wolfy &amp; the Operations Referee", "Instant VIP chat with Arena Administrator &amp; the Operations Referee"),
        ("Founded by Wolfy in Bengaluru, Nexus Gaming Arena has officially opened registrations", "Founded in Bengaluru, Nexus Gaming Arena has officially opened registrations"),
        ("Nexus Gaming Arena is India's premier competitive esports ecosystem founded by Wolfy.", "Nexus Gaming Arena is India's premier competitive esports ecosystem."),
        ("WOLFY CLUTCHED ₹25,000 IN GRAND FINALS", "TOURNAMENT PRIZE ESCROW 100% RBI COMPLIANT"),
        ("14,280 PRO GAMERS ONLINE RIGHT NOW", "OFFICIAL COMPETITIVE SEASONS LIVE"),
        ("14,280 PROS ONLINE", "LIVE COMPETITIVE ARENA"),
        ("14,280+", "Live Arena"),
        ("Team Wolfy Clutch", "Team Apex Clutch"),
        ('MVP: <strong class="text-cyan-400">Wolfy</strong>', 'MVP: <strong class="text-cyan-400">ArenaPro</strong>'),
        ("Executive Console &bull; Wolfy Pro", "Executive Console &bull; Master Admin"),
        ("Shown for Wolfy / Admin", "Shown for Platform Administrator"),
        ("@Wolfy", "@Admin"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    with open('nexus_gaming_arena.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("[OK] nexus_gaming_arena.html cleaned of demo branding and stats.")

def clean_js():
    with open('static/js/app.js', 'r', encoding='utf-8') as f:
        text = f.read()

    # Empty out fake demo leaderboards and demo videos
    text = text.replace(
        "const DEMO_LEADERBOARD = [\n    { rank: 1, username: \"Wolfy\", rating: 2850, elo_rating: 2850, trophies: 15, tournaments_won: 15, win_rate: 88, earnings: 125000, avatar_url: \"https://api.dicebear.com/7.x/bottts/svg?seed=Wolfy\", badge: \"👑 ARENA CHAMPION\", fav_game: \"Valorant\" },\n    { rank: 2, username: \"CyberPhoenix\", rating: 2740, elo_rating: 2740, trophies: 11, tournaments_won: 11, win_rate: 82, earnings: 95000, avatar_url: \"https://api.dicebear.com/7.x/bottts/svg?seed=CyberPhoenix\", badge: \"🔥 GRAND MASTER\", fav_game: \"BGMI\" },\n    { rank: 3, username: \"ShadowStriker\", rating: 2680, elo_rating: 2680, trophies: 9, tournaments_won: 9, win_rate: 79, earnings: 70000, avatar_url: \"https://api.dicebear.com/7.x/bottts/svg?seed=ShadowStriker\", badge: \"⚡ MASTER PRO\", fav_game: \"CS2\" },\n    { rank: 4, username: \"ViperQueen\", rating: 2590, elo_rating: 2590, trophies: 7, tournaments_won: 7, win_rate: 76, earnings: 50000, avatar_url: \"https://api.dicebear.com/7.x/bottts/svg?seed=ViperQueen\", badge: \"DIAMOND ELITE\", fav_game: \"Valorant\" },\n    { rank: 5, username: \"ApexPredator\", rating: 2510, elo_rating: 2510, trophies: 6, tournaments_won: 6, win_rate: 73, earnings: 40000, avatar_url: \"https://api.dicebear.com/7.x/bottts/svg?seed=ApexPredator\", badge: \"DIAMOND ELITE\", fav_game: \"Apex Legends\" },\n    { rank: 6, username: \"NexusTitan\", rating: 2450, elo_rating: 2450, trophies: 5, tournaments_won: 5, win_rate: 71, earnings: 35000, avatar_url: \"https://api.dicebear.com/7.x/bottts/svg?seed=NexusTitan\", badge: \"PLATINUM I\", fav_game: \"Free Fire\" },\n    { rank: 7, username: \"PixelSniper\", rating: 2390, elo_rating: 2390, trophies: 4, tournaments_won: 4, win_rate: 68, earnings: 25000, avatar_url: \"https://api.dicebear.com/7.x/bottts/svg?seed=PixelSniper\", badge: \"PLATINUM II\", fav_game: \"COD Mobile\" }\n];",
        "const DEMO_LEADERBOARD = [];"
    )

    # Empty out fake demo videos
    if "const DEMO_VIDEOS = [" in text:
        import re
        text = re.sub(r'const DEMO_VIDEOS = \[.*?\];', 'const DEMO_VIDEOS = [];', text, flags=re.DOTALL)

    # Update community pulse from fake 14280 / 2500000
    text = text.replace("active_gamers: 14280,", "active_gamers: 1,")
    text = text.replace("total_prize_pool_dollars: 2500000,", "total_prize_pool_dollars: 0,")
    text = text.replace('trending_now_label: "BGMI National Masters"', 'trending_now_label: "Season 1 Inaugural Launch"')

    with open('static/js/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("[OK] static/js/app.js cleaned of demo arrays.")

if __name__ == "__main__":
    clean_html()
    clean_js()
