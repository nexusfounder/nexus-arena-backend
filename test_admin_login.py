import urllib.request
import json

def test(user, pw):
    url = "http://127.0.0.1:8088/api/auth/login"
    payload = json.dumps({"username_or_email": user, "password": pw}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"[OK] {user}:{pw} -> {data}")
    except Exception as e:
        print(f"[ERR] {user}:{pw} -> {e}")

if __name__ == "__main__":
    test("admin", "admin")
    test("Admin", "admin")
    test("Admin", "password123")
    test("admin", "password123")
    test("ADMIN", "admin")
