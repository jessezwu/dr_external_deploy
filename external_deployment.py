# Create an external deployment using the DataRobot REST API
#
# API reference is available on the support site
# https://support.datarobot.com/hc/en-us/articles/215067826-Accessing-the-DataRobot-API-documentation
#
# Note that you must authenticate to use the datarobot library.
# Prefer authentication via yaml config for the datarobot library, otherwise:
# dr.Client(token=API_TOKEN, endpoint='https://app.datarobot.com/api/v2')

import requests
import datarobot as dr

# Credentials
API_TOKEN = 'get this from your profile on the app'

# Set HTTP headers
headers = {'Content-Type': 'application/json', 'Authorization': 'Token %s' % API_TOKEN}

################################################################################
# To create an external deployment, first upload deployment data as a project.

# Upload scored training data as basis of comparison for drift
project = dr.Project.create(
    'path_to_your_scored_training_data.csv',
    project_name = 'External upload'
)

################################################################################
# Create external deployment
#
# ALL of the bracketed parameters and problem type should correspond to your
# own dataset.
# Also bear in mind that creating a deployment requires a reference to some
# project intended as a training dataset reference.
params = {
    'projectId': project.id,
    'modelId': '<name your external model>',
    'label': '<name your deployment>',
    'description': '<describe your deployment>',
    'deploymentType': 'external',
    'predictionColumn': '<predictions>',
    'timestampColumn': '<timestamp>',
    'actualResponseColumn': '<actuals>',
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
# Check this worked
deploy_response.raise_for_status()
# If an error occurs, deploy_response.content() will often give a useful reason

# Get deployment ID
deployment = requests.get(
    deploy_response.headers['Location'],
    headers = headers
).json()
deployment_id = deployment['id']

################################################################################
# Optionally configure threshold for graphs (in this case to 0.2)
# e.g. if you pass probabilities from predictions instead of 0/1 values
# This call can also be used to configure time granularity (default 1 day)
threshold_response = requests.patch(
    'https://app.datarobot.com/api/v2/modelDeployments/%s/displaySettings/' % deployment_id,
    headers = headers,
    json = {'targetDrift': {'positiveClassThreshold': 0.2}}
)
threshold_response.raise_for_status()

################################################################################
# Now that we have the deployment, we want to upload our project data to this
# new deployment, and start monitoring drift.

# First use previously uploaded training data for the drift baseline
upload_response  = requests.post(
    'https://app.datarobot.com/api/v2/modelDeployments/%s/uploadData/' % deployment_id,
    headers = headers,
    json = {'projectId': project.id, 'dataSourceType': 'training'}
)
upload_response.raise_for_status()
# Optionally delete project
requests.delete(
    'https://app.datarobot.com/api/v2/projects/%s/' % project.id,
    headers = headers,
)

# For future scored data - follow the same process of creating a project
project_new = dr.Project.create(
    'path_to_your_new_data.csv',
    project_name = 'External upload'
)
# But upload as scoring data
upload_response  = requests.post(
    'https://app.datarobot.com/api/v2/modelDeployments/%s/uploadData/' % deployment_id,
    headers = headers,
    json = {'projectId': project_new.id, 'dataSourceType': 'scoring'}
)
upload_response.raise_for_status()
# Optionally delete this project
requests.delete(
    'https://app.datarobot.com/api/v2/projects/%s/' % project_new.id,
    headers = headers,
)
