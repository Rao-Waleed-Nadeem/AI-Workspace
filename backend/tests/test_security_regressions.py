import contextlib
import io
import logging
import unittest
from unittest.mock import patch

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.testclient import TestClient

from app.core.logging_config import SecretRedactionFilter
from app.main import app
from app.routes.auth import login


class SecurityRegressionTests(unittest.TestCase):
    def test_login_route_does_not_print_credentials(self):
        with patch(
            "app.routes.auth.auth_service.login",
            return_value={"access_token": "token", "token_type": "bearer"},
        ) as mock_login:
            form_data = OAuth2PasswordRequestForm(
                username="alice@example.com",
                password="super-secret-password",
            )

            with io.StringIO() as captured, contextlib.redirect_stdout(captured):
                result = login(
                    form_data=form_data,
                    db=None,
                    _=None,
                )
                output = captured.getvalue()

            self.assertEqual(result["access_token"], "token")
            self.assertNotIn("alice@example.com", output)
            self.assertNotIn("super-secret-password", output)
            mock_login.assert_called_once()

    def test_security_headers_are_present(self):
        client = TestClient(app)

        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["x-content-type-options"], "nosniff")
        self.assertEqual(response.headers["x-frame-options"], "DENY")
        self.assertEqual(
            response.headers["referrer-policy"],
            "strict-origin-when-cross-origin",
        )

    def test_secret_redaction_filter_sanitizes_sensitive_messages(self):
        record = logging.LogRecord(
            name="audit.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="Authorization: Bearer secret-value",
            args=(),
            exc_info=None,
        )

        filter_ = SecretRedactionFilter()
        self.assertTrue(filter_.filter(record))
        self.assertEqual(record.msg, "Sensitive log message suppressed.")
        self.assertEqual(record.args, ())


if __name__ == "__main__":
    unittest.main()
