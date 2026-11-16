import unittest
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException

from app import ALGORITHM, USUARIOS_DB, crear_token_acceso, obtener_usuario_actual


class CurrentUserTokenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.user = USUARIOS_DB["juan"]

    def assert_unauthorized(self, token: str) -> None:
        with self.assertRaises(HTTPException) as error:
            obtener_usuario_actual(token)

        self.assertEqual(error.exception.status_code, 401)

    def test_accepts_valid_token_signed_with_user_session_secret(self) -> None:
        token = crear_token_acceso(
            {"sub": self.user["username"]},
            session_secret=self.user["session_secret"],
            expires_delta=timedelta(minutes=1),
        )

        self.assertIs(obtener_usuario_actual(token), self.user)

    def test_rejects_expired_token(self) -> None:
        token = jwt.encode(
            {
                "sub": self.user["username"],
                "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
            },
            self.user["session_secret"],
            algorithm=ALGORITHM,
        )

        self.assert_unauthorized(token)

    def test_rejects_token_signed_with_wrong_secret(self) -> None:
        token = jwt.encode(
            {
                "sub": self.user["username"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
            },
            "wrong-secret-that-is-long-enough-for-hs256",
            algorithm=ALGORITHM,
        )

        self.assert_unauthorized(token)

    def test_rejects_token_without_expiration(self) -> None:
        token = jwt.encode(
            {"sub": self.user["username"]},
            self.user["session_secret"],
            algorithm=ALGORITHM,
        )

        self.assert_unauthorized(token)

    def test_rejects_token_for_unknown_user(self) -> None:
        token = jwt.encode(
            {
                "sub": "unknown-user",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
            },
            self.user["session_secret"],
            algorithm=ALGORITHM,
        )

        self.assert_unauthorized(token)


if __name__ == "__main__":
    unittest.main()
