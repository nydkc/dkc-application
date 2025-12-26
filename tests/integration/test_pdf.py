import pytest
from unittest.mock import patch, MagicMock
from werkzeug.exceptions import Forbidden
from google.cloud import ndb


def test_download_pdf(client, login, mock_user):
    # Patch check_access to avoid key comparison issues
    # Patch ndb.Key to return a mock key that yields a mock user
    # Patch User so assertion works
    with patch("dkc.application.download_pdf.check_access") as mock_check_access, \
         patch("dkc.application.download_pdf.ndb.Key") as mock_key_cls, \
         patch("dkc.application.download_pdf.generate_pdf") as mock_generate_pdf, \
         patch("dkc.application.download_pdf.render_template") as mock_render_template, \
         patch("dkc.application.download_pdf.User") as mock_user_cls:

        mock_check_access.return_value = None # Success

        mock_applicant = MagicMock()
        mock_application = MagicMock()
        mock_applicant.application.get.return_value = mock_application

        mock_key_instance = MagicMock()
        mock_key_instance.get.return_value = mock_applicant
        mock_key_cls.return_value = mock_key_instance

        mock_generate_pdf.return_value = b"%PDF-1.4..."
        mock_render_template.return_value = "<html></html>"

        response = client.get("/application/download/pdf/123-test.pdf")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/pdf"
        assert response.headers["Content-Disposition"] == "inline; filename=test.pdf"

        # Verify check_access was called with correct ID
        # Use ANY for the class arg since usage of real vs mock class can be tricky with imports
        from unittest.mock import ANY
        mock_key_cls.assert_called_with(ANY, 123)


def test_download_pdf_access_denied(client, login, mock_user):
    # Patch check_access to raise Forbidden (abort(403))

    with patch("dkc.application.download_pdf.check_access") as mock_check_access, \
         patch("dkc.application.download_pdf.ndb.Key"):

        # dkc.application.download_pdf imports abort from flask.
        # But check_access calls abort(403) which raises HTTPException.
        # We can simulate this by side_effect=Forbidden() if we import Forbidden from werkzeug.exceptions

        mock_check_access.side_effect = Forbidden()

        response = client.get("/application/download/pdf/456-other.pdf")

        assert response.status_code == 403
