import boto3
import json
import logging
import os
from functions import *
from base64 import b64decode
from urlparse import parse_qs
import config, re, create_repo
from slacker import Slacker
import random

kms = boto3.client('kms')
resource = boto3.resource('dynamodb')
client   = boto3.client('dynamodb')
slack = Slacker(config.API_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

functionRepo()
myFunctionRepo = functionRepo()

# Manage creation of the repo
class manageBot:

    # define attribs for all functions
    def __init__(self):
        self.message = ""
        self.table_name = "githubCreateRepo"
        self.table = resource.Table(self.table_name)


    # return the response status
    def getResponse(self, status_code, res):
        return {
            'statusCode': status_code,
            'body': json.dumps(res),
            'headers': {
                'Content-Type': 'application/json',
            },
        }

    # return the body formatted
    def getBody(self, data):
        body = []
        body.append(data)
        return body

    # check parameters
    def checkParam(self, param):
        message = {}
        test = 0

        try:
            data = param.split(" ")
        except KeyError:
            message["status"] = "Parameters have to be separated by space"
            test = 1

        if test == 0:
            if len(data) != 2:
                message["status"] = "exactly 2 parameters are required (Those need to be separated by space): RepoName TeamName\nAvailable teams: `{}` \nExample: /gitrequestrepo nw-watchlist developer \n".format(config.GIT_TEAMS)
                test = 1

        if test == 0:
            if not re.match('^nw-',data[0]):
                message["status"] = "the repository name should start by nw- "
                test = 1

        if test == 0:
            response = self.table.scan()
            if response["Items"]:
                items = response["Items"][0]
                repo = items["data"][0]
                message_id = items["message_id"]
                message["status"] = "Sorry wait until this request gets approved:\n repo=> {}\n message_id=>{} ".format(repo,message_id)
                test = 1


        return message, test, data

    # send SQS message
    def sendDBMessage(self, body_message):
        self.table.put_item(Item=body_message)


    # Generation of messageID for SQS
    def randomGenerator(self, size):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for x in range(size))


def lambda_handler(event, context):
    status_code = 200
    body = message = event_body = {}
    myManageBot = manageBot()
    message["status"] = ""

    status_code, message, event_body = myFunctionRepo.checkBody(event)

    if status_code == 200 and event_body:
        token = event_body['token']

        # Check slack token
        if token != config.EXPECTED_TOKEN:
            message["status"] = "Request token {} does not match expected".format(token)
            return message["status"]
        else:
            user = event_body['user_name']
            command_text = event_body['text']

        # Check the parameters
        message, checkstatus, data  = myManageBot.checkParam(command_text)
        if checkstatus == 0:

            # send information to dynamoDB
            message_id = myManageBot.randomGenerator(size=15)
            myManageBot.sendDBMessage({"message_id":message_id,"slack_user":user,"message_status":"waiting_approval","data":data})

            config.SLACK_APPROVAL.append({"title":"repository creation","text":"requestor=> {}\n repo_name=> {}\n repo_team=> {}\n message_id=> {}".format(user,data[0],data[1],message_id)})
            config.SLACK_APPROVAL.append({"callback_id": "git_repo_`{}`".format(message_id)})
            slack.chat.post_message(config.SLACK_CHANNEL,text="Would you like to approve this request?", attachments=config.SLACK_APPROVAL,username="slackbot")
            message["status"] = "Request submitted for approval for the repo {} ".format(data[0])
            myFunctionRepo.status_message["status"] = "submitted_for_approval"
            myFunctionRepo.status_message["repo"] = data[0]
            myFunctionRepo.logging() # logging event

    body = myManageBot.getBody(message)
    response = myManageBot.getResponse(status_code, body)

    return message["status"]

if __name__ == "__main__":
    event = context = {}
    lambda_handler(event,context)