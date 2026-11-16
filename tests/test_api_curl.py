import json
import os
import subprocess
import unittest


class ApiCurlTests(unittest.TestCase):
    base_url = os.environ.get("JWT_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

    def curl(self, *arguments: str) -> tuple[int, str]:
        result = subprocess.run(
            [
                "curl",
                "--silent",
                "--show-error",
                "--write-out",
                "\n%{http_code}",
                *arguments,
            ],
            capture_output=True,
            check=True,
            text=True,
        )
        body, separator, status = result.stdout.rpartition("\n")
        if not separator:
            self.fail("curl did not return an HTTP status code")
        return int(status), body

    def test_health_endpoint(self) -> None:
        status, response = self.curl(f"{self.base_url}/health")

        self.assertEqual(status, 200)
        self.assertEqual(json.loads(response)["status"], "healthy")

    def test_valid_login_allows_profile_access(self) -> None:
        status, response = self.curl(
            "--request",
            "POST",
            "--header",
            "Content-Type: application/x-www-form-urlencoded",
            "--data-urlencode",
            "username=juan",
            "--data-urlencode",
            "password=password123",
            f"{self.base_url}/token",
        )

        self.assertEqual(status, 200, response)
        token = json.loads(response)["access_token"]
        profile_status, profile_response = self.curl(
            "--header",
            f"Authorization: Bearer {token}",
            f"{self.base_url}/users/me",
        )

        self.assertEqual(profile_status, 200, profile_response)
        self.assertEqual(json.loads(profile_response)["username"], "juan")

    def test_invalid_login_is_rejected(self) -> None:
        status, _ = self.curl(
            "--request",
            "POST",
            "--header",
            "Content-Type: application/x-www-form-urlencoded",
            "--data-urlencode",
            "username=juan",
            "--data-urlencode",
            "password=incorrect",
            f"{self.base_url}/token",
        )

        self.assertEqual(status, 401)

    def test_missing_bearer_token_is_rejected(self) -> None:
        status, _ = self.curl(f"{self.base_url}/users/me")

        self.assertEqual(status, 401)

    def test_invalid_bearer_token_is_rejected(self) -> None:
        status, _ = self.curl(
            "--header",
            "Authorization: Bearer invalid-token",
            f"{self.base_url}/users/me",
        )

        self.assertEqual(status, 401)


if __name__ == "__main__":
    unittest.main()
