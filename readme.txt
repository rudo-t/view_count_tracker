Instructions for using automated tracker

This tracker will extract zendesk view counts from the api, create a google sheet and load the zendesk count extract to this sheet.

When first run it will establish OAuth credentials with Google.

Prerequisites:
    A Google account with Google API authorisation

    Zendesk api access token and user email, subdomain, view ids retrieved.
    Access to the internet and a web browser.
    Python 3.5
    requests and googlepythonapi python libraries


Directions for use:

1.Retrieve and store api token from zendesk. Further instructions on how to do this will are found at:

    https://support.zendesk.com/hc/en-us/articles/226022787-Generating-a-new-API-token-

2.Setup Google OAuth2 access credentials. Instructions can be found here under steps at the following page

    https://developers.google.com/sheets/api/quickstart/python.

3.Place the 'client_secret.json' in the view_count_tracker working directory.

4.At the command line, install needed packages with the following command

    pip install requests google-api-python-client

5.At the command line

    python tracker.py

Upon first run, the google api will request authorisation via a webpage

Notes:
All times listed are local to the device running the script.
