from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def _init_(self, app, daily_limit: int):
        super()._init_(app)
        self.daily_limit = daily_limit
        self.counter = {}  # store per-client usage (by IP)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host  # get user's IP
        if client_ip not in self.counter:
            self.counter[client_ip] = 0

        if request.url.path.startswith("/query"):
            if self.counter[client_ip] >= self.daily_limit:
                raise HTTPException(
                    status_code=429, 
                    detail="Daily request limit reached"
                )
            self.counter[client_ip] += 1

        # get the response from the API
        response = await call_next(request)

        # calculate remaining requests
        remaining = self.daily_limit - self.counter[client_ip]

        # add a custom header
        response.headers["X-Remaining-Requests"] = str(remaining)

        return response