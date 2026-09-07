# 🟠 Orange Test — gpt-scan-domain

**Find Cloudflare-hosted subdomains with passive Certificate Transparency discovery.**

Orange Test accepts a root domain, discovers certificate names through **crt.sh**, resolves A/AAAA records server-side, checks those IPs against Cloudflare's current official CIDR ranges, and displays **only Cloudflare matches**.

> ⚠️ Use this tool only on domains you own or are authorized to assess. It is intentionally passive: no port scanning, HTTP probing, vulnerability scanning, login testing, CAPTCHA bypass, exploitation, or stealth activity.

## ✨ Features

- 🟠 Responsive dark security-research dashboard.
- 🔎 Passive Certificate Transparency discovery through crt.sh.
- 🌐 Server-side A and AAAA resolution with configurable concurrency.
- ☁️ Official Cloudflare IPv4/IPv6 CIDR verification with one-hour in-memory caching.
- ✅ Results are Cloudflare-only (`cloudflare: true`).
- 📋 One-click plain-text copy and per-result copy.
- 📥 CSV export: `hostname,ip,cloudflare`.
- ⏱️ Configurable limits, basic IP rate limiting, and a 90-second scan ceiling.
- 🛡️ Same-origin API by default, with optional explicit CORS allow-list.
- ♿ Keyboard-friendly labels, focus states and live status updates.
- 🧪 Python tests and frontend production build checks.
- 🚀 Vercel-ready FastAPI + static frontend architecture.

## 🧭 Architecture

```text
Browser → POST /api/scan → FastAPI
                         ├─ validate + rate limit
                         ├─ passive crt.sh discovery
                         ├─ A / AAAA DNS resolution
                         ├─ official Cloudflare CIDRs
                         └─ Cloudflare-only results
```

## 📁 Project structure

```text
gpt-scan-domain/
├── api/index.py
├── backend/
├── src/
├── scripts/
├── tests/
├── .github/workflows/ci.yml
├── .env.example
├── index.html
├── package.json
├── requirements.txt
├── vercel.json
└── LICENSE
```

## 🔍 Discovery

The backend queries `https://crt.sh/?q=%25.{domain}&output=json`. Certificate names are normalized, wildcard prefixes removed, lowercased, deduplicated, and restricted to the requested domain and its subdomains. The root domain is always a candidate.

**CT is not a DNS inventory.** A legitimate hostname can be absent from Certificate Transparency data. This first version intentionally avoids brute-force wordlists.

## ☁️ Cloudflare classification

Official ranges are retrieved from `https://www.cloudflare.com/ips-v4` and `https://www.cloudflare.com/ips-v6`, parsed with Python's `ipaddress` module, and cached for one hour. If verification fails, the scanner fails closed instead of guessing.

## 🔌 API

`GET /api/health` returns `{"status":"ok"}`.

`POST /api/scan` accepts `{"domain":"speedtest.net"}` and returns a safe schema containing `success`, `domain`, `results`, `count`, `duration_ms`, `discovery_source`, and `note`. Every normal result has `cloudflare: true`.

Controlled errors include `INVALID_DOMAIN`, `RATE_LIMITED`, `DISCOVERY_UNAVAILABLE`, `CLOUDFLARE_UNAVAILABLE`, `SCAN_TIMEOUT`, and `INTERNAL_ERROR`.

## 🛠️ Local development

Prerequisites: Node.js 20+ and Python 3.12+.

```bash
npm install
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
npm run dev
```

Open `http://localhost:3000`.

## 🧪 Verification

```bash
npm run check
npm run build
python -m pytest -q
```

The source was verified locally before synchronization: frontend syntax/build checks passed and the Python test suite passed.

## 🚀 Vercel

`vercel.json` configures the static frontend output and the FastAPI function with a 90-second maximum duration. `.env.example` documents the supported resource and rate-limit settings.

No API token or secret is required for the core scanner.

## 🛡️ Safety

Only scan systems you are authorized to assess. Orange Test is designed for passive research and deliberately excludes active probing and exploitation features.

## 📜 License

MIT — see `LICENSE`.
