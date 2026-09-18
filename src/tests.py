import unittest
from unittest.mock import patch, Mock

import app as app_module
from db_requests import db_create_table


class AppTests(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        app_module.app.config["DB_CURSOR"] = Mock()
        self.client = app_module.app.test_client()

    def tearDown(self):
        app_module.app.config.pop("DB_CURSOR", None)

    @patch("app.db_get_persons")
    def test_get(self, mock_get_persons):
        mock_get_persons.return_value = (
            True,
            [
                {"id": 1, "name": "Alice", "age": 30, "address": "A", "work": "W"},
                {"id": 2, "name": "Bob", "age": 25, "address": None, "work": None},
            ],
        )

        response = self.client.get("/persons")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        mock_get_persons.assert_called_once()

    @patch("app.db_get_by_id")
    def test_get_by_id(self, mock_get_by_id):
        mock_get_by_id.return_value = (
            True,
            {"id": 1, "name": "Alice", "age": 30, "address": "A", "work": "W"},
        )

        response = self.client.get("/persons/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["name"], "Alice")

    @patch("app.db_get_by_id")
    def test_get_by_id_not_found(self, mock_get_by_id):
        mock_get_by_id.return_value = (False, None)

        response = self.client.get("/persons/999")

        self.assertEqual(response.status_code, 404)

    @patch("app.db_post_persons")
    def test_post(self, mock_post):
        mock_post.return_value = (
            True,
            {"id": 1, "name": "Bob", "age": 25, "address": None, "work": None},
        )

        response = self.client.post("/persons", json={"name": "Bob", "age": 25})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["name"], "Bob")
        mock_post.assert_called_once()

    def test_post_missing_name(self):
        response = self.client.post("/persons", json={"age": 25})

        self.assertEqual(response.status_code, 400)

    @patch("app.db_update_persons")
    def test_patch(self, mock_update):
        mock_update.return_value = (
            True,
            {"id": 1, "name": "Bob", "age": 26, "address": None, "work": None},
        )

        response = self.client.patch("/persons/1", json={"age": 26})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["age"], 26)
        mock_update.assert_called_once()

    @patch("app.db_delete_persons")
    def test_delete(self, mock_delete):
        mock_delete.return_value = True

        response = self.client.delete("/persons/1")

        self.assertEqual(response.status_code, 204)

    @patch("app.db_delete_persons")
    def test_delete_not_found(self, mock_delete):
        mock_delete.return_value = False

        response = self.client.delete("/persons/999")

        self.assertEqual(response.status_code, 404)


class DbRequestsTests(unittest.TestCase):
    def test_create(self):
        cursor = Mock()
        cursor.connection = Mock()

        result = db_create_table(cursor)

        self.assertTrue(result)
        cursor.execute.assert_called_once()
        cursor.connection.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
