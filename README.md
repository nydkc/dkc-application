# Distinguished Key Clubber Application

The application for Distinguished Key Clubber is now online, with the option of _snail mailing_ it to the NY District Awards Committee. This online application aims to streamline the awards process by making it easier for the awards committee to keep track of applicants, and making it easier for applicants to keep track of their application.

Built using Flask and hosted on Google App Engine: [http://dkc-app.nydkc.org](http://dkc-app.nydkc.org)

## Features

- Application
    - Overview
    - Profile
    - Part 1: Personal Statement
    - Part 2: International, District & Divisional Projects
    - Part 3: Involvement in Key Club Functions
    - Part 4: Projects, Advocacy & Newsletters
    - Other & Scoring
    - Verification (through email to trusted parties)
    - File uploads to GCS, in relevant sections for Advocacy, Newsletter and Other materials
    - Download application as PDF
- Account management
    - User login and registration
    - Forgot password / Password reset
    - Access control and isolation of user applications
    - Prevent modification after submission
- Admin Interface
    - Protected by OAuth2 and Google Cloud IAM
    - Settings
    - View applications
    - Search users by information on Profile
    - Lists emails of applicants, split by submission status
    - Run datastore queries _(hidden url)_
    - Delete applications _(hiddent url)_

## Requirements

- Google Cloud
    - Google App Engine (GAE)
    - Google Cloud Datastore
    - Google Cloud Storage (GCS)
    - Google Cloud IAM
    - Google Cloud Logging
    - Google Cloud Build
    - OAuth2
- ~[SendGrid](https://github.com/sendgrid/sendgrid-python)~ [MailerSend](https://github.com/mailersend/mailersend-python)
- [Recaptcha](https://www.google.com/recaptcha)
- [requirements.txt](src/requirements.txt)

## Deployment

```console
$ gcloud app deploy app.yaml --project dkc-app
```

**NOTE:** Google Cloud Build is integrated with this repository, which deploys the latest code that is pushed.

## Local Development

Python 3+ is required to run the DKC Application. The recommended development setup is to use Python's [Virtual Environment (venv)](https://docs.python.org/3/library/venv.html) to install dependencies from [pip](https://pypi.org/project/pip/).

```console
$ virtualenv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ pip install -r src/requirements.txt
```

The Google Cloud SDK will also need to be installed, following instructions at https://cloud.google.com/sdk/docs/quickstart. Once installed, follow the instructions to [create Google Application Credentials for a service account](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys), which will be needed for the next step.

With the Python `venv` and Google Cloud SDK setups complete, it is now possible to run locally:

```console
(venv) $ ./run_local.sh --google_application_credentials=<service_account_json_key_file>
```

The `run_local.sh` script will start a Google Cloud Datastore Emulator as well as the Google App Engine `dev_appserver` to run the DKC Application. It will automatically reload the code when changes are made.
