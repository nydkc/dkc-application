import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from dkc.auth.models import User
from dkc.application.models import Application
from common.datastore import db


def test_submission_page_access(client, login, mock_user):
    response = client.get("/application/submit")
    assert response.status_code == 200
    assert b"Submit" in response.data


def test_submit_application(client, login, mock_user, mock_email_provider):
    mock_user.application.get.return_value.verification_ltg = True
    mock_user.application.get.return_value.verification_club_president = True
    mock_user.application.get.return_value.verification_faculty_advisor = True
    mock_user.application.get.return_value.verification_applicant = True

    with patch(
        "dkc.application.submit.get_email_provider", return_value=mock_email_provider
    ) as mock_get_provider:

        response = client.post("/application/submit", follow_redirects=True)

        assert response.status_code == 200
        assert mock_user.application.get().put.called
        assert mock_email_provider.send_email.called


def test_submit_application_already_submitted(client, login, mock_user):
    mock_user.application.get.return_value.submit_time = MagicMock()

    response = client.post("/application/submit", follow_redirects=True)

    assert response.status_code == 409


def test_submit_application_incomplete(client, login, mock_user):
    mock_user.application.get.return_value.school = None

    response = client.post("/application/submit", follow_redirects=True)

    assert response.status_code == 400
