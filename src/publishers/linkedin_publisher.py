"""
LinkedIn Publisher — posts text content via LinkedIn API v2.
Uses a long-lived OAuth2 access token (valid ~60 days).
No rate limiting issues, completely free.
"""

import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"


class LinkedInPublisher:
    def __init__(self, settings):
        self.settings = settings
        self.headers = {
            "Authorization": f"Bearer {self.settings.linkedin_access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202504",
        }

    async def get_person_urn(self) -> str:
        """Fetch the authenticated user's person URN."""
        # Use cached URN from settings if available
        if self.settings.linkedin_person_urn:
            return self.settings.linkedin_person_urn

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{LINKEDIN_API_BASE}/userinfo",
                headers=self.headers,
            )
            if resp.status_code != 200:
                logger.error("Failed to get person URN: %s", resp.text)
                resp.raise_for_status()
            data = resp.json()
            sub = data.get("sub")  # sub = person ID
            urn = f"urn:li:person:{sub}"
            logger.info("Person URN: %s", urn)
            return urn

    async def post(self, text: str) -> dict:
        """Post a text post to LinkedIn. Returns post URN."""
        person_urn = await self.get_person_urn()

        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{LINKEDIN_API_BASE}/ugcPosts",
                json=payload,
                headers=self.headers,
            )
            if resp.status_code not in (200, 201):
                logger.error("LinkedIn post failed %d: %s", resp.status_code, resp.text)
                resp.raise_for_status()

            post_id = resp.headers.get("x-restli-id", "unknown")
            post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
            logger.info("LinkedIn post published: %s", post_url)
            return {"id": post_id, "url": post_url}
