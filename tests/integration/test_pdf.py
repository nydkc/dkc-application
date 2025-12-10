import pytest
from unittest.mock import patch, MagicMock
from dkc.auth.models import User
from dkc.application.models import Application
from common.models import Settings
from datetime import datetime
from google.cloud import ndb


def test_download_pdf(client, login, mock_user, ndb_context):
    real_user = User(id=123, email="test@example.com")
    real_user.put()

    app = Application(parent=real_user.key)
    app.put()
    real_user.application = app.key
    real_user.put()

    mock_user.key = real_user.key

    with patch("dkc.application.download_pdf.generate_pdf") as mock_generate_pdf, patch(
        "dkc.application.download_pdf.render_template"
    ) as mock_render_template:

        mock_generate_pdf.return_value = b"%PDF-1.4..."
        mock_render_template.return_value = "<html></html>"

        response = client.get("/application/download/pdf/123-test.pdf")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/pdf"
        assert response.headers["Content-Disposition"] == "inline; filename=test.pdf"

        mock_generate_pdf.assert_called()
        mock_render_template.assert_called()


def test_download_pdf_access_denied(client, login, mock_user, ndb_context):
    other_user = User(id=456, email="other@example.com")
    other_user.put()

    mock_user.key = ndb.Key(User, 123)

    response = client.get("/application/download/pdf/456-other.pdf")

    assert response.status_code == 403
