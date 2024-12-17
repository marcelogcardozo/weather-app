from types import TracebackType

import redis

from config import (
    REDIS_DB,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_USERNAME,
)


class RedisClient:
    """
    A class to initialize and manage a Redis client with environment variables.
    """

    def __init__(self) -> None:
        self.connection = self._connect()

    def _connect(self) -> 'redis.Redis[str]':
        """
        Private method to initialize the Redis client.
        """
        return redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True,
        )

    def __enter__(self) -> 'redis.Redis[str]':
        """
        Enter the runtime context and return the Redis client.
        """
        return self.connection

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exit the runtime context and close the Redis connection.

        Args:
            exc_type: The type of exception that was thrown, if any.
            exc_value: The value of the exception that was thrown, if any.
            traceback: The traceback of the exception that was thrown, if any.
        """
        if self.connection:
            self.connection.close()
