# Restful Booker API Automation Testing (Python + pytest)

[![Python API Tests](https://github.com/halovie123/api-automation-pytest/actions/workflows/pytest-api.yml/badge.svg)](https://github.com/halovie123/api-automation-pytest/actions/workflows/pytest-api.yml)

A portfolio project demonstrating **automated REST API testing** with **Python, pytest, Requests, JSON Schema validation, Allure Report, and GitHub Actions**. The suite automates **16 test cases** against the public [Restful Booker API](https://restful-booker.herokuapp.com/), covering authentication, health checks, booking CRUD, response validation, filtering, and negative scenarios.

## Overview

| Item | Details |
| --- | --- |
| System under test | [Restful Booker](https://restful-booker.herokuapp.com/) |
| Python version in CI | 3.12 |
| Test framework | pytest |
| HTTP client | Requests |
| Schema validation | jsonschema |
| Test reports | JUnit XML and Allure |
| CI/CD | GitHub Actions |
| Verified CI run | **16 passed, 0 failed (2.96 s)** on November 25, 2026 |

**[See the successful GitHub Actions run](https://github.com/halovie123/api-automation-pytest/actions/runs/45590817327)**

> These are the results of a specific CI run, not a guarantee that future runs will always pass. The API is a shared demo service and can reset its data.

## Repository structure

```text
api-automation-pytest/
├── .github/
│   └── workflows/
│       └── pytest-api.yml     # Automated CI pipeline
├── tests/
│   └── test_booking.py        # 16 API test cases
├── conftest.py                # Session, token, and booking fixtures
├── settings.py                # API URL and environment-based credentials
├── pytest.ini                 # pytest configuration and smoke marker
├── requirements.txt           # Python dependencies
├── .gitignore                 # Ignore generated/local files
└── README.md
```

## API endpoints covered

| Method | Endpoint | Coverage |
| --- | --- | --- |
| `GET` | `/ping` | API health check |
| `POST` | `/auth` | Successful and invalid authentication |
| `GET` | `/booking` | List bookings and filter by first/last name |
| `POST` | `/booking` | Create a booking |
| `GET` | `/booking/{id}` | Retrieve booking; verify unknown/deleted IDs |
| `PUT` | `/booking/{id}` | Authenticated update and unauthorized update |
| `PATCH` | `/booking/{id}` | Authenticated partial update |
| `DELETE` | `/booking/{id}` | Delete and verify deletion |

## Test cases

| ID | Test scenario | Category |
| --- | --- | --- |
| TC01 | Health check returns `201 Created` | Smoke |
| TC02 | Successful authentication returns a non-empty token | Smoke |
| TC03 | Incorrect password is rejected | Negative |
| TC04 | Empty username is rejected | Negative |
| TC05 | Empty password is rejected | Negative |
| TC06 | Get booking list | Positive |
| TC07 | Create booking and verify booking ID | Positive |
| TC08 | Get newly created booking and compare its data | Smoke |
| TC09 | Validate booking response against JSON Schema | Contract |
| TC10 | Unknown booking ID returns `404` | Negative |
| TC11 | Filter bookings by first name | Positive |
| TC12 | Filter bookings by last name | Positive |
| TC13 | Authorized PUT updates and persists booking data | Positive |
| TC14 | PUT without authentication is rejected (`401` or `403`) | Negative |
| TC15 | Authorized PATCH updates a field while preserving others | Positive |
| TC16 | Delete booking and confirm subsequent GET returns `404` | Smoke |

TC03–TC05 use `@pytest.mark.parametrize` to create three separate pytest test cases. Four tests have the `smoke` marker.

## Fixtures and test isolation

Fixtures in `conftest.py`:

- **`api`** (`scope="session"`): creates a reusable `requests.Session` with JSON headers, then closes it after the test session.
- **`token`** (`scope="session"`): authenticates with `/auth` and checks that a non-empty token was returned.
- **`booking`** (function scope): creates a new booking and yields `(booking_id, payload)` to an individual test. After the test, it checks whether the booking still exists and attempts to delete it with Basic Auth.

Tests using `booking` do not depend on a hard-coded ID or the execution order of another test. Cleanup is **best effort** because external demo API failures or resets can occur.

## Prerequisites and installation

- Python **3.12** recommended (same version as CI).
- Internet access to `https://restful-booker.herokuapp.com`.
- Optional: Node.js and Allure CLI for HTML reporting.

### Windows / VS Code (CMD)

```bat
git clone https://github.com/halovie123/api-automation-pytest.git
cd api-automation-pytest
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

For PowerShell, use `.\.venv\Scripts\Activate.ps1` instead. For macOS/Linux, activate with `source .venv/bin/activate`.

### Configuration

`settings.py` defines the API URL and reads credentials from the environment:

| Setting | Description |
| --- | --- |
| `BASE_URL` | `https://restful-booker.herokuapp.com` |
| `RB_USERNAME` | Username, defaults to `admin` for the demo |
| `RB_PASSWORD` | Password, defaults to public demo password locally |

To set demo credentials explicitly in Windows CMD:

```bat
set RB_USERNAME=admin
set RB_PASSWORD=password123
```

**Security:** The values shown are public demo credentials only. Never commit real secrets. GitHub Actions reads `RB_PASSWORD` from a repository secret. For a production project, remove credential fallbacks and require environment variables.

## Running tests locally

All 16 tests:

```bat
python -m pytest -v
```

Smoke tests only:

```bat
python -m pytest -m smoke -v
```

Filter by test name:

```bat
python -m pytest -k "booking_schema" -v
```

### JUnit XML report

```bat
python -m pytest -v --junitxml=report.xml
```

### Allure report

The `allure-pytest` plugin is included in `requirements.txt`:

```bat
python -m pytest -v --alluredir=allure-results --clean-alluredir
```

Install the appropriate Allure CLI (CI uses `npm install -g allure`) and create/open the HTML report:

```bat
allure generate allure-results -o allure-report
allure open allure-report
```

Generated reports and raw results are ignored by Git to avoid committing bulky or sensitive run data.

## GitHub Actions CI/CD

Workflow: [`.github/workflows/pytest-api.yml`](.github/workflows/pytest.yml)

**Triggers:** each push to `main` and manual `workflow_dispatch`.

The workflow:

1. Checks out source code and installs Python 3.12.
2. Installs dependencies and Allure CLI.
3. Runs pytest using the GitHub secret `RB_PASSWORD`.
4. Generates `reports/report.xml` and Allure results/HTML.
5. Uploads the **`pytest-api-reports`** artifact for review.

**[View workflow runs](https://github.com/halovie123/api-automation-pytest/actions/workflows/pytest-api.yml)**

To download reports: open a workflow run → **Summary** → **Artifacts** → `pytest-api-reports`. The artifact includes `reports/report.xml`, `allure-results/`, and `allure-report/` when generated successfully.

The upload step uses `if: always()` to retain any available evidence even if tests fail.

## Verified test execution

**GitHub Actions run:** [45590817327](https://github.com/halovie123/api-automation-pytest/actions/runs/45590817327), **November 25, 2026**.

| Metric | Verified result |
| --- | ---: |
| Test cases executed | **16** |
| Passed | **16** |
| Failed | **0** |
| Test execution time | **2.96 s** |
| Workflow conclusion | **Success** |
| CI report artifact | **`pytest-api-reports`** — uploaded |

This successful run is documented evidence, not an assertion that the shared API will always behave the same way.

## Observations and limitations

- The public demo API returns HTTP `200` with `{"reason": "Bad credentials"}` for the invalid-login scenarios tested. Tests assert this observed behavior; it should not be treated as a general recommendation for API authentication design.
- Health-check and successful deletion are asserted as `201` according to the current demo behavior exercised by the suite.
- The scope is functional API testing, **not** performance, security penetration testing, load testing, or exhaustive schema validation.
- The public demo database may reset. Fixtures create fresh booking data and attempt cleanup to minimize cross-test dependencies.
- No product defect has been confirmed from this successful run alone. A genuine bug report needs clear steps to reproduce, an agreed expected result, an actual result, and evidence.

## Related project and documentation

- [Project 2 Part 1 — Restful Booker Postman & Newman](https://github.com/halovie123/api-testing-restful-booker)
- [Restful Booker](https://restful-booker.herokuapp.com/)
- [pytest](https://docs.pytest.org/)
- [Requests Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [jsonschema](https://python-jsonschema.readthedocs.io/)
- [Allure Report for pytest](https://allurereport.org/docs/pytest/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Portfolio focus:** automated REST API testing, test-data fixtures, parametrization, JSON Schema validation, reporting, and continuous integration.
