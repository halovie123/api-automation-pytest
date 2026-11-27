
import json
from pathlib import Path

import pytest
import requests

from api.booking_client import BookingClient
from config.settings import (
    BASE_URL,
    TIMEOUT,
    USERNAME,
    PASSWORD
)


# Fixture 1: HTTP session
@pytest.fixture(scope="session")
def api():
    session = requests.Session()

    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })

    yield session

    session.close()


# Fixture 2: BookingClient
@pytest.fixture(scope="session")
def booking_client(api):
    return BookingClient(api)


# Fixture 3: Token
@pytest.fixture(scope="session")
def token(api):
    response = api.post(
        f"{BASE_URL}/auth",
        json={
            "username": USERNAME,
            "password": PASSWORD
        },
        timeout=TIMEOUT
    )

    response.raise_for_status()

    token_value = response.json()["token"]

    assert isinstance(token_value, str)
    assert token_value

    return token_value


# Fixture 4: Dữ liệu booking
@pytest.fixture
def booking_payload():
    data_file = (
        Path(__file__).resolve().parent
        / "data"
        / "bookings.json"
    )

    with data_file.open(encoding="utf-8") as f:
        data = json.load(f)

    return data["valid_booking"]


# Fixture 5: Tạo và dọn booking
@pytest.fixture
def booking(booking_client, booking_payload):
    payload = booking_payload

    # SETUP
    response = booking_client.create(payload)

    assert response.status_code == 200, response.text

    booking_id = response.json()["bookingid"]

    try:
        yield booking_id, payload

    finally:
        # TEARDOWN
        check = booking_client.get(booking_id)

        if check.status_code == 200:
            cleanup = booking_client.delete(booking_id)

            assert cleanup.status_code == 201, (
                f"Cleanup failed: "
                f"{cleanup.status_code} {cleanup.text}"
            )

        elif check.status_code != 404:
            raise AssertionError(
                f"Unexpected cleanup status: "
                f"{check.status_code}"
            )
