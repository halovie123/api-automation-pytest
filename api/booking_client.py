
from config.settings import (
    BASE_URL,
    TIMEOUT,
    USERNAME,
    PASSWORD
)


class BookingClient:

    def __init__(self, session):
        self.session = session
        self.base_url = BASE_URL
        self.timeout = TIMEOUT
        self.auth = (USERNAME, PASSWORD)

    # GET danh sách booking
    def list(self, params=None):
        return self.session.get(
            f"{self.base_url}/booking",
            params=params,
            timeout=self.timeout
        )

    # POST tạo booking
    def create(self, payload):
        return self.session.post(
            f"{self.base_url}/booking",
            json=payload,
            timeout=self.timeout
        )

    # GET chi tiết booking
    def get(self, booking_id):
        return self.session.get(
            f"{self.base_url}/booking/{booking_id}",
            timeout=self.timeout
        )

    # PUT cập nhật toàn bộ booking
    def update(self, booking_id, payload):
        return self.session.put(
            f"{self.base_url}/booking/{booking_id}",
            json=payload,
            auth=self.auth,
            timeout=self.timeout
        )

    # PATCH cập nhật một phần
    def patch(self, booking_id, payload):
        return self.session.patch(
            f"{self.base_url}/booking/{booking_id}",
            json=payload,
            auth=self.auth,
            timeout=self.timeout
        )

    # DELETE booking
    def delete(self, booking_id):
        return self.session.delete(
            f"{self.base_url}/booking/{booking_id}",
            auth=self.auth,
            timeout=self.timeout
        )
