"""
========================================================================
NEXUS GAMING ARENA - SUPABASE 1-CLICK UPLOADER
Walks you through uploading the website to Supabase Storage with zero hassle.
========================================================================
"""

import os
import sys
import webbrowser
from pathlib import Path
import mimetypes

try:
    import httpx
except ImportError:
    httpx = None

try:
    import requests
except ImportError:
    requests = None

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

def print_banner():
    print("\n" + "=" * 65)
    print("   🎮 NEXUS GAMING ARENA - SUPABASE 1-CLICK UPLOADER")
    print("=" * 65 + "\n")

def get_supabase_credentials():
    url = ""
    key = ""

    # Check if already present in .env
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("SUPABASE_URL=") and not "your-project-ref" in line:
                    url = line.split("=", 1)[1].strip().strip("'\"")
                elif line.startswith("SUPABASE_ANON_KEY=") and not "your_actual_anon_key" in line and not "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." in line:
                    key = line.split("=", 1)[1].strip().strip("'\"")

    if url and key:
        print(f"[+] Using Supabase Project credentials from .env:")
        print(f"    URL: {url}")
        print(f"    Key: {key[:15]}...{key[-5:] if len(key)>20 else ''}")
        return url, key

    print("Please paste the 2 items from your Supabase Dashboard:")
    print(" (Dashboard -> Project Settings ⚙️ -> API)\n")

    while not url:
        url_input = input("1. Enter your Project URL (e.g. https://xyz.supabase.co): ").strip()
        if url_input.startswith("http"):
            url = url_input.rstrip("/")
        else:
            print("   [!] Please enter a valid URL starting with https://")

    while not key:
        key_input = input("\n2. Enter your anon public API Key (starts with eyJ... or sb_publishable_...): ").strip()
        if len(key_input) > 20:
            key = key_input
        else:
            print("   [!] Key looks too short. Make sure to copy the full key.")

    # Save to .env
    env_content = f"""# NEXUS GAMING ARENA ENVIRONMENT CONFIGURATION
NEXUS_PORT=8088
NEXUS_SECRET_KEY=nexus-super-secure-production-grade-secret-key-2026-esports

# Supabase Project Credentials
SUPABASE_URL={url}
SUPABASE_ANON_KEY={key}
SUPABASE_SERVICE_ROLE_KEY={key}
"""
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(env_content)
    print("\n[+] Credentials safely saved to .env!")

    return url, key

def upload_file(client, supabase_url: str, api_key: str, bucket: str, local_path: Path, storage_path: str):
    url = f"{supabase_url.rstrip('/')}/storage/v1/object/{bucket}/{storage_path}"
    content_type, _ = mimetypes.guess_type(str(local_path))
    content_type = content_type or "application/octet-stream"

    with open(local_path, "rb") as f:
        file_bytes = f.read()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "apikey": api_key,
        "Content-Type": content_type,
        "x-upsert": "true"
    }

    if httpx:
        res = client.post(url, content=file_bytes, headers=headers)
    else:
        res = client.post(url, data=file_bytes, headers=headers)

    success = res.status_code in (200, 201)
    status_code = res.status_code
    text = res.text

    if success:
        public_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket}/{storage_path}"
        print(f"  [✓] Uploaded: {storage_path} ({len(file_bytes):,} bytes)")
        return True, public_url, None
    else:
        print(f"  [✗] Failed {storage_path} (HTTP {status_code}): {text}")
        return False, None, text

def main():
    print_banner()
    supabase_url, api_key = get_supabase_credentials()

    bucket = "nexus-arena"
    print(f"\n[*] Preparing Supabase Storage bucket '{bucket}'...")

    client = httpx.Client(timeout=30.0) if httpx else requests.Session()

    # Files to upload
    files_to_upload = [
        (BASE_DIR / "nexus_gaming_arena.html", "index.html"),
        (BASE_DIR / "static" / "css" / "style.css", "static/css/style.css"),
        (BASE_DIR / "static" / "js" / "app.js", "static/js/app.js"),
        (BASE_DIR / "static" / "manifest.json", "static/manifest.json")
    ]

    while True:
        print(f"\n[*] Uploading website assets to Supabase CDN bucket '{bucket}'...")
        success_count = 0
        total_count = len(files_to_upload)
        rls_error = False
        live_index_url = None

        for local_file, remote_path in files_to_upload:
            if local_file.exists():
                ok, pub_url, err_msg = upload_file(client, supabase_url, api_key, bucket, local_file, remote_path)
                if ok:
                    success_count += 1
                    if remote_path == "index.html":
                        live_index_url = pub_url
                else:
                    if err_msg and ("row-level security" in err_msg.lower() or "unauthorized" in err_msg.lower()):
                        rls_error = True

        if success_count == total_count:
            print("\n" + "=" * 65)
            print("  🎉 SUCCESS! ALL WEBSITE ASSETS UPLOADED TO SUPABASE!")
            print("=" * 65)
            if live_index_url:
                print(f"\nYour Live Testing Website URL:\n👉 {live_index_url}\n")
                print("Opening your website in your browser...")
                try:
                    webbrowser.open(live_index_url)
                except Exception:
                    pass
            print("=" * 65 + "\n")
            break

        if rls_error:
            print("\n" + "-" * 65)
            print("  🔒 SUPABASE STORAGE PERMISSION (RLS) NEEDED")
            print("-" * 65)
            print("Supabase blocks uploads with public/anon keys until a policy is added.")
            print("To fix this in 10 seconds:\n")
            print("1. Open Supabase SQL Editor: https://supabase.com/dashboard/project/exrzgubjuhjyvfwqlntc/sql")
            print("2. Paste and Run this SQL query:\n")
            print("-" * 65)
            print("""CREATE POLICY "Public Upload nexus-arena" ON storage.objects 
FOR INSERT TO public WITH CHECK (bucket_id = 'nexus-arena');

CREATE POLICY "Public Select nexus-arena" ON storage.objects 
FOR SELECT TO public USING (bucket_id = 'nexus-arena');

CREATE POLICY "Public Update nexus-arena" ON storage.objects 
FOR UPDATE TO public USING (bucket_id = 'nexus-arena');""")
            print("-" * 65)
            print("(A file named 'enable_storage_policy.sql' has also been created for you)")
            print("\nAfter clicking 'Run' in your Supabase SQL Editor:")
            retry = input("Press [Enter] to retry uploading now (or type 'q' to quit): ").strip().lower()
            if retry == 'q':
                print("[*] Upload cancelled. You can run setup_supabase.py anytime.")
                break
        else:
            print(f"\n[!] Uploaded {success_count}/{total_count} files.")
            retry = input("Press [Enter] to retry (or type 'q' to quit): ").strip().lower()
            if retry == 'q':
                break

if __name__ == "__main__":
    main()
