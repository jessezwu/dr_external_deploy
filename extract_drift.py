# Extract drift statistics from an existing deployment

import requests
import datetime

# Authorisation
API_TOKEN = 'get this from your profile in the app'
DEPLOYMENT = 'the id of your deployment'

# List existing deployments
# deployments = requests.get('https://app.datarobot.com/api/v2/modelDeployments/', headers=headers)

# Set request headers
headers = {'Authorization': 'Token %s' % API_TOKEN}

# Query parameters for drift, start is inclusive, end is exclusive, set timestamps accordingly
params = {
    'start': '2019-03-01',
    'end': '2019-04-01',
    'metric': 'kl_divergence'
}

# Get drift
deploy_response = requests.get(
    'https://app.datarobot.com/api/v2/modelDeployments/%s/dataDrift/' % DEPLOYMENT,
    headers = headers,
    params = params
)
deploy_response.raise_for_status()

deploy_response.json()
