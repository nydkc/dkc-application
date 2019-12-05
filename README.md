# Distinguished Key Clubber Application

The application for Distinguished Key Clubber is now online-based with the option of snail mailing it to the awards committee co-chairs. This online application aims to make it easier for the awards committee to keep track of applicants and to make it easier for applicants to keep track of their application.

Hosted on Google App Engine: [http://dkc-app.nydkc.org](http://dkc-app.nydkc.org)

## Features

- Application
    - Overview
    - Profile
    - Part 1: Personal Statement
    - Part 2: International, District & Divisional Projects
    - Part 3: Involvement in Key Club Functions
    - Part 4: Projects, Advocacy & Newsletters
    - Other & Scoring
    - Verification through Email
    - Upload files on Overview and Advocacy
- Account management
    - Password reset
    - Access control for logged in users
    - Block modification after submission
    - Download application as PDF
- Admin Interface
    - Settings
    - View applications
    - Search users by profile information
    - Lists emails of applicants split by submitted status
    - Run datastore queries
    - Handle deleted files

## Requirements

- Google App Engine
    - User authentication
    - NDB
    - Blobstore
    - Mail
- [Sendgrid](https://cloud.google.com/appengine/docs/python/mail/sendgrid)
- [Recaptcha](https://www.google.com/recaptcha/intro/index.html)
- [xhtml2pdf](https://github.com/chrisglass/xhtml2pdf)
    - Install required dependencies using pip: `pip install -r requirements.txt -t lib`
- [html2text](https://github.com/aaronsw/html2text)

## Deployment

```shell
$ gcloud app deploy app.yaml --project dkc-app
```
