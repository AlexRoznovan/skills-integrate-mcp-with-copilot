import tempfile
import unittest
from pathlib import Path
from fastapi import HTTPException

from auth import (
    add_teacher,
    authenticate_teacher,
    create_session,
    verify_session,
)
from app import app, require_teacher


class TeacherAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.teacher_file = Path(self.temp_dir.name) / "teachers.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_teacher_password_is_hashed_and_verified(self):
        add_teacher("teacher", "a-long-password", self.teacher_file)

        self.assertTrue(
            authenticate_teacher("teacher", "a-long-password", self.teacher_file)
        )
        self.assertFalse(
            authenticate_teacher("teacher", "wrong-password", self.teacher_file)
        )
        self.assertFalse(
            authenticate_teacher("unknown", "a-long-password", self.teacher_file)
        )
        self.assertNotIn("a-long-password", self.teacher_file.read_text())

    def test_session_rejects_tampering_and_expiration(self):
        token = create_session("teacher", "test-secret", now=100)

        self.assertEqual(verify_session(token, "test-secret", now=101), "teacher")
        self.assertIsNone(verify_session(token + "tampered", "test-secret", now=101))
        self.assertIsNone(verify_session(token, "test-secret", now=100 + 8 * 60 * 60))

    def test_mutation_routes_require_teacher_dependency(self):
        protected_paths = {
            "/activities/{activity_name}/signup",
            "/activities/{activity_name}/unregister",
        }
        routes = [route for route in app.routes if route.path in protected_paths]

        self.assertEqual(len(routes), 2)
        for route in routes:
            self.assertIn(
                require_teacher,
                [dependency.call for dependency in route.dependant.dependencies],
            )

    def test_missing_teacher_session_is_unauthorized(self):
        with self.assertRaises(HTTPException) as error:
            require_teacher(None)

        self.assertEqual(error.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()