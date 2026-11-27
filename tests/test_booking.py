
import pytest
import requests
from jsonschema import validate

from settings import BASE_URL, USERNAME, PASSWORD


BOOKING_SCHEMA = {
    "type": "object",
    "required": [
        "firstname",
        "lastname",
        "totalprice",
        "depositpaid",
        "bookingdates"
    ],
    "properties": {
        "firstname": {"type": "string"},
        "lastname": {"type": "string"},
        "totalprice": {"type": "number"},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin": {"type": "string"},
                "checkout": {"type": "string"}
            }
        },
        "additionalneeds": {"type": "string"}
    }
}


# TC01 - Health check
@pytest.mark.smoke
def test_health_check(api):
    r = api.get(f"{BASE_URL}/ping", timeout=10)

    assert r.status_code == 201
    assert r.text.strip() == "Created"


# TC02 - Authentication thành công
@pytest.mark.smoke
def test_auth_valid_token(token):
    assert isinstance(token, str)
    assert len(token) > 0


# TC03, TC04, TC05 - Authentication thất bại
@pytest.mark.parametrize(
    "username, password",
    [
        ("admin", "wrongpassword"),
        ("", "password123"),
        ("admin", "")
    ]
)
def test_auth_invalid_credentials(api, username, password):
    r = api.post(
        f"{BASE_URL}/auth",
        json={
            "username": username,
            "password": password
        },
        timeout=10
    )

    assert r.status_code == 200

    body = r.json()
    assert body["reason"] == "Bad credentials"
    assert "token" not in body


# TC06 - GET danh sách bookings
def test_get_all_bookings(api):
    r = api.get(f"{BASE_URL}/booking", timeout=10)

    assert r.status_code == 200
    assert isinstance(r.json(), list)


# TC07 - POST tạo booking
def test_create_booking_returns_valid_id(booking):
    booking_id, payload = booking

    assert isinstance(booking_id, int)
    assert booking_id > 0
    assert payload["firstname"] == "Minh"


# TC08 - GET booking vừa tạo
@pytest.mark.smoke
def test_get_booking_returns_created_data(
    booking_client, booking
):
    booking_id, payload = booking

    r = booking_client.get(booking_id)

    assert r.status_code == 200

    body = r.json()

    assert body["firstname"] == payload["firstname"]
    assert body["lastname"] == payload["lastname"]
    assert body["totalprice"] == payload["totalprice"]


# TC09 - Kiểm tra JSON Schema
def test_get_booking_schema(api, booking):
    booking_id, _ = booking

    r = api.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=10
    )

    assert r.status_code == 200

    validate(
        instance=r.json(),
        schema=BOOKING_SCHEMA
    )


# TC10 - GET booking không tồn tại
def test_get_unknown_booking_returns_404(api):
    r = api.get(
        f"{BASE_URL}/booking/999999999",
        timeout=10
    )

    assert r.status_code == 404


# TC11 - Lọc theo firstname
def test_filter_booking_by_firstname(api, booking):
    booking_id, payload = booking

    r = api.get(
        f"{BASE_URL}/booking",
        params={"firstname": payload["firstname"]},
        timeout=10
    )

    assert r.status_code == 200

    ids = [item["bookingid"] for item in r.json()]
    assert booking_id in ids


# TC12 - Lọc theo lastname
def test_filter_booking_by_lastname(api, booking):
    booking_id, payload = booking

    r = api.get(
        f"{BASE_URL}/booking",
        params={"lastname": payload["lastname"]},
        timeout=10
    )

    assert r.status_code == 200

    ids = [item["bookingid"] for item in r.json()]
    assert booking_id in ids


# TC13 - PUT cập nhật booking hợp lệ
def test_update_booking(api, booking):
    booking_id, payload = booking

    updated = payload.copy()
    updated["firstname"] = "MinhUpdated"
    updated["totalprice"] = 200

    r = api.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=updated,
        auth=(USERNAME, PASSWORD),
        timeout=10
    )

    assert r.status_code == 200
    assert r.json()["firstname"] == "MinhUpdated"
    assert r.json()["totalprice"] == 200

    # Kiểm tra dữ liệu đã được lưu
    check = api.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=10
    )

    assert check.status_code == 200
    assert check.json()["firstname"] == "MinhUpdated"


# TC14 - PUT không có xác thực
def test_update_without_token_is_rejected(booking):
    booking_id, payload = booking

    updated = payload.copy()
    updated["firstname"] = "Unauthorized"

    # Request độc lập, không kèm auth/cookie
    r = requests.put(
        f"{BASE_URL}/booking/{booking_id}",
        json=updated,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        timeout=10
    )

    assert r.status_code in (401, 403)


# TC15 - PATCH cập nhật một phần
def test_patch_booking(api, booking):
    booking_id, payload = booking

    r = api.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json={"additionalneeds": "Late checkout"},
        auth=(USERNAME, PASSWORD),
        timeout=10
    )

    assert r.status_code == 200

    body = r.json()
    assert body["additionalneeds"] == "Late checkout"
    assert body["firstname"] == payload["firstname"]


# TC16 - DELETE và xác minh xóa thành công
@pytest.mark.smoke
def test_delete_booking(api, booking):
    booking_id, _ = booking

    r = api.delete(
        f"{BASE_URL}/booking/{booking_id}",
        auth=(USERNAME, PASSWORD),
        timeout=10
    )

    assert r.status_code == 201
    assert r.text.strip() == "Created"

    # GET lại sau khi xóa
    check = api.get(
        f"{BASE_URL}/booking/{booking_id}",
        timeout=10
    )

    assert check.status_code == 404
