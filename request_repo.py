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
sqs = boto3.resource('sqs')
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
        self.sqs_queue = "githubCreateRepo.fifo"

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
            if len(data) != 3:
                message["status"] = "exactly 3 parameters are required: Repo Name, Description, Repo team name"
                test = 1

        if test == 0:
            if not re.match('^nw-',data[0]):
                message["status"] = "the repository name should start by nw- "
                test = 1

        return message, test, data

    # send SQS message
    def sendSQSMessage(self, body_message):

        MessageGroupId = self.randomGenerator(size=10)
        queue = sqs.get_queue_by_name(QueueName=self.sqs_queue)
        response = queue.send_message(MessageBody=json.dumps(body_message),MessageGroupId=MessageGroupId)

        myFunctionRepo.status_message["message_id"] = response.get('MessageId')
        myFunctionRepo.status_message["message_md5_body"] = response.get('MD5OfMessageBody')
        myFunctionRepo.status_message["slack_user"] = body_message["slack_user"]
        try:
            myFunctionRepo.status_message["sqs_status_code"] = response["ResponseMetadata"]["HTTPStatusCode"]
        except KeyError:
            myFunctionRepo.status_message = 500

        return myFunctionRepo.status_message["sqs_status_code"]

    # Generation of messageID for SQS
    def randomGenerator(self, size):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for x in range(size))



def lambda_handler(event, context):
    status_code = 200
    body = message = event_body = {}
    myManageBot = manageBot()

    status_code, message, event_body = myFunctionRepo.checkBody(event)

    if status_code == 200 and event_body:
        token = event_body['token']

        # Check slack token
        if token != config.EXPECTED_TOKEN:
            message["status"] = "Request token {} does not match expected".format(token)
        else:
            user = event_body['user_name']
            command_text = event_body['text']

        # Check the parameters
        message, checkstatus, data  = myManageBot.checkParam(command_text)
        if checkstatus == 0:

            # send information to the SQS queue
            sqs_status_code = myManageBot.sendSQSMessage({"data":data,"slack_user":user,"status":"waiting_approval"})

            # send message to slack channel
            if sqs_status_code == 200:

                config.SLACK_APPROVAL.append({"title":"repository creation","text":"requestor=> {}\n repo_name=> {}\n repo_team=> {}\n message_id=> {}".format(user,data[0],data[2],myFunctionRepo.status_message["message_id"])})
                config.SLACK_APPROVAL.append({"callback_id": "git_repo_`{}`".format(myManageBot.randomGenerator(size=8))})
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