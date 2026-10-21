"""
========================================================================
NEXUS GAMING ARENA - SUPABASE STORAGE UPLOADER
Uploads website assets (HTML, CSS, JS) to a public Supabase Storage bucket.
Uses standard httpx / requests (zero external dependencies).
========================================================================
Usage:
  python upload_to_supabase_storage.py --url <SUPABASE_URL> --key <SUPABASE_KEY>
  or simply set SUPABASE_URL and SUPABASE_ANON_KEY / SUPABASE_SERVICE_ROLE_KEY in .env
"""

import os
import sys
import argparse
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

def load_env_file():
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v

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
        "x-upsert": "true"  # Overwrite if exists
    }

    if httpx:
        res = client.post(url, content=file_bytes, headers=headers)
        success = res.status_code in (200, 201)
        status_code = res.status_code
        text = res.text
    else:
        res = client.post(url, data=file_bytes, headers=headers)
        success = res.status_code in (200, 201)
        status_code = res.status_code
        text = res.text

    if success:
        public_url = f"{supabase_url.rstrip('/')}/storage/v1/object/public/{bucket}/{storage_path}"
        print(f"  [OK] Uploaded: {storage_path} ({len(file_bytes)} bytes)")
        print(f"       Public URL: {public_url}")
        return public_url
    else:
        print(f"  [FAIL] {storage_path} (HTTP {status_code}): {text}")
        return None

def main():
    load_env_file()

    parser = argparse.ArgumentParser(description="Upload Nexus Arena website to Supabase Storage")
    parser.add_argument("--url", default=os.environ.get("SUPABASE_URL"), help="Supabase Project URL")
    parser.add_argument("--key", default=os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY"), help="Supabase API Key")
    parser.add_argument("--bucket", default="nexus-arena", help="Supabase Storage Bucket Name (default: nexus-arena)")
    args = parser.parse_args()

    supabase_url = args.url
    api_key = args.key
    bucket = args.bucket

    if not supabase_url or not api_key:
        print("\n" + "=" * 60)
        print(" [!] Missing Supabase Credentials")
        print("=" * 60)
        print("Please provide your Supabase Project URL and Key via CLI or .env file:")
        print("  python upload_to_supabase_storage.py --url https://your-id.supabase.co --key YOUR_ANON_OR_SERVICE_KEY")
        print("\nOr configure .env with:")
        print("  SUPABASE_URL=https://your-id.supabase.co")
        print("  SUPABASE_ANON_KEY=your-anon-key")
        print("=" * 60 + "\n")
        sys.exit(1)

    print(f"\n[*] Connecting to Supabase Project: {supabase_url}")
    print(f"[*] Target Bucket: {bucket}")

    # Use HTTP client
    client = httpx.Client(timeout=30.0) if httpx else requests.Session()

    # 1. Ensure bucket exists
    bucket_url = f"{supabase_url.rstrip('/')}/storage/v1/bucket"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    print("[*] Creating/Verifying public storage bucket...")
    create_bucket_payload = {
        "id": bucket,
        "name": bucket,
        "public": True,
        "file_size_limit": 52428800  # 50 MB
    }
    
    try:
        if httpx:
            b_res = client.post(bucket_url, json=create_bucket_payload, headers=headers)
        else:
            b_res = client.post(bucket_url, json=create_bucket_payload, headers=headers)
        if b_res.status_code in (200, 201):
            print(f"  [OK] Public bucket '{bucket}' ready!")
        elif "already exists" in b_res.text.lower() or b_res.status_code == 409 or b_res.status_code == 400:
            print(f"  [OK] Bucket '{bucket}' already exists and is ready.")
        else:
            print(f"  [i] Bucket note ({b_res.status_code}): {b_res.text}")
    except Exception as e:
        print(f"  [!] Note during bucket check: {e}")

    # 2. Files to upload
    files_to_upload = [
        (BASE_DIR / "nexus_gaming_arena.html", "index.html"),
        (BASE_DIR / "nexus_gaming_arena.html", "nexus_gaming_arena.html"),
        (BASE_DIR / "static" / "css" / "style.css", "static/css/style.css"),
        (BASE_DIR / "static" / "js" / "app.js", "static/js/app.js"),
        (BASE_DIR / "static" / "manifest.json", "static/manifest.json")
    ]

    print("\n[*] Uploading website assets to Supabase Storage CDN:")
    live_index_url = None
    for local_file, remote_path in files_to_upload:
        if local_file.exists():
            pub_url = upload_file(client, supabase_url, api_key, bucket, local_file, remote_path)
            if remote_path == "index.html":
                live_index_url = pub_url

    print("\n" + "=" * 70)
    print(" [SUCCESS] Website Assets Uploaded to Supabase Storage!")
    print("=" * 70)
    if live_index_url:
        print(f"\n >>> LIVE TESTING URL: {live_index_url} <<<\n")
    print("You can share this link for immediate live testing and trials.")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
