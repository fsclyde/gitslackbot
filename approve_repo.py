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
from boto3.dynamodb.conditions import Key


kms = boto3.client('kms')
resource = boto3.resource('dynamodb')
client   = boto3.client('dynamodb')
lam   = boto3.client('lambda')
slack = Slacker(config.API_TOKEN)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

functionRepo()
myFunctionRepo = functionRepo()


# Manage Approval
class manageApprove:

    # define attribs for all functions
    def __init__(self):
        self.table_name = "githubCreateRepo"
        self.table = resource.Table(self.table_name)

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
            if len(data) < 3:
                message["status"] = "At least 3 parameters are required (Separated by space): messageId teamsRead teamsWrite\nAvailable teams: `{}` \nExample: /gitapprove SFDjds98kfjskdf readonly,devops Tesla\n".format(config.GIT_TEAMS)
                test = 1

        if test == 0:
            if len(data[0]) != 15:
                message["status"] = "Wrong messaged_id provided"
                test = 1

        return message, test, data

    # Query dynamodb to get information from it
    def getItemFromDynamodb(self,data):
        message = {}
        table_data = requestor = ""

        # Using query With dynamoDB
        response = self.table.query(KeyConditionExpression=Key('message_id').eq(data[0]))
        if response["Items"]:
            table_data = response['Items'][0]["data"]
            requestor = response['Items'][0]["slack_user"]
        else:
            message["status"] = "This message does not match with the one in the DB"

        return requestor, table_data, message


def lambda_handler(event, context):
    status_code = 200
    body = message = event_body = dev_input = {}
    myManageApprove = manageApprove()
    message["status"] = requestor = ""
    status_code, message, event_body = myFunctionRepo.checkBody(event)
    if event_body:
        command_text = event_body['text']
        callback_url = event_body["response_url"]
        approver = event_body["user_name"]
        channel_name = event_body["channel_name"]

        # Check the parameters
        message, checkstatus, data = myManageApprove.checkParam(command_text)

        if checkstatus == 0:
            requestor, dev_input, message = myManageApprove.getItemFromDynamodb(data)

            if dev_input and requestor:
                message["status"] = "The repository {} will be created soon".format(dev_input[0])

                # Add all repository informations
                info_repo = {
                    "repo_name":dev_input[0],
                    "repo_team":dev_input[1],
                    "repo_teams_read":data[1],
                    "repo_teams_write":data[2],
                    "approver":approver,
                    "requestor":requestor,
                    "channel":channel_name,
                    "message_id":data[0]
                }

                # if SSH key declared then add it
                if len(data) == 5:

                    ssh_info = {
                        "ssh_title":data[3],
                        "ssh_key":data[4]
                    }

                    info_repo.update(ssh_info)
                # Call Asynchronous function to create the repo

                lam.invoke(
                    FunctionName='nwGitCreate',
                    InvocationType='Event',
                    LogType='None',
                    Payload=json.dumps(info_repo)
                )

    return message["status"]


if __name__ == "__main__":
    event = context = {}
    lambda_handler(event,context)