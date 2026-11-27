
import pytest
import requests


# TC17 - Booking vừa tạo có trong danh sách
def test_new_booking_exists_in_list(booking_client, booking):
    booking_id, _ = booking

    r = booking_client.list()

    assert r.status_code == 200

    ids = [item["bookingid"] for item in r.json()]
    assert booking_id in ids


# TC18 - Danh sách chứa booking ID hợp lệ
def test_booking_ids_are_valid(booking_client, booking):
    booking_id, _ = booking

    r = booking_client.list()

    assert r.status_code == 200

    items = r.json()
    assert isinstance(items, list)

    assert any(
        item["bookingid"] == booking_id
        for item in items
    )

    for item in items:
        assert isinstance(item["bookingid"], int)
        assert item["bookingid"] > 0


# TC19 - Lọc theo cả firstname và lastname
def test_filter_by_full_name(booking_client, booking):
    booking_id, payload = booking

    r = booking_client.list(
        params={
            "firstname": payload["firstname"],
            "lastname": payload["lastname"]
        }
    )

    assert r.status_code == 200

    ids = [item["bookingid"] for item in r.json()]
    assert booking_id in ids


# TC20 - Kiểm tra Content-Type
def test_get_booking_content_type(booking_client, booking):
    booking_id, _ = booking

    r = booking_client.get(booking_id)

    assert r.status_code == 200

    content_type = r.headers.get("Content-Type", "").lower()
    assert "application/json" in content_type


# TC21 - Kiểm tra ngày check-in/check-out
def test_get_booking_dates(booking_client, booking):
    booking_id, payload = booking

    r = booking_client.get(booking_id)

    assert r.status_code == 200

    dates = r.json()["bookingdates"]

    assert dates["checkin"] == payload["bookingdates"]["checkin"]
    assert dates["checkout"] == payload["bookingdates"]["checkout"]


# TC22 - Kiểm tra depositpaid và additionalneeds
def test_get_booking_optional_data(booking_client, booking):
    booking_id, payload = booking

    r = booking_client.get(booking_id)

    assert r.status_code == 200

    body = r.json()

    assert body["depositpaid"] is payload["depositpaid"]
    assert body["additionalneeds"] == payload["additionalneeds"]


# TC23, TC24, TC25 - Tạo booking với 3 mức giá
@pytest.mark.parametrize(
    "price",
    [0, 1, 9999],
    ids=["zero-price", "minimum-positive", "high-price"]
)
def test_create_booking_with_prices(
    booking_client, booking_payload, price
):
    payload = {
        **booking_payload,
        "totalprice": price
    }

    r = booking_client.create(payload)

    assert r.status_code == 200, r.text

    booking_id = r.json()["bookingid"]

    try:
        assert isinstance(booking_id, int)
        assert booking_id > 0

        check = booking_client.get(booking_id)

        assert check.status_code == 200
        assert check.json()["totalprice"] == price

    finally:
        cleanup = booking_client.delete(booking_id)
        assert cleanup.status_code == 201


# TC26 - PUT cập nhật lastname
def test_put_update_lastname(booking_client, booking):
    booking_id, payload = booking

    updated = {
        **payload,
        "lastname": "UpdatedLastname"
    }

    r = booking_client.update(booking_id, updated)

    assert r.status_code == 200
    assert r.json()["lastname"] == "UpdatedLastname"

    check = booking_client.get(booking_id)

    assert check.status_code == 200
    assert check.json()["lastname"] == "UpdatedLastname"


# TC27 - PUT cập nhật depositpaid
def test_put_update_depositpaid(booking_client, booking):
    booking_id, payload = booking

    updated = {
        **payload,
        "depositpaid": False
    }

    r = booking_client.update(booking_id, updated)

    assert r.status_code == 200
    assert r.json()["depositpaid"] is False

    check = booking_client.get(booking_id)

    assert check.status_code == 200
    assert check.json()["depositpaid"] is False


# TC28 - PUT cập nhật bookingdates
def test_put_update_booking_dates(booking_client, booking):
    booking_id, payload = booking

    new_dates = {
        "checkin": "2026-12-01",
        "checkout": "2026-12-05"
    }

    updated = {
        **payload,
        "bookingdates": new_dates
    }

    r = booking_client.update(booking_id, updated)

    assert r.status_code == 200
    assert r.json()["bookingdates"] == new_dates

    check = booking_client.get(booking_id)

    assert check.status_code == 200
    assert check.json()["bookingdates"] == new_dates


# TC29 - PATCH chỉ cập nhật lastname
def test_patch_only_lastname(booking_client, booking):
    booking_id, payload = booking

    r = booking_client.patch(
        booking_id,
        {"lastname": "PatchedLastname"}
    )

    assert r.status_code == 200

    check = booking_client.get(booking_id)

    assert check.status_code == 200

    body = check.json()

    assert body["lastname"] == "PatchedLastname"
    assert body["firstname"] == payload["firstname"]
    assert body["totalprice"] == payload["totalprice"]


# TC30 - PATCH không có xác thực
def test_patch_without_auth_is_rejected(
    booking_client, booking
):
    booking_id, payload = booking

    # Dùng request riêng để không gửi credentials
    r = requests.patch(
        f"{booking_client.base_url}/booking/{booking_id}",
        json={"firstname": "Unauthorized"},
        headers={"Accept": "application/json"},
        timeout=booking_client.timeout
    )

    assert r.status_code in (401, 403)

    check = booking_client.get(booking_id)

    assert check.status_code == 200
    assert check.json()["firstname"] == payload["firstname"]
