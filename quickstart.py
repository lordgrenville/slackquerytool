from __future__ import print_function
import httplib2
import os
import datetime
import pytz

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_id.json'
APPLICATION_NAME = 'Slack Room Query Tool'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Hits up the big or small meeting room and gets its status for the next hour
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    #how soon is now? choosing the current time
    tz = pytz.timezone('Asia/Jerusalem')

    m = tz.localize(datetime.datetime.now())
    timeMin = m.isoformat()
    a = tz.localize(datetime.datetime.now()) + datetime.timedelta(hours=1)
    timeMax = a.isoformat()

    #selecting the room
    room_choice = input('Please write little for the little room, or big for the big room')
    while not room_choice == "little" and not room_choice == "big":
        room_choice = input('Please write little for the little room, or big for the big room')
    if room_choice == 'little':
        room = "positivemobile.co.il_33363633373637353130@resource.calendar.google.com"
    else:
        room = "positivemobile.co.il_3538343631343537313634@resource.calendar.google.com"

    body = {
      "timeMin": timeMin,
      "timeMax": '2017-04-19T18:39:48-08:00',
      "timeZone": 'Asia/Jerusalem',
      "items": [{"id": room}]
    }

    eventsResult = service.freebusy().query(body=body).execute()
    cal_dict = eventsResult[u'calendars']

    for cal_name in cal_dict:
        if cal_dict[cal_name]['busy'] == []:
            print("The room is currently free")
        else:
            end_time = cal_dict[cal_name]['busy'][0]['end'][11:19]
            print ('The %s room is currently busy. It will be free at %s' %(room_choice, end_time))

if __name__ == '__main__':
    main()