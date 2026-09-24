class AppError(Exception):
    status_code = 500
    code = "internal_error"
    message = "An unexpected error occurred."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)
        self.message = message or self.message

class ProviderError(AppError):
    code = "provider_error"
    status_code = 502
    message = "The AI provider could not complete the request."

class DatabaseError(AppError):
    code = "database_error"
    status_code = 500
    message = "A database error occurred."

class DatabaseUnavailableError(DatabaseError):
    code = "database_unavailable"
    status_code = 503
    message = "The database is temporarily unavailable."

class RateLimitError(AppError):
    code = "rate_limited"
    status_code = 429
    message = (
        "Too many requests. "
        "Please try again later."
    )

    def __init__(
        self,
        *,
        retry_after: int,
    ):
        super().__init__(self.message)
        self.retry_after = retry_after

