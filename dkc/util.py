import json, logging
import urllib, urllib2

def verify_captcha(recaptcha_secret, grecaptcha):
    grecaptcha_verification_data = {
        "secret": recaptcha_secret,
        "response": grecaptcha
    }
    try:
        recaptcha_response = json.loads(urllib2.urlopen("https://www.google.com/recaptcha/api/siteverify", data=urllib.urlencode(grecaptcha_verification_data)).read())
        recaptcha_success = recaptcha_response['success']
    except Exception as e:
        logging.warning('Could not verify recaptcha: %s', e)
        recaptcha_success = False
    return recaptcha_success
