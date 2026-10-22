import copy
import unittest

from antipodal.webapp import create_app, store


class AdminMfaTests(unittest.TestCase):
    def setUp(self):
        self.users_backup = copy.deepcopy(store.USERS)
        self.client = create_app().test_client()
        store.SESSIONS["pw-only"] = {
            "user_id": 3,
            "mfa_complete": False,
            "csrf_token": "x",
            "created_at": 0,
        }
        store.SESSIONS["mfa-done"] = {
            "user_id": 3,
            "mfa_complete": True,
            "csrf_token": "y",
            "created_at": 0,
        }

    def tearDown(self):
        store.USERS.clear()
        store.USERS.update(self.users_backup)
        store.SESSIONS.pop("pw-only", None)
        store.SESSIONS.pop("mfa-done", None)

    def test_delete_requires_completed_mfa(self):
        resp = self.client.delete(
            "/api/admin/users/2", headers={"Cookie": "session=pw-only"}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertIn(2, store.USERS)

    def test_delete_allowed_after_mfa(self):
        resp = self.client.delete(
            "/api/admin/users/2", headers={"Cookie": "session=mfa-done"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(2, store.USERS)


if __name__ == "__main__":
    unittest.main()
