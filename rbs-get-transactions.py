import requests
import os
import urllib3
import re
import csv
import time
import sys
from tqdm import tqdm

BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Stop complaints about making unverified SSL requests.
urllib3.disable_warnings()

for environment in ['RBS_CLIENT_ID', 'RBS_CLIENT_SECRET']:
    if environment not in os.environ:
        print('Set {0} as an environment variable'.format(environment))
        sys.exit(1)

# Update this configuration to match your environment.
CLIENT_ID = os.environ['RBS_CLIENT_ID']
CLIENT_SECRET = os.environ['RBS_CLIENT_SECRET']
APP_ID = '3a12066f-8853-444e-8e42-24670a35d9e8'
USERNAME = '1234567890|1234567890'
FINANCIAL_ID = '0015800000jfwB4AAI'
RBS_API_URL = 'https://ob.sandbox.rbs.co.uk'
REDIRECT_URI = 'https://{0}.example.org/redirect'.format(APP_ID)

print('Getting access token...')

r = requests.post(RBS_API_URL + '/token',
                  data={
                      'grant_type': 'client_credentials',
                      'client_id': CLIENT_ID,
                      'client_secret': CLIENT_SECRET,
                      'scope': 'accounts',
                  },
                  verify=False)

ACCESS_TOKEN = r.json()['access_token']

print('Getting consent...')

r = requests.post(RBS_API_URL + '/open-banking/v3.1/aisp/account-access-consents',
                  json={
                      'Data': {
                          'Permissions': [
                              "ReadAccountsDetail",
                              "ReadBalances",
                              "ReadTransactionsCredits",
                              "ReadTransactionsDebits",
                              "ReadTransactionsDetail",
                          ],
                      },
                      'Risk': {},
                  },
                  headers={
                      'Authorization': 'Bearer {0}'.format(ACCESS_TOKEN),
                      'x-fapi-financial-id': FINANCIAL_ID,
                  },
                  verify=False)

CONSENT_ID = r.json()['Data']['ConsentId']

r = requests.get(RBS_API_URL + '/authorize',
                 params={
                     'client_id': CLIENT_ID,
                     'response_type': 'code id_token',
                     'scope': 'openid accounts',
                     'redirect_uri': REDIRECT_URI,
                     'request': CONSENT_ID,
                     'authorization_mode': 'AUTO_POSTMAN',
                     'authorization_result': 'APPROVED',
                     'authorization_username': '{0}@{1}.example.org'.format(USERNAME, APP_ID),
                     'authorization_accounts': '*',
                 },
                 verify=False)

AUTHORIZATION_CODE = re.search(r'#code=([^&]*)', r.json()['redirectUri']).group(1)

r = requests.post(RBS_API_URL + '/token',
                  data={
                      'client_id': CLIENT_ID,
                      'client_secret': CLIENT_SECRET,
                      'redirect_uri': REDIRECT_URI,
                      'grant_type': 'authorization_code',
                      'code': AUTHORIZATION_CODE,
                  },
                  verify=False)

RESOURCE_ACCESS_TOKEN = r.json()['access_token']

r = requests.get(RBS_API_URL + '/open-banking/v3.1/aisp/accounts',
                 headers={
                     'Authorization': 'Bearer {0}'.format(RESOURCE_ACCESS_TOKEN),
                     'x-fapi-financial-id': FINANCIAL_ID,
                 },
                 verify=False)

csv_headers = [
    'TransactionId',
    'BookingDateTime',
    'Amount',
    'Currency',
]

start = time.perf_counter()

for account in r.json()['Data']['Account']:
    ACCOUNT_ID = account['AccountId']

    print('Account id {0}'.format(ACCOUNT_ID))

    page = 0
    transactions = []
    progress_bar = None
    csv_file = os.path.join(BASE_PATH, 'output', 'transactions-{0}.csv'.format(ACCOUNT_ID))

    with open(csv_file, 'w', newline='') as fh:
        csv_writer = csv.writer(fh)
        csv_writer.writerow(csv_headers)

        while True:
            r = requests.get(RBS_API_URL + '/open-banking/v3.1/aisp/accounts/{0}/transactions'.format(ACCOUNT_ID),
                             params={
                                 'page': page,
                             },
                             headers={
                                 'Authorization': 'Bearer {0}'.format(RESOURCE_ACCESS_TOKEN),
                                 'x-fapi-financial-id': FINANCIAL_ID,
                             },
                             verify=False)

            for transaction in r.json()['Data']['Transaction']:
                csv_writer.writerow([
                    transaction['TransactionId'],
                    transaction['BookingDateTime'],
                    transaction['Amount']['Amount'],
                    transaction['Amount']['Currency'],
                ])

            page += 1
            total_pages = r.json()['Meta']['TotalPages']

            if not progress_bar:
                progress_bar = tqdm(total=int(total_pages))

            if page >= total_pages:
                progress_bar.update(1)
                progress_bar.close()
                break
            else:
                progress_bar.update(1)

print('Operation took {:,.2f} seconds'.format(time.perf_counter() - start))
