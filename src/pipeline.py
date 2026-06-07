"""
LinkedIn Dev Content Pipeline
Generates and posts system design + webdev + career posts to LinkedIn.
"""

import asyncio
import logging
import sys
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from src.generators.post_generator import PostGenerator
from src.publishers.linkedin_publisher import LinkedInPublisher
from config.settings import Settings
from config.topics import TopicBank

logger = logging.getLogger(__name__)
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist():
    return datetime.now(IST)


def send_telegram(token: str, chat_id: str, msg: str):
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({"chat_id": chat_id, "text": msg}).encode()
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        logger.warning("Telegram notification failed: %s", e)


async def run_pipeline(
    niche: str = "system_design",
    topic: Optional[str] = None,
    dry_run: bool = False,
) -> dict:
    settings = Settings()

    logger.info("=" * 60)
    logger.info(
        "LINKEDIN PIPELINE STARTED | niche=%s dry_run=%s", niche, dry_run
    )
    logger.info("=" * 60)

    try:
        # ── 1. Pick topic ──────────────────────────────────────────────
        topic_bank = TopicBank()
        selected_topic = topic or topic_bank.pick_unused(niche)
        logger.info("[1/3] ✅ Topic: %s", selected_topic)

        # ── 2. Generate post ───────────────────────────────────────────
        gen = PostGenerator(settings)
        post = await gen.generate(selected_topic, niche)
        logger.info("[2/3] ✅ Post generated | hook: %s", post.hook[:80])
        logger.info("Post preview:\n%s", post.full_text[:300])

        # ── 3. Post to LinkedIn ────────────────────────────────────────
        post_url = ""

        if not dry_run:
            publisher = LinkedInPublisher(settings)
            result = await publisher.post(post.full_text)
            post_url = result["url"]
            logger.info("[3/3] ✅ Posted: %s", post_url)
        else:
            logger.info("[3/3] ⏭️  Dry run — skipping post")
            logger.info("Full post:\n%s", post.full_text)

        # ── Notify Telegram ────────────────────────────────────────────
        topic_bank.mark_used(niche, selected_topic)

        msg = (
            f"💼 LinkedIn post published!\n"
            f"Topic: {selected_topic}\n"
            f"Niche: {niche}\n"
            f"Hook: {post.hook[:80]}\n"
            f"URL: {post_url or 'dry-run'}"
        )
        send_telegram(
            settings.telegram_bot_token,
            settings.telegram_allowed_user_id,
            msg,
        )

        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE ✅")
        logger.info("=" * 60)

        return {
            "status": "success",
            "topic": selected_topic,
            "niche": niche,
            "post_url": post_url,
            "dry_run": dry_run,
        }

    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        logger.error("PIPELINE FAILED ❌: %s\n%s", exc, tb)
        send_telegram(
            settings.telegram_bot_token,
            settings.telegram_allowed_user_id,
            f"❌ LinkedIn pipeline failed!\nTopic: {topic}\nError: {str(exc)[:200]}",
        )
        raise


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--niche",
        default="system_design",
        choices=["system_design", "webdev", "career"],
    )
    parser.add_argument("--topic", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                log_dir / f"linkedin_{now_ist().strftime('%Y%m%d')}.log",
                encoding="utf-8",
            ),
        ],
    )

    result = asyncio.run(
        run_pipeline(
            niche=args.niche,
            topic=args.topic or None,
            dry_run=args.dry_run,
        )
    )
    print(f"\n✅ Done | topic={result['topic']} | url={result['post_url']}")


if __name__ == "__main__":
    main()
