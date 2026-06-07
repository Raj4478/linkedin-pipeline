"""
LinkedIn Post Generator — uses Gemini to generate long-form LinkedIn posts.
LinkedIn format is different from Twitter: longer, more narrative, no hashtag spam.
"""

import logging
import httpx
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LinkedInPost:
    topic: str
    niche: str
    hook: str          # First line — must stop the scroll
    body: str          # Full post body
    full_text: str     # hook + body combined, ready to post


SYSTEM_PROMPTS = {
    "system_design": """You are a senior backend engineer writing LinkedIn posts for Indian software engineers.
Write engaging, educational LinkedIn posts about system design concepts.
Style: conversational, uses Indian tech examples (Zomato, Swiggy, Razorpay, PhonePe, CRED, Zepto),
includes emojis sparingly, ends with a question to drive comments.
NOT a tweet thread — this is one cohesive LinkedIn post.""",

    "webdev": """You are a senior backend engineer writing LinkedIn posts for Indian software engineers.
Write practical, code-adjacent LinkedIn posts about backend development.
Style: direct, uses real code snippets or pseudocode, relatable to Indian SDE-I/II audience,
references tools they actually use at Indian startups.""",

    "career": """You are a senior engineer and mentor writing LinkedIn posts for Indian software engineers.
Write honest, experience-backed career advice for Indian developers (SDE-I to SDE-III level).
Style: personal, vulnerable, avoids generic gyaan, specific to Indian tech ecosystem
(service companies, product startups, FAANG India, YC-backed startups).""",
}

POST_PROMPT = """Write a LinkedIn post about: "{topic}"

Requirements:
- Start with a HOOK line that stops scrolling (surprising stat, bold claim, or relatable frustration)
- 150-250 words total
- Use line breaks between paragraphs for readability
- 3-5 relevant emojis (not excessive)
- End with ONE engaging question to drive comments
- 3-5 hashtags at the very end
- Use Indian tech context where relevant

Return ONLY the post text. No preamble, no "Here's a post:", just the post itself."""


class PostGenerator:
    def __init__(self, settings):
        self.settings = settings

    async def generate(self, topic: str, niche: str) -> LinkedInPost:
        logger.info("Generating LinkedIn post: %s", topic)
        system = SYSTEM_PROMPTS.get(niche, SYSTEM_PROMPTS["system_design"])
        text = await self._call_gemini(system, POST_PROMPT.format(topic=topic))

        lines = text.strip().split("\n")
        hook = lines[0] if lines else topic
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else text

        return LinkedInPost(
            topic=topic,
            niche=niche,
            hook=hook,
            body=body,
            full_text=text.strip(),
        )

    async def _call_gemini(self, system: str, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent"
            f"?key={self.settings.gemini_api_key}"
        )
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.85,
                "maxOutputTokens": 600,
            },
        }
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
