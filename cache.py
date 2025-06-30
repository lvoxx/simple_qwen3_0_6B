import redis
from difflib import SequenceMatcher

class PromptCache:
    def __init__(self, host="redis", port=6379, threshold=0.92, prefix="prompt:", decode_responses=True):
        self.redis = redis.Redis(host=host, port=port, decode_responses=decode_responses)
        self.threshold = threshold
        self.prefix = prefix  # Optional prefix to separate keyspace

    def normalize(self, prompt: str) -> str:
        return (
            prompt.strip()
            .lower()
            .replace("\n", " ")
            .replace(".", "")
            .replace(",", "")
        )

    def fuzzy_match(self, a: str, b: str) -> bool:
        return SequenceMatcher(None, a, b).ratio() >= self.threshold

    def get(self, prompt: str) -> str | None:
        norm = self.normalize(prompt)
        pattern = f"{self.prefix}*"

        for key in self.redis.scan_iter(match=pattern):
            key_plain = key.removeprefix(self.prefix)
            if self.fuzzy_match(norm, key_plain):
                print(f"[Cache] Hit: {key}")
                return self.redis.get(key)
        return None

    def set(self, prompt: str, response: str):
        norm = self.normalize(prompt)
        redis_key = self.prefix + norm
        self.redis.set(redis_key, response)
        print(f"[Cache] Stored: {norm[:40]}...")

    def clear(self):
        keys = list(self.redis.scan_iter(match=self.prefix + "*"))
        if keys:
            self.redis.delete(*keys)
            print(f"[Cache] Cleared {len(keys)} items")

    def size(self) -> int:
        return len(list(self.redis.scan_iter(match=self.prefix + "*")))
