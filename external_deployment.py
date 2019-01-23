import datarobot as dr
import requests
import sys

# API reference is available on the support site
# https://support.datarobot.com/hc/en-us/articles/215067826-Accessing-the-DataRobot-API-documentation

# Credentials
API_TOKEN = 'get this from your profile on the app'

# Set HTTP headers
headers = {'Content-Type': 'application/json', 'Authorization': 'Token %s' % API_TOKEN}

# List existing deployments
# deployments = requests.get('https://app.datarobot.com/api/v2/modelDeployments/', headers=headers)

################################################################################
# Create external deployment

# All of these parameters should correspond to your own dataset
# Note the project id - deployment requires a reference to some project
# This should represent the training data (or initial data if no model)
params = {
    'projectId': '5c33d636083f4d4deb513d8b',
    'modelId': 'external',
    'label': 'External Prediction Test',
    'description': 'Data monitoring test',
    'deploymentType': 'external',
    'predictionColumn': 'predictions',
    'timestampColumn': 'timestamp',
    'actualResponseColumn': 'actuals',
    'problemType': 'classification',
    'minorityClass': '1',
    'majorityClass': '0'
}

# Generate deployment
deploy_response = requests.post(
    'https://app.datarobot.com/api/v2/modelDeployments/asyncCreate/',
    headers = headers,
    json = params
)
deploy_response.raise_for_status()

# Get deployment ID
deployment = requests.get(
    deploy_response.headers['Location'],
    headers = headers
).json()
deployment_id = deployment['id']

# Optionally configure threshold for graphs (in this case to 0.2)
# e.g. if you pass probabilities from predictions instead of 0/1 values
# This call can also be used to configure time granularity (default 1 day)
threshold = requests.patch(
    'https://app.datarobot.com/api/v2/modelDeployments/%s/displaySettings/' % deployment_id,
    headers = headers,
    json = {'targetDrift': {'positiveClassThreshold': 0.2}}
)

################################################################################
# Now that we have a deployment, we want to upload data to this new deployment,
# and start monitoring drift.

# Must first upload data as a project.
# Prefer authentication via yaml config for the datarobot library, otherwise:
# dr.Client(token=API_TOKEN, endpoint='https://app.datarobot.com/api/v2')
project = dr.Project.create(
    'path_to_your_scoring_data.csv',
    project_name = 'External upload'
)

# Use this newly uploaded data in our deployment tracking
# By default this assumes new scoring data, but a once off load of training
# data is also possible
upload_response  = requests.post(
    'https://app.datarobot.com/api/v2/modelDeployments/%s/uploadData/' % deployment_id,
    headers = headers,
    json = {'projectId': project.id}
)

# Optionally delete projects
requests.delete(
    'https://app.datarobot.com/api/v2/projects/%s/' % project.id,
    headers = headers,
)
