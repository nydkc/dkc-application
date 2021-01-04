import json
import io
import logging
import urllib.request
import xhtml2pdf.pisa as pisa


def verify_captcha(recaptcha_secret, grecaptcha):
    grecaptcha_verification_data = {"secret": recaptcha_secret, "response": grecaptcha}
    try:
        recaptcha_response = json.loads(
            urllib.request.urlopen(
                "https://www.google.com/recaptcha/api/siteverify",
                data=urllib.urlencode(grecaptcha_verification_data),
            ).read()
        )
        recaptcha_success = recaptcha_response["success"]
    except Exception as e:
        logging.warning("Could not verify recaptcha: %s", e)
        recaptcha_success = False
    return recaptcha_success


def generate_pdf(html_data):
    html_data = html_data.encode("utf8")
    html_data = io.BytesIO(html_data)

    output = io.BytesIO()
    pisa.log.setLevel("WARNING")  # suppress debug log output
    pdf = pisa.CreatePDF(
        html_data,
        output,
        encoding="utf-8",
    )

    pdf_data = pdf.dest.getvalue()
    return pdf_data
