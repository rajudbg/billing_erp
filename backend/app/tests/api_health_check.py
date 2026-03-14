from __future__ import annotations

import requests

BASE_URL = "http://localhost:8000"


def check_health() -> None:
    resp = requests.get(f"{BASE_URL}/health")
    print("GET /health:", resp.status_code, resp.json())


def check_login() -> None:
    payload = {"email": "admin@example.com", "password": "admin123"}
    resp = requests.post(f"{BASE_URL}/api/v1/auth/login-json", json=payload)
    print("POST /api/v1/auth/login-json:", resp.status_code, resp.json())
    if resp.ok:
        return resp.json()["access_token"]
    return None


def check_dashboard_summary(token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/v1/dashboard/summary", headers=headers)
    print("GET /api/v1/dashboard/summary:", resp.status_code, resp.json())


def main() -> None:
    check_health()
    token = check_login()
    if token:
        check_dashboard_summary(token)
    else:
        print("Login failed; skipping dashboard check.")


if __name__ == "__main__":
    main()

