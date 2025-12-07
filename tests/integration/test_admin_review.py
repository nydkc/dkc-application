import pytest
from unittest.mock import patch, MagicMock
from dkc.auth.models import User
from dkc.application.models import Application
from common.datastore import db


def test_admin_view_application(client):
    email = "applicant@example.com"

    with patch("admin.auth.login_manager.get_current_admin_user") as mock_user, patch(
        "admin.dashboard.query_helpers.find_applicant_and_application_by_email"
    ) as mock_query:

        mock_user.return_value = MagicMock(email="admin@example.com")

        mock_applicant = MagicMock()
        mock_applicant.key.id.return_value = "test_id"
        mock_application = MagicMock()
        mock_application.submit_time = None
        mock_application.personal_statement_choice = None
        mock_query.return_value = (mock_applicant, mock_application)

        response = client.get(f"/admin/show/{email}")
        assert response.status_code == 200


def test_admin_scoring(client):
    email = "applicant@example.com"

    with patch("admin.auth.login_manager.get_current_admin_user") as mock_user, patch(
        "admin.dashboard.query_helpers.find_applicant_and_application_by_email"
    ) as mock_query:

        mock_user.return_value = MagicMock(email="admin@example.com")

        mock_applicant = MagicMock()
        mock_applicant.key.id.return_value = "test_id"
        mock_application = MagicMock()
        mock_application.submit_time = None
        mock_application.personal_statement_choice = None
        mock_query.return_value = (mock_applicant, mock_application)

        response = client.post(f"/admin/show/{email}", data={"graded": "on"})
        assert response.status_code == 200
        assert response.data == b"ok"
