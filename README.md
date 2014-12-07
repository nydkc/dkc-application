# Distinguished Key Clubber Application

The application for Distinguished Key Clubber is now online-based with the option of snail mailing it to the awards committee co-chairs. This online application aims to make it easier to the awards committee to keep track of applicants and to make it easier for applicants to keep track of their application.

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
    - Verification
- Account management
    - Password reset
    - Access control for logged in users
    - Block modification after submission
    - Download application as PDF
- Admin Interface
    - View applications
    - Search users by profile information
    - Lists emails of applicants split by submitted status

## Requirements

- Google App Engine
    - User authentication
    - NDB
    - Blobstore
    - Mail
- [xhtml2pdf](https://github.com/chrisglass/xhtml2pdf)
    - Install required dependencies using pip: `pip install -r requirements.txt -t lib`
- [html2text](https://github.com/aaronsw/html2text)

## Notes
- There is a bug with Google App Engine's Push-To-Deploy, so to get the PDF Generation to work correctly, the application must be deployed using the GAE App.
- Backup datastore using `appcfg.py download_data --email=INSERT_EMAIL_HERE --url=http://dkc-app.appspot.com/_ah/remote_api --filename=backup`
- Upload datastore to local development using `appcfg.py upload_data --filename=backup --application=dev~dkc-app --url=http://localhost:20000/_ah/remote_api`
