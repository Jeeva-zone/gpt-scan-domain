# 🟠 Orange Test — gpt-scan-domain

**Find Cloudflare-hosted subdomains with passive Certificate Transparency discovery.**

Orange Test is a privacy-conscious reconnaissance utility for authorized security research. Enter a root domain and it discovers certificate names from **Certificate Transparency (crt.sh)**, resolves A/AAAA records server-side, and keeps only IPs that belong to **Cloudflare's official published ranges**.

> ⚠️ **Authorization required:** Use Orange Test only on domains you own or are explicitly authorized to assess. The project is intentionally passive and does **not** perform port scanning, HTTP probing, vulnerability scanning, login testing, CAPTCHA bypass, exploitation, credential attacks, or stealth activity.

## 🚀 One-click deployment

### ▲ Deploy with Vercel — recommended

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Jeeva-zone/gpt-scan-domain)

Vercel is the recommended deployment target because the repository already includes the FastAPI serverless function configuration in `vercel.json`. The frontend is built into `dist/`, while `api/index.py` serves `/api/scan` and `/api/health`.

### 🟢 Deploy with Netlify

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Jeeva-zone/gpt-scan-domain)

> **Netlify note:** Netlify's one-click button can import and deploy this public repository, but the current project is configured primarily for **Vercel's FastAPI runtime**. The static frontend can be deployed to Netlify, while the `/api/*` FastAPI backend requires a compatible Netlify Functions/hosting adapter or a separately hosted API. For a complete zero-configuration deployment of the current codebase, use Vercel.

## ✨ Features

- 🟠 Modern responsive dark security-research interface.
- 🔎 Passive Certificate Transparency discovery through `crt.sh`.
- 🌐 Server-side A and AAAA DNS resolution.
- ☁️ Official Cloudflare IPv4/IPv6 CIDR verification.
- ✅ Cloudflare-only results — unresolved and non-Cloudflare entries are hidden.
- 📋 One-click copy of all results and per-result copy actions.
- 📥 CSV export with `hostname,ip,cloudflare` columns.
- ❌ Cancel an in-progress scan from the interface.
- 🧹 Clear the current results and start again.
- ⏱️ Configurable resource limits, per-IP rate limiting, and a 90-second scan ceiling.
- 🛡️ Same-origin API by default, with optional explicit CORS allow-list.
- ♿ Keyboard-friendly labels, focus states, and live status updates.
- 🧪 Automated Python tests plus frontend build/syntax checks.
- 🚀 Vercel-ready FastAPI + static frontend architecture.

## 🧭 How it works

```text
┌──────────────────────┐
│      Web browser     │
│  Enter root domain   │
└──────────┬───────────┘
           │ POST /api/scan
           ▼
┌──────────────────────┐
│       FastAPI        │
│ validate + rate limit│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       crt.sh         │
│ Passive CT discovery │
└──────────┬───────────┘
           │ hostnames
           ▼
┌──────────────────────┐
│      DNS A/AAAA      │
│ Server-side resolve  │
└──────────┬───────────┘
           │ IP addresses
           ▼
┌──────────────────────┐
│ Cloudflare CIDRs     │
│ IPv4 + IPv6 ranges   │
└──────────┬───────────┘
           │ matches only
           ▼
┌──────────────────────┐
│   Orange Test UI     │
│ 🟠 hostname → IP     │
└──────────────────────┘
```

The discovery source is **Certificate Transparency**, not a brute-force wordlist. A real hostname may therefore be absent from the results if it has no relevant certificate history.

## 🧪 Usage manual

### 1. Open Orange Test

After deployment, open your site's URL. The dashboard presents the **Find Cloudflare-hosted subdomains** interface.

### 2. Enter a root domain

Type a domain such as:

```text
speedtest.net
example.com
```

Use the domain name itself rather than a full URL, path, port, or credentials.

### 3. Start the scan

Click **Start Orange Test**.

The interface moves through these stages:

```text
Connecting
   ↓
Discovering subdomains
   ↓
Resolving and checking
   ↓
Preparing results
```

### 4. Review the results

Only Cloudflare-hosted matches are displayed. Each matching row contains the discovered hostname and resolved IP address.

For example:

```text
🟠 api.example.com      104.x.x.x
🟠 assets.example.com   2606:4700::xxxx
```

The tool intentionally does **not** show unresolved hosts or hosts that do not map to Cloudflare ranges.

### 5. Copy results

Use **Copy results** to copy the discovered hostname/IP pairs to your clipboard. Individual result rows also provide a copy action.

### 6. Export CSV

Use **Download CSV** to export:

```csv
hostname,ip,cloudflare
api.example.com,104.x.x.x,true
assets.example.com,2606:4700::xxxx,true
```

### 7. Cancel or clear

- **Cancel scan** stops the current browser request and returns the interface to an idle state.
- **Clear** removes the current result set so another domain can be scanned.

### 8. Empty results

When nothing qualifies, Orange Test reports:

```text
No 🟠 Cloudflare subdomains were found for <domain>.
```

An empty result does not prove that a domain has no subdomains. It only means no qualifying Cloudflare match was found through the passive workflow used by this version.

## 🔍 Discovery details

The backend requests Certificate Transparency data from:

```text
https://crt.sh/?q=%25.{domain}&output=json
```

Certificate names are normalized, wildcard prefixes are removed, lowercased, deduplicated, and restricted to the requested domain and its subdomains. The root domain is always included as a candidate.

### Important limitation

**Certificate Transparency is not a complete DNS inventory.** Hosts can be missing from CT data, and CT records can outlive or differ from current DNS configuration.

## ☁️ Cloudflare classification

Orange Test obtains Cloudflare's official published ranges from:

```text
https://www.cloudflare.com/ips-v4
https://www.cloudflare.com/ips-v6
```

The ranges are parsed with Python's `ipaddress` module and cached in memory for one hour. Classification is fail-closed: if the authoritative range data cannot be verified, the scanner does not guess that an address belongs to Cloudflare.

## 🧠 Scan limits and safety controls

The backend is deliberately bounded for responsible passive use:

| Control | Default behavior |
|---|---|
| DNS workers | Up to 25 concurrent workers |
| Candidate hosts | Maximum 1,000 |
| Returned results | Maximum 500 |
| Scan duration | Maximum 90 seconds |
| Rate limiting | 1 scan per IP per 60 seconds |
| Cloudflare range cache | 1 hour |
| DNS timeout | 1.5 seconds per host |
| `crt.sh` request timeout | 12 seconds |

These controls help prevent runaway resource usage and are not intended to support aggressive scanning.

## 🔌 API manual

### Health check

```http
GET /api/health
```

Example response:

```json
{
  "status": "ok"
}
```

### Scan a domain

```http
POST /api/scan
Content-Type: application/json
```

Request:

```json
{
  "domain": "speedtest.net"
}
```

Successful responses contain fields including:

```json
{
  "success": true,
  "domain": "speedtest.net",
  "results": [
    {
      "hostname": "example.speedtest.net",
      "ip": "104.x.x.x",
      "cloudflare": true
    }
  ],
  "count": 1,
  "duration_ms": 1234,
  "discovery_source": "crt.sh",
  "note": "..."
}
```

Controlled error codes include:

```text
INVALID_DOMAIN
RATE_LIMITED
DISCOVERY_UNAVAILABLE
CLOUDFLARE_UNAVAILABLE
SCAN_TIMEOUT
INTERNAL_ERROR
```

### Example with cURL

```bash
curl -X POST https://YOUR-DOMAIN.example/api/scan \
  -H "Content-Type: application/json" \
  -d '{"domain":"speedtest.net"}'
```

Replace `https://YOUR-DOMAIN.example` with your deployed site URL.

## 🛠️ Local development

### Prerequisites

- Node.js 20+
- Python 3.12+

### Install

```bash
npm install
python -m venv .venv
```

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

Then install Python dependencies:

```bash
pip install -r requirements.txt
```

### Run locally

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

The development helper serves the frontend on port `3000`, runs FastAPI on port `8000`, and proxies `/api/*` to the backend.

## 🧪 Testing and verification

Run the same checks used by CI:

```bash
npm ci
npm run check
npm run build
python -m pytest -q
```

The CI workflow installs Python 3.12 and Node.js 22, builds the frontend, and runs the Python test suite on every push.

## 📦 Project structure

```text
gpt-scan-domain/
├── api/
│   └── index.py                 # FastAPI serverless entry point
├── backend/
│   ├── cloudflare_ranges.py     # Official Cloudflare CIDR loading/cache
│   ├── config.py                # Runtime configuration
│   ├── discovery.py             # crt.sh discovery + normalization
│   ├── dns_resolver.py          # A/AAAA resolution
│   ├── formatting.py            # Response/CSV formatting helpers
│   ├── rate_limit.py            # In-memory rate limiter
│   ├── scanner.py               # Scan orchestration
│   └── validation.py             # Domain validation
├── src/
│   ├── app.js                   # Browser application logic
│   └── styles.css               # UI styling
├── scripts/
│   ├── build.mjs                # Static production build
│   └── dev_server.py             # Local frontend/backend helper
├── tests/                        # Automated tests
├── .github/workflows/ci.yml      # Continuous integration
├── .env.example                  # Optional runtime settings
├── index.html                    # Frontend entry point
├── package.json                  # Node scripts
├── requirements.txt              # Python dependencies
├── vercel.json                   # Vercel deployment configuration
└── LICENSE                       # MIT license
```

## 🚀 Vercel deployment manual

The current project is configured for Vercel's static output plus Python function architecture.

### One click

Use the button at the top of this README, sign in to Vercel, choose the destination account/team, and deploy.

### Manual import

1. Open Vercel.
2. Choose **Add New Project**.
3. Import `Jeeva-zone/gpt-scan-domain` from GitHub.
4. Keep the repository's `vercel.json` configuration.
5. Deploy.
6. Open the generated production URL and run a test scan.

No API token or frontend secret is required for the core scanner.

### Local Vercel testing

For Vercel-specific local behavior, install the Vercel CLI and run the project through Vercel's development environment when needed. The repository's own `npm run dev` command remains the simplest local development path.

## 🟢 Netlify deployment manual

Netlify can import the public repository through the Deploy to Netlify button or through **Add new project → Import an existing project**. Netlify supports Git-based continuous deployment, so pushes to the connected repository can trigger new deploys. citeturn753710search0turn753710search1

For this repository, however, the current backend is implemented as a Vercel-oriented FastAPI function. Therefore:

- ✅ The static frontend can be published by Netlify.
- ⚠️ The `/api/*` FastAPI endpoints need a Netlify-compatible backend adapter/function setup before Netlify can provide the complete end-to-end scanner.
- ✅ Vercel remains the recommended one-click target for the current source tree.

The Netlify Deploy Button format used above is the official repository-template pattern documented by Netlify. citeturn753710search0

## 🔐 Security model

Orange Test deliberately avoids active network interaction beyond what is necessary for its passive workflow:

- No port scanning.
- No HTTP service probing.
- No vulnerability exploitation.
- No login or authentication testing.
- No CAPTCHA bypass.
- No credential collection.
- No brute-force subdomain wordlists.
- No stealth/evasion features.
- No secrets or API tokens required in the browser.

Only scan systems you are authorized to assess.

## 🗺️ Future ideas

The repository can be extended later with features such as additional passive discovery sources, richer result filtering, persistent scan history, or alternative deployment adapters. These are intentionally **not** part of the current implementation.

## 📜 License

MIT — see [`LICENSE`](LICENSE).

## ⭐ Project

Repository: **https://github.com/Jeeva-zone/gpt-scan-domain**

Built for focused, passive Cloudflare subdomain research. 🟠