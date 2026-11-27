
import os


BASE_URL = os.getenv(
    "BASE_URL",
    "https://restful-booker.herokuapp.com"
).rstrip("/")

TIMEOUT = float(os.getenv("API_TIMEOUT", "10"))

USERNAME = os.getenv("RB_USERNAME", "admin")
PASSWORD = os.getenv("RB_PASSWORD", "password123")
