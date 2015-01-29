import webapp2, json, logging
from dkc import *
from models import User

class EventHandler(webapp2.RequestHandler):

    def post(self):
        email_events = json.loads(self.request.body)
        for email_event in email_events:
            if email_event['event'] == "bounce":
                if email_event.has_key('user_id'):
                    user_id = email_event['user_id'] # All sendgrid events should have a user_id
                    applicant = User.get_by_id(int(user_id))
                    application = applicant.application.get()
                    email_sent_to = email_event['email']
                    if email_sent_to == application.verification_ltg_email:
                        application.verification_ltg_sent = False
                        application.verification_ltg_email = "FAILED TO SEND EMAIL TO: " + application.verification_ltg_email
                    if email_sent_to == application.verification_club_president_email:
                        application.verification_club_president_sent = False
                        application.verification_club_president_email = "FAILED TO SEND EMAIL TO: " + application.verification_club_president_email
                    if email_sent_to == application.verification_faculty_advisor_email:
                        application.verification_faculty_advisor_sent = False
                        application.verification_faculty_advisor_email = "FAILED TO SEND EMAIL TO: " + application.verification_faculty_advisor_email
                    application.put()
                    logging.error("Email sending failed for %s under user %s (%s %s - %s)" % (email_sent_to, user_id, applicant.first_name, applicant.last_name, applicant.email))
                else:
                    logging.info(email_event)
            else:
                logging.info(email_event)


application = webapp2.WSGIApplication([
    ('/sendgrid/event', EventHandler),
], debug=True, config=config)
