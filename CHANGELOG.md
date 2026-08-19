# Changelog

## 0.3.0

- Added the `antipodal/webapp/` Flask API: accounts, roles, saved locations,
  sessions, MFA, password recovery, coupons, plan upgrades, and a three-step
  export workflow, plus the `wsgi.py` entry point.
- Seeded 31 logic-level security flaws across broken access control, business
  logic, and authentication and session management for the SonarQube Hunter
  Agent to find. These are not labelled inline.
- Documented the intended authorization matrix in `README.md`.

## 0.2.0

- Added `antipodal/auth.py`, `antipodal/cache.py`, and `antipodal/report.py`
  with new security, reliability, and maintainability issues.
- Added `Dockerfile`, `infra/main.tf`, and `k8s/deployment.yaml` so the Docker,
  Terraform, and Kubernetes analyzers have something to report.
- Added a `web/` front end with DOM-based XSS and HTML rule violations.
- Expanded `requirements.txt` with more outdated pins for dependency risk
  reporting.

## 0.1.0

- Initial antipodal calculator demo fixture.
- Core antipode, great-circle distance, and hemisphere helpers.
- Seeded with intentional security, reliability, and maintainability issues
  for SonarQube analysis.
