#### Settings file ####
import os, boto3
from base64 import b64decode

kms = boto3.client('kms')

# Github parameters
USERNAME = kms.decrypt(CiphertextBlob=b64decode(os.environ["USERNAME"]))['Plaintext']
PASSWORD = kms.decrypt(CiphertextBlob=b64decode(os.environ["PASSWORD"]))['Plaintext']

# GITHUB_API_URL = "http://github.nw.adesa.com/api/v3/{}"
GITHUB_API_URL = "https://api.github.com/{}"
GITHUB_ORGANISATION = "fsbaseorga"

# Slack parameters
SLACK_CHANNEL = "#githubot"
EXPECTED_TOKEN = kms.decrypt(CiphertextBlob=b64decode(os.environ["ENC_EXPECTED_TOKEN"]))['Plaintext']
API_TOKEN = kms.decrypt(CiphertextBlob=b64decode(os.environ["API_TOKEN"]))['Plaintext']

SLACK_APPROVAL = [{
                    "title": "Approve a request using",
                    "text": "/gitapprove [message_id]"
                }]
# SLACK_APPROVAL = [{
#                     "fallback": "You are unable to choose an answer",
#                     "color": "#3AA3E3",
#                     "attachment_type": "default",
#                     "actions": [
#                         {
#                             "name": "repo",
#                             "text": "approve",
#                             "style": "primary",
#                             "type": "button",
#                             "value": "approve"
#                         },
#                         {
#                             "name": "repo",
#                             "text": "reject",
#                             "style": "danger",
#                             "type": "button",
#                             "value": "reject"
#                         }
#                     ]
#                 }]
