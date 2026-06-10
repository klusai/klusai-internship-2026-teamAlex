# Secret detection patterns

Regex catalogue for the secret-scanner skill. Each entry: what it catches, a regex usable with `rg`/`grep -E`, and notes. Patterns are intentionally broad — the skill applies triage (see SKILL.md "Reducing false positives") to decide the final verdict.

Run with `rg -nE '<pattern>'` (or `grep -nE`) so hits come back as `file:line`. Use `-i` only where noted; vendor prefixes are case-sensitive.

## Vendor-specific keys (high confidence — these prefixes are rarely false positives)

| Secret | Pattern |
|--------|---------|
| AWS Access Key ID | `\b(AKIA\|ASIA\|AGPA\|AIDA\|AROA\|AIPA\|ANPA\|ANVA)[0-9A-Z]{16}\b` |
| AWS Secret Access Key | `(?i)aws.{0,20}(secret\|sk).{0,20}['"][0-9a-zA-Z/+]{40}['"]` |
| GitHub token | `\b(ghp\|gho\|ghu\|ghs\|ghr)_[0-9A-Za-z]{36}\b` |
| GitHub fine-grained PAT | `\bgithub_pat_[0-9A-Za-z_]{82}\b` |
| GitLab PAT | `\bglpat-[0-9A-Za-z\-_]{20}\b` |
| Slack token | `\bxox[baprs]-[0-9A-Za-z-]{10,72}\b` |
| Slack webhook | `https://hooks\.slack\.com/services/T[0-9A-Z]+/B[0-9A-Z]+/[0-9A-Za-z]+` |
| Google API key | `\bAIza[0-9A-Za-z\-_]{35}\b` |
| Google OAuth client | `\b[0-9]+-[0-9a-z]{32}\.apps\.googleusercontent\.com\b` |
| Stripe secret key | `\bsk_live_[0-9a-zA-Z]{24,}\b` (also `rk_live_`; `sk_test_` is usually a doc/sandbox key) |
| Stripe restricted key | `\brk_live_[0-9a-zA-Z]{24,}\b` |
| Twilio | `\bSK[0-9a-fA-F]{32}\b` / Account SID `\bAC[0-9a-fA-F]{32}\b` |
| SendGrid | `\bSG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}\b` |
| Mailgun | `\bkey-[0-9a-f]{32}\b` |
| OpenAI / Anthropic style | `\b(sk-\|sk-ant-)[0-9A-Za-z\-_]{20,}\b` |
| npm token | `\bnpm_[0-9A-Za-z]{36}\b` |
| Heroku API key (UUID) | `(?i)heroku.{0,15}[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` |
| Square | `\bsq0(atp\|csp\|idp)-[0-9A-Za-z\-_]{22,43}\b` |
| Shopify | `\bshp(at\|ca\|pa\|ss)_[0-9a-fA-F]{32}\b` |
| Datadog | `(?i)datadog.{0,15}\b[0-9a-f]{32}\b` |
| Cloudflare API token | `(?i)cloudflare.{0,20}\b[0-9A-Za-z_-]{40}\b` |

## Cryptographic material (critical)

| Secret | Pattern |
|--------|---------|
| PEM private key | `-----BEGIN (RSA \|EC \|DSA \|OPENSSH \|PGP \|ENCRYPTED )?PRIVATE KEY-----` |
| SSH private key body | `-----BEGIN OPENSSH PRIVATE KEY-----` |
| PuTTY private key | `PuTTY-User-Key-File-` |
| PKCS#12 / cert files | filename ends in `.pem`, `.key`, `.pfx`, `.p12`, `.keystore`, `.jks` |

## Tokens & structured credentials

| Secret | Pattern |
|--------|---------|
| JWT | `\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b` |
| Basic-auth in URL | `(?i)\b(https?\|ftp)://[^/\s:@]+:[^/\s:@]+@` |
| DB connection string w/ password | `(?i)(postgres\|postgresql\|mysql\|mongodb(\+srv)?\|redis\|amqp)://[^:\s]+:[^@\s]+@` |
| Bearer token literal | `(?i)authorization['"]?\s*[:=]\s*['"]bearer\s+[0-9A-Za-z._-]{20,}` |

## Generic / heuristic (lower confidence — lean on entropy + name + triage)

These catch the "assigned a literal to a secret-named variable" case across languages:

| Catches | Pattern |
|---------|---------|
| Secret-named assignment | `(?i)(api[_-]?key\|apikey\|secret\|passwd\|password\|pwd\|token\|access[_-]?key\|client[_-]?secret\|auth[_-]?token\|private[_-]?key)['"]?\s*[:=]\s*['"][^'"]{8,}['"]` |
| High-entropy hex blob | `['"][0-9a-fA-F]{32,}['"]` |
| High-entropy base64 blob | `['"][A-Za-z0-9+/]{40,}={0,2}['"]` |

For the generic hits, judge by:
- **Entropy** — a real key looks random; `password = "password"` or `token = "todo"` does not.
- **Proximity** — value sits right next to a secret-y name.
- **Source** — a literal string, *not* `os.environ[...]`, `process.env.X`, `config.get(...)`, or `${VAR}` interpolation.

## Placeholder / allowlist signals (down-rank or drop)

Treat as benign unless other signals override:

- Values: `your_*`, `*_here`, `xxx...`, `changeme`, `example`, `dummy`, `placeholder`, `<...>`, `REPLACE_ME`, `foo`/`bar`/`baz`, all-zeros, repeated single char.
- Files: `*.example`, `*.sample`, `*.template`, `*.dist`, `*.md` (docs), test fixtures, and this repo's ignored `private/`, `local/`, `scratch/`, `*.local`, `.env.example`.
- Env-var references: `os.environ`, `os.getenv`, `process.env`, `System.getenv`, `ENV[...]`, `${...}`, `%VAR%`.
