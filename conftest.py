
import pytest
import requests

from settings import BASE_URL, USERNAME, PASSWORD


# Fixture 1: Tạo HTTP session
@pytest.fixture(scope="session")
def api():
    s = requests.Session()

    s.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })

    yield s

    s.close()


# Fixture 2: Tạo token
@pytest.fixture(scope="session")
def token(api):
    response = api.post(
        f"{BASE_URL}/auth",
        json={
            "username": USERNAME,
            "password": PASSWORD
        },
        timeout=10
    )

    response.raise_for_status()

    token_value = response.json()["token"]

    assert isinstance(token_value, str)
    assert token_value

    return token_value


# Fixture 3: Tạo và dọn booking
@pytest.fixture
def booking(api, token):
    payload = {
        "firstname": "Minh",
        "lastname": "Tran",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-11-01",
            "checkout": "2026-11-03"
        },
        "additionalneeds": "Breakfast"
    }

    # SETUP: Tạo booking mới
    response = api.post(
        f"{BASE_URL}/booking",
        json=payload,
        timeout=10
    )

    assert response.status_code == 200, response.text

    booking_id = response.json()["bookingid"]

    yield booking_id, payload

    # TEARDOWN: Xóa booking nếu vẫn tồn tại
    check = api.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=10
    )

    if check.status_code == 404:
        return

    assert check.status_code == 200, check.text

    cleanup = api.delete(
        f"{BASE_URL}/booking/{booking_id}",
        auth=(USERNAME, PASSWORD),
        timeout=10
    )

    assert cleanup.status_code == 201, (
        f"Cleanup failed: {cleanup.status_code} "
        f"{cleanup.text}"
    )
