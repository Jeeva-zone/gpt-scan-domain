from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.config import ALLOWED_ORIGINS, RATE_LIMIT_SECONDS
from backend.rate_limit import check_rate_limit
from backend.scanner import ScanError, scan_domain
from backend.validation import is_valid_domain, normalize_domain

app = FastAPI(title='Orange Test API', docs_url=None, redoc_url=None)

if ALLOWED_ORIGINS:
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(CORSMiddleware, allow_origins=list(ALLOWED_ORIGINS), allow_methods=['POST', 'GET'], allow_headers=['Content-Type'])

class ScanRequest(BaseModel):
    domain: str


def error_response(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content={'success': False, 'error': {'code': code, 'message': message}})


@app.get('/api/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/api/scan')
def scan(request: Request, payload: ScanRequest) -> Any:
    domain = normalize_domain(payload.domain)
    if not is_valid_domain(domain):
        return error_response('INVALID_DOMAIN', 'Please enter a valid domain.', 400)

    client_ip = request.client.host if request.client else 'unknown'
    allowed, retry_after = check_rate_limit(client_ip, RATE_LIMIT_SECONDS)
    if not allowed:
        response = error_response('RATE_LIMITED', 'Please wait before starting another scan.', 429)
        response.headers['Retry-After'] = str(retry_after)
        return response

    try:
        return scan_domain(domain)
    except ScanError as exc:
        return error_response(exc.code, exc.message, exc.status)
    except Exception:
        return error_response('INTERNAL_ERROR', 'The scan could not be completed.', 500)
