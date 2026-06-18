import pytest
from dkc.application.models import Application, InternationalProject, GeneralProject
import datetime


def test_application_defaults(ndb_context):
    app = Application()
    app.put()

    assert app.notes == ""
    assert app.graded is None  # BooleanProperty defaults to None if not specified
    assert app.submit_time is None
    assert app.start_time is not None
    assert app.updated_time is not None


def test_application_structured_properties(ndb_context):
    app = Application()

    # Test InternationalProject
    int_project = InternationalProject(
        section="Service", event="Cleanup", description="Cleaning park"
    )
    app.international_projects.append(int_project)

    # Test GeneralProject
    gen_project = GeneralProject(
        event="Fundraiser", location="School", description="Baking sale"
    )
    app.other_projects.append(gen_project)

    app.put()

    fetched_app = app.key.get()
    assert len(fetched_app.international_projects) == 1
    assert fetched_app.international_projects[0].event == "Cleanup"

    assert len(fetched_app.other_projects) == 1
    assert fetched_app.other_projects[0].event == "Fundraiser"
