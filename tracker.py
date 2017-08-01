import time
import requests
import threading
import google_credentials
from apiclient import discovery

#class for google sheets interface
class GoogleSheets():
    def __init__(self):
        # establish credentials for google sheets access
        self.credentials = google_credentials.get_credentials()
        # create service object to be used with sheets api
        self.service = discovery.build('sheets', 'v4', credentials=self.credentials)

    def create_spreadsheet(self, sheet_title='zendesk_view_count'):
        # Setup the details needed to instantiate the google sheet
        sheet_properties = {'title': sheet_title}
        #worksheet_properties = {'title': 'sheet1_zendesk_view_count'}
        headers = ['date_time', 'view_id', 'view_title', 'ticket_count']
        # apply json formatting for google sheets api
        values = [{'userEnteredValue': {'stringValue': value}} for value in headers]
        spreadsheet_body = {
            'properties': sheet_properties,
            'sheets': [
                {  # "properties": worksheet_properties,
                    "data": [{"rowData": [{"values": values}]}]
                }]}
        # launch request and parse response
        request = self.service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()
        self.spreadsheet_id = response['spreadsheetId']
        self.sheet_url = response['spreadsheetUrl']
        print('Spreadsheet created in Google Sheets! View counts will be available at the following URL: \n\n\t{}'.format(self.sheet_url))

    def load(self, zendesk_data):
        # create data to be loaded into google sheets
        values = zendesk_data
        body = {'values': values}
        value_input_option = 'USER_ENTERED'

        request = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            valueInputOption=value_input_option,
            range="A:D",
            body=body)

        response = request.execute()

        print('{} rows have been updated '.format(response['updates']['updatedRows']))


class ExtractZendeskData():
    def __init__(self, email, subdomain, zendesk_api_token, view_ids):
        self.email = email + '/token'
        self.subdomain = subdomain
        self.zendesk_api_token = zendesk_api_token
        self.view_ids = view_ids

    def get(self):
        # Get view list for view names
        view_list_url = 'https://{}.zendesk.com/api/v2/views.json'.format(self.subdomain)
        view_list_response = requests.get(view_list_url, auth=(self.email, self.zendesk_api_token))
        view_list_response_json = view_list_response.json()
        # create dict of resquested view names
        view_names_dict = {}
        for view in view_list_response_json['views']:
            if view['id'] in [int(x) for x in view_ids.split(',')]:
                view_names_dict[view['id']] = view['title']

        request_ids = {'ids': self.view_ids}
        view_count_url = 'https://{}.zendesk.com/api/v2/views/count_many.json'.format(self.subdomain)
        # establish time of zendesk request
        time_now = time.strftime('%m-%d-%Y %H:%M', time.localtime())
        view_count_response = requests.get(view_count_url, auth=(self.email, self.zendesk_api_token), params=request_ids)
        view_count_response_json = view_count_response.json()
        # transform data to specification required for google sheets
        view_count_data = []
        for view_count in view_count_response_json['view_counts']:
            if view_count['view_id'] in [int(x) for x in view_ids.split(',')]:
                new_row = [time_now,
                           str(view_count['view_id']),
                           str(view_names_dict[view_count['view_id']]),
                           str(view_count['value'] if view_count['value'] else 0)]
                view_count_data.append(new_row)
        return view_count_data


class AutomatedTracker():
    # initialise ongiong tracker with previously created google sheets and zendesk api access objects
    def __init__(self, google_sheets, zendesk):
        self.google_sheets = google_sheets
        self.zendesk = zendesk

    # Start to track
    def start(self):
        # set etl to repeat in 10 minutes
        threading.Timer(600.0, self.start).start()
        # hit zendesk api endpoint
        zendesk_data = self.zendesk.get()
        # append to google sheet
        self.google_sheets.load(zendesk_data)


def enter_zendesk_details():
    subdomain = input('enter zendesk subdomain with tickets to be tracked :')
    while not subdomain:
        subdomain = input('enter zendesk subdomain with tickets to be tracked :')
    email = input('user email address containing view counts :')
    while not email:
        email = input('user email address containing view counts :')
    zendesk_api_token = input('enter zendesk api token :')
    while not zendesk_api_token:
        zendesk_api_token = input('enter zendesk api token :')
    view_ids = input('enter the view ids to be tracked as a comma serperated list :')
    while not zendesk_api_token:
        view_ids = input('enter the view ids to be tracked as a comma serperated list :')
    return subdomain, email, zendesk_api_token, view_ids

if __name__ == '__main__':

    subdomain, email, zendesk_api_token, view_ids = enter_zendesk_details()
    # enter_zendesk_details()
    # inititalise data
    # obtain google sheets access
    google_interface = GoogleSheets()

# create google sheet
    google_interface.create_spreadsheet()
# get zendesk user input
    zendesk_interface = ExtractZendeskData(email, subdomain, zendesk_api_token, view_ids)
# run automated tracker
    tracker = AutomatedTracker(google_interface, zendesk_interface)

    print('Spreadsheet will be updated every 10 minutes\n')
    tracker.start()
