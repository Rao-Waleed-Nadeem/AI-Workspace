from collections import defaultdict, deque
from threading import Lock
import time

from fastapi import Depends, Request

from app.core.dependencies import get_current_user
from app.core.config import settings
from app.core.errors import RateLimitError
from app.models import User


class InMemoryRateLimiter:

    def __init__(
        self,
        limit: int,
        window_seconds: int,
    ):
        self.limit = limit
        self.window_seconds = window_seconds

        self._requests = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            timestamps = self._requests[key]

            while (
                timestamps
                and timestamps[0] <= cutoff
            ):
                timestamps.popleft()

            if len(timestamps) >= self.limit:
                retry_after = max(
                    1,
                    int(
                        timestamps[0]
                        + self.window_seconds
                        - now
                    ),
                )

                raise RateLimitError(
                    retry_after=retry_after
                )

            timestamps.append(now)

ai_limiter = InMemoryRateLimiter(
    limit=settings.AI_RATE_LIMIT_REQUESTS,
    window_seconds=(
        settings.AI_RATE_LIMIT_WINDOW_SECONDS
    ),
)

auth_limiter = InMemoryRateLimiter(
    limit=settings.AUTH_RATE_LIMIT_REQUESTS,
    window_seconds=(
        settings.AUTH_RATE_LIMIT_WINDOW_SECONDS
    ),
)

def rate_limit_ai(
    request: Request,
    current_user: User = Depends(
        get_current_user
    ),
) -> None:

    ai_limiter.check(
        f"user:{current_user.id}"
    )

def _client_key(
    request: Request,
) -> str:

    return (
        request.client.host
        if request.client
        else "unknown"
    )

def rate_limit_auth(
    request: Request,
) -> None:

    auth_limiter.check(
        f"ip:{_client_key(request)}"
    )