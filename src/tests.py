import os
import unittest
from unittest.mock import patch, Mock

import psycopg2
from psycopg2.extras import RealDictCursor

from db_requests import *
import app as app_module

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



TEST_DB_CONFIG = {
    "database": os.getenv("TEST_DB_NAME", "persons_test"),
    "host": os.getenv("TEST_DB_HOST", "localhost"),
    "user": os.getenv("TEST_DB_USER", "postgres"),
    "password": os.getenv("TEST_DB_PASSWORD", "postgres"),
    "port": os.getenv("TEST_DB_PORT", "5432"),
}


class IntegrationDbTests(unittest.TestCase):
    """Тесты реального взаимодействия с PostgreSQL.

    Требуют запущенного PostgreSQL и тестовой БД.
    Параметры подключения берутся из переменных окружения:
      TEST_DB_NAME, TEST_DB_HOST, TEST_DB_USER, TEST_DB_PASSWORD, TEST_DB_PORT
    """

    def setUp(self):
        try:
            self.conn = psycopg2.connect(
                database=TEST_DB_CONFIG["database"],
                host=TEST_DB_CONFIG["host"],
                user=TEST_DB_CONFIG["user"],
                password=TEST_DB_CONFIG["password"],
                port=TEST_DB_CONFIG["port"],
            )
        except psycopg2.OperationalError as e:
            self.skipTest(f"PostgreSQL недоступен: {e}")

        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.schema = "test_persons_schema"

        self.cursor.execute(f"DROP SCHEMA IF EXISTS {self.schema} CASCADE;")
        self.cursor.execute(f"CREATE SCHEMA {self.schema};")
        self.cursor.execute(f"SET search_path TO {self.schema};")
        self.conn.commit()

        db_create_table(self.cursor)

    def tearDown(self):
        if hasattr(self, "conn") and self.conn:
            self.cursor.execute(f"DROP SCHEMA IF EXISTS {self.schema} CASCADE;")
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def test_create_table(self):
        """Проверяем, что db_create_table действительно создаёт таблицу."""
        self.cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = 'persons';
        """, (self.schema,))
        row = self.cursor.fetchone()
        self.assertIsNotNone(row)

    def test_post_and_get_by_id(self):
        # INSERT + SELECT по id.
        status, person = db_post_persons(
            self.cursor,
            name="Alice",
            age=30,
            address="Moscow",
            work="Engineer",
        )
        self.assertTrue(status)
        self.assertEqual(person["name"], "Alice")
        self.assertEqual(person["age"], 30)
        person_id = person["id"]

        status, fetched = db_get_by_id(self.cursor, person_id)
        self.assertTrue(status)
        self.assertEqual(fetched["name"], "Alice")
        self.assertEqual(fetched["address"], "Moscow")

    def test_get_by_id_not_found(self):
        # SELECT несуществующего id.
        status, fetched = db_get_by_id(self.cursor, 99999)
        self.assertFalse(status)
        self.assertIsNone(fetched)

    def test_get_persons(self):
        # SELECT всех записей.
        db_post_persons(self.cursor, name="Alice", age=30)
        db_post_persons(self.cursor, name="Bob", age=25)

        status, persons = db_get_persons(self.cursor)
        self.assertTrue(status)
        self.assertEqual(len(persons), 2)
        names = [p["name"] for p in persons]
        self.assertIn("Alice", names)
        self.assertIn("Bob", names)

    def test_update_persons(self):
        # UPDATE существующей записи.
        status, person = db_post_persons(
            self.cursor, name="Alice", age=30, address="Moscow", work="Engineer"
        )
        person_id = person["id"]

        status, updated = db_update_persons(
            self.cursor,
            person_id,
            {"age": 31, "work": "Manager"},
        )
        self.assertTrue(status)
        self.assertEqual(updated["age"], 31)
        self.assertEqual(updated["work"], "Manager")
        self.assertEqual(updated["name"], "Alice")

    def test_update_persons_not_found(self):
        # UPDATE несуществующего id.
        status, updated = db_update_persons(
            self.cursor, 99999, {"age": 99}
        )
        self.assertFalse(status)
        self.assertIsNone(updated)

    def test_delete_persons(self):
        # DELETE существующей записи.
        status, person = db_post_persons(self.cursor, name="Alice", age=30)
        person_id = person["id"]

        deleted = db_delete_persons(self.cursor, person_id)
        self.assertTrue(deleted)

        status, fetched = db_get_by_id(self.cursor, person_id)
        self.assertFalse(status)
        self.assertIsNone(fetched)

    def test_delete_persons_not_found(self):
        # DELETE несуществующего id.
        deleted = db_delete_persons(self.cursor, 99999)
        self.assertFalse(deleted)


if __name__ == "__main__":
    unittest.main()
