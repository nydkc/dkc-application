import os, logging
from dkc import *
from models import SurveyResponse

class SurveyHandler(BaseHandler):

    def get(self):
        self.render_template('survey.html')

    def post(self):
        survey_response = SurveyResponse()
        try: # HTTP_X_APPENGINE_CITY is added when deployed
            survey_response.city = os.environ['HTTP_X_APPENGINE_CITY'] # Categorize by location
        except:
            pass
        survey_response.user_agent = os.environ['HTTP_USER_AGENT'] # Categorize by browser type
        survey_response.opinion = self.request.get('opinion')
        survey_response.improvements = self.request.get('improvements')
        survey_response.rating = self.request.get('rating')
        logging.info(survey_response)
        survey_response.put()
        self.render_template('survey-thank_you.html')
