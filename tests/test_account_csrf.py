import unittest

from antipodal.webapp import create_app, store


class AccountDeleteCsrfTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        store.SESSIONS["csrf-test-sid"] = {
            "user_id": 2,
            "mfa_complete": True,
            "csrf_token": "expected-token",
            "created_at": 0,
        }

    def tearDown(self):
        store.SESSIONS.pop("csrf-test-sid", None)

    def test_delete_without_csrf_token_is_rejected(self):
        resp = self.client.post(
            "/account/delete",
            data={},
            headers={"Cookie": "session=csrf-test-sid"},
        )

        self.assertEqual(resp.status_code, 403)
        self.assertIn(2, store.USERS)
        self.assertIn(103, store.LOCATIONS)

    def test_delete_with_wrong_csrf_token_is_rejected(self):
        resp = self.client.post(
            "/account/delete",
            data={"_csrf": "wrong"},
            headers={"Cookie": "session=csrf-test-sid"},
        )

        self.assertEqual(resp.status_code, 403)
        self.assertIn(2, store.USERS)
        self.assertIn(103, store.LOCATIONS)


if __name__ == "__main__":
    unittest.main()
