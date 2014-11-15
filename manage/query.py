import urllib
from manage import *
from dkc.models import User

def get_application_by_email(email):
    applicant = User.get_by_auth_id(email)
    application = applicant.application.get()
    return applicant, application

def get_all_applicants():
    query = User.query().order(User.division, User.first_name, User.last_name)    
    applicants = query.fetch()     
    return applicants

def get_all_emails():
    query = User.query()
    applicants = query.fetch()
    emails = []
    for applicant in applicants:
        emails.append(applicant.email)
    return emails
