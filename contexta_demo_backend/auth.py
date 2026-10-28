"""
Shared-password gate for the whole backend.

POST /api/login trades the demo password for a signed pass ("<expiry>.<hmac>").
Every other route except /health requires it as `Authorization: Bearer <pass>`
(wired up once in main.py as an app-wide dependency).

The password lives only in the DEMO_PASSWORD env var -- never in the repo or
the frontend bundle. It is also the signing key, so changing it in Vercel
logs everyone out. Unset means nobody gets in (fail closed).

Read per request, not at import, so a new password takes effect on the next
request without a restart.
"""
import hashlib
import hmac
import os
import time

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

load_dotenv()

PASS_TTL = 7 * 24 * 3600   # how long one login lasts
MAX_TRIES = 3              # wrong passwords before a lockout
LOCKOUT = 15 * 60          # seconds
OPEN_PATHS = {"/health", "/api/login"}

router = APIRouter()

# ip -> (consecutive failures, locked until)
# ponytail: per-instance memory, so on serverless the count is best-effort and
# resets on cold start. The password is the real protection; move this to
# Upstash/Redis if a strict lockout is ever required.
_fails: dict[str, tuple[int, float]] = {}


def _password() -> str:
    return os.getenv("DEMO_PASSWORD", "")


def _sign(exp: str) -> str:
    return hmac.new(_password().encode(), exp.encode(), hashlib.sha256).hexdigest()


def issue_pass(now: float | None = None) -> str:
    exp = str(int((now or time.time()) + PASS_TTL))
    return f"{exp}.{_sign(exp)}"


def pass_is_valid(token: str) -> bool:
    if not _password():
        return False
    exp, _, sig = token.partition(".")
    if not exp.isdigit() or not hmac.compare_digest(sig, _sign(exp)):
        return False
    return int(exp) > time.time()


async def require_pass(request: Request):
    if request.url.path in OPEN_PATHS:
        return
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not pass_is_valid(token):
        raise HTTPException(status_code=401, detail="Password required")


def _client_ip(request: Request) -> str:
    # Vercel's proxy sets these; request.client is the proxy itself there.
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return request.headers.get("x-real-ip") or forwarded or request.client.host


class LoginRequest(BaseModel):
    password: str


@router.post("/api/login")
async def login(body: LoginRequest, request: Request):
    ip = _client_ip(request)
    now = time.time()
    fails, locked_until = _fails.get(ip, (0, 0.0))
    if locked_until > now:
        # retry_after in the body, not a header: a cross-origin fetch can't read
        # Retry-After without an Expose-Headers rule.
        raise HTTPException(status_code=429, detail={"retry_after": int(locked_until - now) + 1})

    expected = _password()
    if expected and hmac.compare_digest(body.password.encode(), expected.encode()):
        _fails.pop(ip, None)
        return {"token": issue_pass(), "expires_in": PASS_TTL}

    fails += 1
    _fails[ip] = (0, now + LOCKOUT) if fails >= MAX_TRIES else (fails, 0.0)
    raise HTTPException(status_code=401, detail="Wrong password")
