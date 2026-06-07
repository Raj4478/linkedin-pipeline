"""
LinkedIn OAuth2 Token Generator — run this ONCE locally to get your access token.
The token is valid for ~60 days. Store it in GitHub Secrets as LINKEDIN_ACCESS_TOKEN.

Usage:
    python get_linkedin_token.py

You need:
    LINKEDIN_CLIENT_ID     — from LinkedIn Developer App
    LINKEDIN_CLIENT_SECRET — from LinkedIn Developer App
"""

import os
import httpx
import urllib.parse
import http.server
import threading
import webbrowser

CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", input("Enter LinkedIn Client ID: ").strip())
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", input("Enter LinkedIn Client Secret: ").strip())
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "openid profile email w_member_social"

auth_code = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        if "/callback" in self.path:
            params = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            auth_code = params.get("code")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Auth successful! You can close this tab.</h2>")

    def log_message(self, *args):
        pass  # Suppress server logs


def get_token():
    global auth_code

    # Step 1: Build auth URL
    auth_url = (
        "https://www.linkedin.com/oauth/v2/authorization?"
        + urllib.parse.urlencode({
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": "linkedin_pipeline_auth",
        })
    )

    # Step 2: Start local callback server
    server = http.server.HTTPServer(("localhost", 8888), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    # Step 3: Open browser
    print(f"\nOpening LinkedIn auth in browser...")
    print(f"If it doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)
    thread.join(timeout=120)

    if not auth_code:
        print("❌ No auth code received. Try again.")
        return

    # Step 4: Exchange code for token
    resp = httpx.post(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if resp.status_code != 200:
        print(f"❌ Token exchange failed: {resp.text}")
        return

    data = resp.json()
    access_token = data["access_token"]
    expires_in = data.get("expires_in", 0)
    days = expires_in // 86400

    # Step 5: Get person URN
    profile = httpx.get(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    ).json()
    person_id = profile.get("sub", "")
    person_urn = f"urn:li:person:{person_id}"
    name = profile.get("name", "Unknown")

    print(f"\n✅ Authenticated as: {name}")
    print(f"✅ Token valid for: ~{days} days")
    print(f"\n{'='*60}")
    print("Add these to GitHub Secrets:")
    print(f"{'='*60}")
    print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
    print(f"LINKEDIN_PERSON_URN={person_urn}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    get_token()
