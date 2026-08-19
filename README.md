# Antipodal Calculator

A small Python utility that computes the **antipode** (the point on Earth's
surface diametrically opposite a given coordinate), the great-circle distance
to it, and some related helpers.

> ⚠️ **This project is a SonarQube demo fixture.** It intentionally contains
> security vulnerabilities, reliability bugs, and maintainability smells so they
> can be surfaced by a SonarQube Server / SonarQube Cloud scan. **Do not use any
> of this code in production.**

## Layout

```
antipodal-calculator/
  main.py                 CLI entry point
  requirements.txt        pinned (deliberately outdated) dependencies
  Dockerfile              root user, latest tag, secrets in ENV
  antipodal/
    __init__.py
    config.py             hardcoded secrets, insecure defaults
    calculator.py         core antipodal math
    database.py           SQL injection, weak hashing, resource leaks
    api.py                insecure HTTP, eval, pickle, command injection
    utils.py              duplication, dead code, complexity
    auth.py               unverified JWT, weak cipher, ReDoS, insecure cookies
    cache.py              path traversal, temp file races, unsafe extraction
    report.py             copy/paste duplication, cognitive complexity
    webapp/
      __init__.py         app factory, access-control decorators
      store.py            accounts, locations, sessions, coupons, export jobs
      auth_routes.py      login, MFA, logout, password reset
      location_routes.py  saved location CRUD
      account_routes.py   profile and account management
      admin_routes.py     operator-only account administration
      billing_routes.py   coupons, plan upgrade, export workflow
  wsgi.py                 API entry point
  infra/
    main.tf               public bucket, open security group, wildcard IAM
  k8s/
    deployment.yaml       privileged container, hostPath, no resource limits
  web/
    index.html            missing lang/alt, cleartext form action, duplicate ids
    app.js                DOM XSS, eval, insecure randomness
```

## Run

```bash
python main.py 40.7128 -74.0060 "New York"
```

## API

```bash
python wsgi.py            # http://localhost:8080
```

Accounts are seeded in `antipodal/webapp/store.py`: `ada` and `grace` hold the
`user` role, `root` holds `admin`. All three use the password `password`.

Sign-in is two steps for accounts with MFA enabled. `POST /api/login` validates
the password, then `POST /api/mfa/verify` validates the second factor before the
session counts as fully authenticated.

An export is three steps: `POST /api/export/request` opens a job,
`POST /api/export/<job_id>/confirm` charges one credit and marks it paid, and
`GET /api/export/<job_id>/download` returns the rows for a paid job.

### Intended authorization rules

| Endpoint | Who may call it |
|---|---|
| `GET /api/locations` | Any authenticated account, own locations only |
| `GET|PUT|DELETE /api/locations/<id>` | The account that owns the location |
| `GET /api/locations/shared/<owner_id>` | Accounts the owner has shared with |
| `GET|PATCH /api/profile` | The account itself; `role`, `plan`, and `credits` are not self-editable |
| `GET /api/users/<id>` | Any authenticated account; public fields only |
| `POST /account/{password,email,delete}` | The account itself, with a valid CSRF token |
| `GET /api/admin/users` | Admin role only |
| `POST /api/admin/users/<id>/promote` | Admin role only |
| `POST /api/admin/users/<id>/credits` | Admin role only |
| `DELETE /api/admin/users/<id>` | Admin role only |
| `GET /api/admin/metrics` | Admin role only |
| `POST /api/credits/redeem` | Any authenticated account, once per coupon per account |
| `POST /api/billing/upgrade` | Any authenticated account, after payment settles |
| `GET /api/export/<job_id>/download` | The account that owns a paid job |
| `POST /api/export/<job_id>/refund` | The owner, once per job, if never downloaded |
| `GET /api/billing/invoices/<id>` | The account the invoice belongs to |

The API deliberately does not always enforce the table above. Reconciling the two
is the exercise.

## Analyze with SonarQube

```bash
sonar-scanner
```

## Two layers of planted issues

The fixture is deliberately split so both halves of the Sonar stack have
something to do.

**Pattern-detectable flaws** — hardcoded secrets, SQL injection, `eval`, weak
crypto, IaC misconfiguration, DOM XSS. These are labelled inline with the
category they belong to, and static analysis finds them.

**Logic flaws** — everything in `antipodal/webapp/`. Broken access control,
business logic abuse, and authentication and session management defects. These
have no pattern signature: finding them means comparing what a route says it does
against what it actually enforces. They are **not** labelled inline, so an agent
has to reason rather than read a comment.

## Categories of planted issues

- **Security (Blocker/Critical):** hardcoded DB password & API keys that must be
  rotated, SQL injection, `eval()`, insecure deserialization (`pickle`,
  `yaml.load`), command injection (`shell=True`, `os.system`), path traversal,
  disabled TLS verification (`verify=False`, `_create_unverified_context`),
  unverified JWT signatures, DES/ECB weak cipher, weak hashing (MD5, MD4,
  SHA-1), insecure randomness for tokens, ReDoS, permissive CORS, insecure
  cookies, world-writable file permissions, unsafe archive extraction.
- **Reliability (Bugs):** bare `except`, mutable default argument, division by
  zero, unclosed resources, unreachable code, unchecked `argv`, identical
  operands, mutation during iteration, wrong argument counts, mismatched format
  strings, exact float comparison.
- **Maintainability (Code Smells):** duplicated functions and copy/pasted
  blocks, high cognitive complexity, too many parameters, nested ternaries,
  shadowed builtins, self-assignment, magic numbers, commented-out code, unused
  imports and locals, TODO/FIXME tags.
- **Infrastructure as Code:** Docker (root user, `latest` tag, secrets in
  `ENV`, `chmod 777`), Terraform (public S3 bucket, `0.0.0.0/0` ingress,
  wildcard IAM policy, unencrypted storage), Kubernetes (privileged container,
  `hostPath` volume, no resource limits, plaintext secret env vars).
- **Web front end:** DOM-based XSS, `eval()`, `document.write`,
  `Math.random()` for tokens, cleartext form action, duplicate element ids,
  missing `lang` and `alt` attributes.
- **Dependency risk (SCA):** outdated pins in `requirements.txt` (`requests`,
  `flask`, `jinja2`, `werkzeug`, `pyyaml`, `urllib3`, `cryptography`, `pyjwt`,
  `pycryptodome`, `lxml`, `pillow`).
