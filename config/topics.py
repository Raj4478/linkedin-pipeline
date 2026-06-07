"""Topic Bank — rotates topics to avoid repetition."""

import json
from pathlib import Path

TOPICS = {
    "system_design": [
        "how URL shortener works",
        "designing a notification system",
        "how CDN works",
        "load balancer types explained",
        "designing a chat system like WhatsApp",
        "how Netflix recommendation works",
        "rate limiting algorithms",
        "database sharding explained",
        "CAP theorem simplified",
        "how search autocomplete works",
        "designing a ride-sharing app like Uber",
        "consistent hashing explained",
        "how DNS works",
        "designing a payment system",
        "event-driven architecture explained",
        "microservices vs monolith",
        "how Redis works under the hood",
        "designing a file storage system like S3",
        "WebSocket vs HTTP polling",
        "how Kafka works",
    ],
    "webdev": [
        "NestJS dependency injection explained",
        "TypeScript generics in practice",
        "PostgreSQL indexing strategies",
        "Docker best practices for Node.js",
        "JWT vs session authentication",
        "TypeORM query optimization",
        "REST vs GraphQL vs gRPC",
        "AWS SQS vs SNS vs EventBridge",
        "Node.js event loop explained",
        "PostgreSQL vs MongoDB — when to use which",
        "Redis caching patterns",
        "API rate limiting in NestJS",
        "database migrations best practices",
        "async/await vs promises",
        "environment variables and secrets management",
    ],
    "career": [
        "how to crack system design interviews",
        "SDE-I to SDE-II transition tips",
        "how to negotiate salary in India",
        "building a personal brand as a developer",
        "how to write a resume that gets shortlisted",
        "contributing to open source as a fresher",
        "how to prepare for DSA interviews",
        "remote work tips for Indian developers",
        "how to get referrals at top tech companies",
        "freelancing vs full-time job for developers",
    ],
}

TRACKER_FILE = Path("data/used_topics.json")


class TopicBank:
    def __init__(self):
        TRACKER_FILE.parent.mkdir(exist_ok=True)
        if TRACKER_FILE.exists():
            self.used = json.loads(TRACKER_FILE.read_text())
        else:
            self.used = {k: [] for k in TOPICS}

    def pick_unused(self, niche: str) -> str:
        all_topics = TOPICS.get(niche, TOPICS["system_design"])
        used = self.used.get(niche, [])
        unused = [t for t in all_topics if t not in used]
        if not unused:
            # Reset cycle
            self.used[niche] = []
            unused = all_topics
        return unused[0]

    def mark_used(self, niche: str, topic: str):
        if niche not in self.used:
            self.used[niche] = []
        if topic not in self.used[niche]:
            self.used[niche].append(topic)
        TRACKER_FILE.write_text(json.dumps(self.used, indent=2))
