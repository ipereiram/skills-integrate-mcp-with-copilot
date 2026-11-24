import time
import unittest
from unittest.mock import patch

from fastapi import HTTPException, Request, Response

from src import app
from src.auth import create_teacher_record, verify_teacher_credentials


def make_request(cookie: str = "", scheme: str = "http") -> Request:
    headers = [(b"cookie", cookie.encode("ascii"))] if cookie else []
    return Request(
        {
            "type": "http",
            "scheme": scheme,
            "server": ("testserver", 443 if scheme == "https" else 80),
            "client": ("testclient", 1234),
            "method": "POST",
            "path": "/",
            "query_string": b"",
            "headers": headers,
        }
    )


class TeacherAuthTests(unittest.TestCase):
    def setUp(self):
        app.sessions.clear()

    def test_password_record_verifies_password_without_storing_plaintext(self):
        teacher = create_teacher_record("teacher", "correct horse battery staple")

        self.assertNotIn("password", teacher)
        self.assertTrue(
            verify_teacher_credentials(
                "teacher", "correct horse battery staple", [teacher]
            )
        )
        self.assertFalse(verify_teacher_credentials("teacher", "wrong", [teacher]))
        self.assertFalse(verify_teacher_credentials("unknown", "wrong", [teacher]))

    def test_registration_changes_require_teacher_session(self):
        request = make_request()

        with self.assertRaises(HTTPException) as signup_error:
            app.signup_for_activity("Chess Club", "new@mergington.edu", request)
        with self.assertRaises(HTTPException) as unregister_error:
            app.unregister_from_activity(
                "Chess Club", "michael@mergington.edu", request
            )

        self.assertEqual(signup_error.exception.status_code, 401)
        self.assertEqual(unregister_error.exception.status_code, 401)

    def test_logged_in_teacher_can_register_and_unregister(self):
        session_id = "valid-session"
        app.sessions[session_id] = ("teacher", time.time() + 60)
        request = make_request(f"{app.SESSION_COOKIE}={session_id}")
        email = "new@mergington.edu"

        self.assertIn("Signed up", app.signup_for_activity("Chess Club", email, request)["message"])
        self.assertIn(
            "Unregistered",
            app.unregister_from_activity("Chess Club", email, request)["message"],
        )

    def test_login_sets_secure_session_cookie(self):
        teacher = create_teacher_record("teacher", "correct horse battery staple")
        response = Response()

        with patch("src.app.load_teachers", return_value=[teacher]):
            app.login(
                app.TeacherLogin(
                    username="teacher", password="correct horse battery staple"
                ),
                make_request(scheme="https"),
                response,
            )

        cookie = response.headers["set-cookie"].lower()
        self.assertIn("httponly", cookie)
        self.assertIn("secure", cookie)
        self.assertIn("samesite=lax", cookie)

    def test_expired_session_is_rejected(self):
        app.sessions["expired-session"] = ("teacher", time.time() - 1)

        self.assertIsNone(app.get_session_username("expired-session"))
        self.assertNotIn("expired-session", app.sessions)


if __name__ == "__main__":
    unittest.main()
