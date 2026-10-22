import unittest

from antipodal.webapp import create_app, store


class AccountEmailCsrfTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.original_email = store.USERS[2]["email"]
        store.SESSIONS["test-session"] = {
            "user_id": 2,
            "mfa_complete": True,
            "csrf_token": "expected-token",
            "created_at": 0,
        }

    def tearDown(self):
        store.USERS[2]["email"] = self.original_email
        store.SESSIONS.pop("test-session", None)

    def test_email_change_without_csrf_token_is_rejected(self):
        resp = self.client.post(
            "/account/email",
            data={"email": "changed@example.com"},
            headers={"Cookie": "session=test-session"},
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(store.USERS[2]["email"], self.original_email)

    def test_email_change_with_valid_csrf_token_succeeds(self):
        resp = self.client.post(
            "/account/email",
            data={"email": "changed@example.com", "_csrf": "expected-token"},
            headers={"Cookie": "session=test-session"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(store.USERS[2]["email"], "changed@example.com")


if __name__ == "__main__":
    unittest.main()
